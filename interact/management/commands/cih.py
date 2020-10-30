import sys
from datetime import datetime
import logging
import gzip
from django.core.management.base import BaseCommand
import json
from interact import models
#from primary_server.settings import SCHEMAS, STARCODER_EXPERIMENTS_PATH, PROJECT_IDS
import os.path
from glob import glob
from interact.visualization import potential_figures
import logging
import shutil
import torch
import pickle

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = ()
    def add_arguments(self, parser):
        parser.add_argument(
            dest="command",
            choices=[
                "create_projects",
                "create_visualizations",
                "collect_models",
                "create_tsne",                
                "create_topics",
                "create_liwc",
                "upload_data",
                "upload_models",
            ]
        )

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        getattr(self, options["command"])(*args, **options)
        
    def collect_models(self, *args, **options):
        for project_id in PROJECT_IDS:
            model_files = glob(os.path.join(STARCODER_EXPERIMENTS_PATH, "work", project_id, "model_*pkl.gz"))
            if len(model_files) == 1:
                logger.info("Copying model for project '%s'", project_id)
                shutil.copyfile(model_files[0], os.path.join("interact", "static", "{}.pkl.gz".format(project_id)))

    def upload_models(self, *args, **options):
        import starcoder        
        for project_id in PROJECT_IDS:
            model_files = glob(os.path.join(STARCODER_EXPERIMENTS_PATH, "work", project_id, "model_*pkl.gz"))
            if len(model_files) == 1:
                logger.info("Loading model for project '%s'", project_id)
                state, model_args, schema = torch.load(gzip.open(model_files[0], "rb"))
                model = starcoder.ensemble_model.GraphAutoencoder(
                    schema,
                    model_args.depth,
                    model_args.autoencoder_shapes,
                    reverse_relationships=True
                )
                sys.exit()
                #model.load_state_dict(state)
                #model.eval()
                
    def create_topics(self, *args, **options):
        models.TopicModel.objects.all().delete()
        for project_id in PROJECT_IDS:
            project = models.Project.objects.get(starcoder_id=project_id)
            model_files = glob(os.path.join(STARCODER_EXPERIMENTS_PATH, "work", project_id, "topic_models.json.gz"))
            if len(model_files) == 1:
                logger.info("Creating topic model object for project '%s'", project_id)
                items = []
                with gzip.open(model_files[0], "rt") as ifd:
                    for line in ifd:
                        j = json.loads(line)
                        if j["value"] >= 0.005:
                            items.append(j)
                m = models.TopicModel(project=project, spec=items)
                m.save()
            else:
                logger.info("*Not* creating topic model object for project '%s' because there are %d models", project_id, len(model_files))
                            

    def create_tsne(self, *args, **options):
        models.TSNE.objects.all().delete()
        for project_id in PROJECT_IDS:

            project = models.Project.objects.get(starcoder_id=project_id)
            schema = SCHEMAS[project_id]
            eidf = schema["meta"]["id_field"]
            etf = schema["meta"]["entity_type_field"]
            model_files = glob(os.path.join(STARCODER_EXPERIMENTS_PATH, "work", project_id, "tsne*.json.gz"))
            if len(model_files) == 1:
                logger.info("Creating TSNE object for project '%s'", project_id)
                items = []
                with gzip.open(model_files[0], "rt") as ifd:
                    for line in ifd:                        
                        j = json.loads(line)
                        j["entity_type"] = j["original"][etf]
                        j["id"] = j["original"][eidf]
                        j["label"] = "\n".join(["{}: {}".format(k, v) for k, v in j["original"].items() if k not in [eidf, etf]])
                        del j["original"]
                        del j["bottleneck"]
                        del j["reconstruction"]
                        items.append(j)
                m = models.TSNE(project=project, spec=items)
                m.save()
            else:
                logger.info("*Not* creating TSNE object for project '%s' because there are %d models", project_id, len(model_files))
                
    def create_liwc(self, *args, **options):
        models.LIWC.objects.all().delete()
        for project_id in PROJECT_IDS:
            project = models.Project.objects.get(starcoder_id=project_id)
            model_files = glob(os.path.join(STARCODER_EXPERIMENTS_PATH, "work", project_id, "liwc.json.gz"))
            if len(model_files) == 1:
                logger.info("Creating LIWC object for project '%s'", project_id)
                items = []
                with gzip.open(model_files[0], "rt") as ifd:
                    for line in ifd:
                        j = json.loads(line)
                        j["liwc_features"] = {k : v for k, v in j.get("liwc_features", {}).items() if isinstance(v, float) and v > 0.0}
                        items.append(j)
                m = models.LIWC(project=project, spec=items)
                try:
                    m.save()
                except:
                    pass
            else:
                logger.info("*Not* creating LIWC object for project '%s' because there are %d models", project_id, len(model_files))
                
    def create_projects(self, *args, **options):
        models.Project.objects.all().delete()
        for project_id in PROJECT_IDS: #options["project_ids"]:
            schema = SCHEMAS[project_id]
            project_name = schema["meta"].get("name", project_id)
            project_description = schema["meta"].get("description", "")
            logging.info("Creating project '{}'".format(project_name))
            project = models.Project.objects.create(name=project_name, description=project_description, starcoder_id=project_id)
            project.save()
            sch = models.Schema.objects.create(project=project, schema=schema)
            sch.save()
                
    def upload_data(self, *args, **options):
        id_lookup = {}
        for project_id in PROJECT_IDS: #options["project_ids"]:
            logging.info("Uploading data for project '{}'".format(project_id))
            project = models.Project.objects.get(starcoder_id=project_id)
            relationships = {}
            id_field_name = SCHEMAS[project_id]["meta"]["id_field"]
            entity_type_field_name = SCHEMAS[project_id]["meta"]["entity_type_field"]
            entity_type_objects = {}
            for name in SCHEMAS[project_id]["entity_types"].keys():
                getattr(models, models.make_name(project_id, name)).objects.all().delete()
                getattr(models, models.make_name(project_id, "reconstructed^{}".format(name))).objects.all().delete()
                etos = models.EntityType.objects.filter(project=project, name=name)
                if etos.count() == 0:
                    eto = models.EntityType.objects.create(project=project, name=name)
                    eto.save()
                    entity_type_objects[name] = eto
            fname = glob(os.path.join(STARCODER_EXPERIMENTS_PATH, "work", project_id, "output*.json.gz"))
            if len(fname) == 1:                
                to_create = {}
                with gzip.open(fname[0], "rt") as ifd:
                    for i, line in enumerate(list(ifd)[0:1500]):
                        jj = json.loads(line)
                        j = jj["original"]
                        et = getattr(models, models.make_name(project_id, j[entity_type_field_name]))
                        print(entity_type_objects)
                        field_values = {
                            "starcoder_id" : j[id_field_name],
                            "id" : i,
                            "entity_type" : entity_type_objects[j[entity_type_field_name]],
                        }
                        id_lookup[j[id_field_name]] = i
                        for k, v in j.items():
                            if k in SCHEMAS[project_id]["data_fields"]:
                                if SCHEMAS[project_id]["data_fields"][k].get("type") == "date":
                                    formats = SCHEMAS[project_id]["data_fields"][k].get("format", "%d-%b-%Y")
                                    formats = formats if isinstance(formats, list) else [formats]
                                    s = v
                                    v = None
                                    for f in formats:
                                        try:
                                            v = datetime.strptime(s, f)
                                            break
                                        except:
                                            pass
                                if v != None:
                                    field_values[k] = v
                            elif k in SCHEMAS[project_id]["relationship_fields"]:
                                relationships[et] = relationships.get(et, {})
                                relationships[et][k] = relationships[et].get(k, {})
                                relationships[et][k][j[id_field_name]] = v
                        to_create[et] = to_create.get(et, [])
                        to_create[et].append(field_values)
                        if "reconstruction" in jj:
                            j = jj["reconstruction"]
                            et = getattr(models, models.make_name(project_id, "reconstructed^{}".format(j[entity_type_field_name])))
                            field_values = {"starcoder_id" : j[id_field_name], "id" : i}
                            id_lookup[j[id_field_name]] = i
                            for k, v in j.items():
                                if k in SCHEMAS[project_id]["data_fields"]:
                                    if SCHEMAS[project_id]["data_fields"][k].get("type") == "date":
                                        formats = SCHEMAS[project_id]["data_fields"][k].get("format", "%d-%b-%Y")
                                        formats = formats if isinstance(formats, list) else [formats]
                                        s = v
                                        v = None
                                        for f in formats:
                                            try:
                                                v = datetime.strptime(s, f)
                                                break
                                            except:
                                                pass
                                    if v != None:
                                        field_values[k] = v
                                        
                                elif k in SCHEMAS[project_id]["relationship_fields"]:
                                    relationships[et] = relationships.get(et, {})
                                    relationships[et][k] = relationships[et].get(k, {})
                                    relationships[et][k][j[id_field_name]] = v
                                    #field_values[k] = field_values.get(k, []) + (v if isinstance(v, list) else [v])
                                    #if isinstance(v, list)
                                    #field_values[k].append(v)
                            if "bottleneck" in jj:
                                field_values["_bottleneck"] = jj["bottleneck"]
                            to_create[et] = to_create.get(et, [])
                            to_create[et].append(field_values)
                ids = {}
                for et, vv in to_create.items():
                    #print(et, vv)
                    #sys.exit()
                    try:
                        et.objects.bulk_create([et(**v) for v in vv])
                    except:
                        pass
                    ids[et] = et.objects.values_list("starcoder_id", flat=True)
                for et, rels in relationships.items():
                    objs = []
                    fields = set()
                    for rel, mapping in rels.items():
                        items = []
                        for source, targets in mapping.items():
                            st = SCHEMAS[project_id]["relationship_fields"][rel]["source_entity_type"]
                            tt = SCHEMAS[project_id]["relationship_fields"][rel]["target_entity_type"]
                            #print(source, targets)
                            #items += [{"{}_id".format(st) : id_lookup[source], "{}_id".format(tt) : id_lookup[t]} for t in (targets if isinstance(targets, list) else [targets])]
                            #items = [getattr(et, rel).through(**i) for i in items]
                            items += [(id_lookup[source], id_lookup[t]) for t in (targets if isinstance(targets, list) else [targets]) if t in id_lookup]
                        #print(items[0:100])
                        try:
                            getattr(et, rel).through.objects.bulk_create(
                                [getattr(et, rel).through(i, s, t) for i, (s, t) in enumerate(items)]
                            )
                        except:
                            pass
                    #getattr(et, rel).through(
                    #)
                #for obj in et.objects.all():
                #   for rel, ups in rels.items():
                #       if obj.starcoder_id in ups:
                #           v = ups[obj.starcoder_id]
                #           getattr(obj, rel).set(v if isinstance(v, list) else [v])
                #           fields.add(rel)
                #           objs.append(obj)
                #et.objects.bulk_update(objs, fields)
                #print(k, len(v))
                    #e = et.objects.create(starcoder_id=j[id_field_name], **field_values) if es.count() == 0 else es[0]
                    #e.save()
                    # for k, v in j.items():
                    #     if k in SCHEMAS[project_id]["relationship_fields"]:
                    #         relationships[k] = relationships.get(k, {})
                    #         relationships[k][(
                    #             e,
                    #             getattr(models, models.make_name(project_id, SCHEMAS[project_id]["relationship_fields"][k]["target_entity_type"]))
                    #         )] = relationships[k].get(j[id_field_name], []) + [v]
            # for rel_name, vs in relationships.items():
            #     for (src, tgt_type), tgt_ids in vs.items():
            #         for tgt_id in tgt_ids:
            #             es = tgt_type.objects.filter(starcoder_id=tgt_id)
            #             if es.count() == 1:
            #                 getattr(src, rel_name).add(es[0])
                        #else:
                        #    print(es.count())

