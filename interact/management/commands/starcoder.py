import sys
from datetime import datetime
import logging
import gzip
from django.core.management.base import BaseCommand
import json
from interact import models
from starcoder_server.settings import SCHEMAS, STARCODER_EXPERIMENTS_PATH, PROJECT_IDS
import os.path
from glob import glob
from interact.visualization import potential_figures
import logging
import shutil

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = ()
    def add_arguments(self, parser):
        parser.add_argument(
            dest="command",
            choices=[
                "create_visualizations",
                "create_schemas",
                "collect_models",
                "create_tsne",                
                "create_topics",
                "create_liwc",
                "upload_data",                
            ]
        )

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        getattr(self, options["command"])(*args, **options)
        
    def create_visualizations(self, *args, **options):
        logger.info("Removing existing visualizations")
        models.Visualization.objects.all().delete()
        logger.info("Generating specs")
        to_create = []
        for project in models.Project.objects.all():
            schema = models.Schema.objects.get(project=project).schema
            for spec in potential_figures(schema):
                spec["project"] = project.starcoder_id
                to_create.append(
                    models.Visualization(
                        project=project,
                        spec=spec,
                        id=len(to_create),
                    )
                )
        logger.info("Creating visualizations")                
        models.Visualization.objects.bulk_create(to_create)

    def create_schemas(self, *args, **options):
        pass

    def collect_models(self, *args, **options):
        for project_id in PROJECT_IDS:
            model_files = glob(os.path.join(STARCODER_EXPERIMENTS_PATH, "work", project_id, "model_*pkl.gz"))
            if len(model_files) == 1:
                logger.info("Copying model for project '%s'", project_id)
                shutil.copyfile(model_files[0], os.path.join("interact", "static", "{}.pkl.gz".format(project_id)))

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
                m.save()

    def upload_data(self, *args, **options):
        id_lookup = {}
        for project_id in PROJECT_IDS: #options["project_ids"]:
            schema = SCHEMAS[project_id]
            project_name = schema["meta"].get("name", project_id)
            project_description = schema["meta"].get("description", "")
            print("Loading project '{}'".format(project_name))
            ps = models.Project.objects.filter(name=project_name, starcoder_id=project_id)
            project = models.Project.objects.create(name=project_name, description=project_description, starcoder_id=project_id) if ps.count() == 0 else ps[0]
            project.save()
            for spec in potential_figures(schema, project_id).values():
                name = "Plot {entity_a_type}.{field_a} against {entity_b_type}.{field_b}".format(**spec)
                if spec["relationship"] != None:
                    name += " via {} {} links".format(spec["relationship"], spec["direction"])
                v = models.Visualization.objects.create(
                    project=project,
                    name=name,
                    spec=spec,
                )
                v.save()
            
            ss = models.Schema.objects.filter(project=project)
            so = models.Schema.objects.create(schema=schema, project=project) if ss.count() == 0 else ss[0]
            so.save()

            relationships = {}

            id_field_name = SCHEMAS[project_id]["meta"]["id_field"]
            entity_type_field_name = SCHEMAS[project_id]["meta"]["entity_type_field"]

            for name in SCHEMAS[project_id]["entity_types"].keys():
                etos = models.EntityType.objects.filter(project=project, name=name)
                if etos.count() == 0:
                    eto = models.EntityType.objects.create(project=project, name=name)
                    eto.save()
            fname = glob(os.path.join(STARCODER_EXPERIMENTS_PATH, "work", project_id, "output*.json.gz"))
            if len(fname) == 1:
                to_create = {}
                with gzip.open(fname[0], "rt") as ifd:
                    for i, line in enumerate(list(ifd)):
                        jj = json.loads(line)
                        j = jj["original"]
                        et = getattr(models, models.make_name(project_id, j[entity_type_field_name]))
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
                    et.objects.bulk_create([et(**v) for v in vv])
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
                        getattr(et, rel).through.objects.bulk_create(
                            [getattr(et, rel).through(i, s, t) for i, (s, t) in enumerate(items)]
                        )
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

