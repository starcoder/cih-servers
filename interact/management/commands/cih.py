from importlib import reload
import time
import sys
from datetime import datetime
import logging
import gzip
from django.core.management.base import BaseCommand
from django.core.management import call_command
import django.db.migrations
import json
import interact
from interact import models
import os.path
from glob import glob
from interact.visualization import potential_figures
import logging
import shutil
import torch
import pickle
import os
import shutil

logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primary_server.settings')
try:
    from django.core.management import execute_from_command_line
except ImportError as exc:
    raise ImportError(
        "Couldn't import Django. Are you sure it's installed and "
        "available on your PYTHONPATH environment variable? Did you "
        "forget to activate a virtual environment?"
    ) from exc
#execute_from_command_line(sys.argv)


class Command(BaseCommand):
    help = ()
    def add_arguments(self, parser):
        sps = parser.add_subparsers()

        create = sps.add_parser("create_project")
        create.add_argument("--schema_file", dest="schema_file", required=True)
        create.set_defaults(command=self.create_project)

        for upload_type in ["data", "structure", "topic", "liwc", "tsne"]:
            upload = sps.add_parser("upload_{}".format(upload_type))
            upload.add_argument("--{}_file".format(upload_type), dest="{}_file".format(upload_type))
            upload.add_argument("--schema_file", dest="schema_file")
            upload.add_argument("--overwrite", dest="overwrite", default=False, action="store_true")
            upload.set_defaults(command=getattr(self, "upload_{}".format(upload_type))) #.upload_data)

        #upload_model = sps.add_parser("upload_model")
        #upload_model.add_argument("--model_file", dest="model_file")
        #upload_model.add_argument("--schema_file", dest="schema_file")
        #upload_data.add_argument("--overwrite", dest="overwrite", default=False, action="store_true",
        #                    help="When objects already exist, remove them, rather than skipping them.")
        #upload_data.set_defaults(command=self.upload_data)


        #reset = sps.add_parser("reset")
        #reset.set_defaults(command=self.reset)
        #migrate = sps.add_parser("migrate")
        #migrate.set_defaults(command=self.migrate)
        
    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        options["command"](**options)
        # if "experiment_path" in options:
        #     for subpath in glob(os.path.join(options["experiment_path"], "work", "*")):
        #         files = {
        #             "schema_file" : "schema.json",
        #             "output_file" : "output*json.gz",
        #             "data_file" :  "data.json.gz",
        #             "bottlenecks_file" : "tsne*json.gz",
        #             "liwc_file" : "liwc.json.gz", # = os.path.join(subpath, "schema.json")
        #             "topics_file" : "topic_models.json.gz", # = os.path.join(subpath, "schema.json")
        #             "model_file" : "model*pkl.gz", # = glob(os.path.join(subpath, "model*pkl.gz"))
        #         }
        #         files = {k : glob(os.path.join(subpath, v)) for k, v in files.items()}
        #         options["command"](
        #             **files,
        #             **options
        #         )
        # else:
        #     options["command"](**options)
        #     pass
        #options["command"](**options)

    def upload_project(self, schema_file, data_file, liwc_file, topics_file, bottlenecks_file, **args):
        if data_file and schema_file:
            self.upload_data(schema_file[0], data_file[0], **args)
        pass
        
    def reset(self, **args):
        for fname in glob(
                os.path.join(
                    django.db.migrations.state.global_apps.get_app_config("interact").path,
                    "migrations",
                    "*"
                )
        ):
            if os.path.isdir(fname):
                shutil.rmtree(fname)
            elif os.path.basename(fname): # != "__init__.py":
                os.remove(fname)
        execute_from_command_line("manage.py reset_db --noinput -c".split())
        #execute_from_command_line("manage.py makemigrations".split())        
        #execute_from_command_line("manage.py makemigrations interact".split())

    def migrate(self, **args):
        execute_from_command_line("manage.py makemigrations".split())
        execute_from_command_line("manage.py makemigrations interact".split())
        execute_from_command_line("manage.py migrate".split())
        execute_from_command_line("manage.py migrate interact".split())
        
    def create_project(self, schema_file, **args):
        with open(schema_file, "rt") as ifd:
            schema = json.load(ifd)
        name = schema["meta"]["name"]
        logger.info("Creating Project '{}'".format(name))
        interact.models.Project.objects.filter(name=name).delete()
        project = interact.models.Project.objects.create(schema=schema, name=name)
        project.save()
        for entity_type_name in schema["entity_types"].keys():
            logger.info("Creating EntityType '{}'".format(entity_type_name))
            eto = interact.models.EntityType.objects.create(project=project, name=entity_type_name)
            eto.save()                

    # def create_projects(self, experiment_path, **args):

    #     with open(schema_fname, "rt") as ifd:
    #         schema = json.load(ifd)
    #     name = schema["meta"]["name"]
    #     logger.info("Creating Project '{}'".format(name))
    #     interact.models.Project.objects.filter(name=name).delete()
    #     project = interact.models.Project.objects.create(schema=schema, name=name)
    #     project.save()
    #     for entity_type_name in schema["entity_types"].keys():
    #         logger.info("Creating EntityType '{}'".format(entity_type_name))
    #         eto = interact.models.EntityType.objects.create(project=project, name=entity_type_name)
    #         eto.save()                
            
    # def upload_experiments(self, experiment_path, **args):
    #     execute_from_command_line("manage.py migrate".split())
    #     execute_from_command_line("manage.py migrate interact".split())
    #     for subpath in glob(os.path.join(experiment_path, "work", "*")):
    #         schema_fname = os.path.join(subpath, "schema.json")
    #         self.create_project(schema_fname)
    #         #execute_from_command_line("manage.py makemigrations interact".split())
    #         #execute_from_command_line("manage.py migrate interact".split())            
    #         #data_fname = os.path.join(subpath, "data.json.gz")
    #         #self.upload_data(schema_fname, data_fname)
            
        
    # def collect_models(self, *args, **options):
    #     for project_id in PROJECT_IDS:
    #         model_files = glob(os.path.join(STARCODER_EXPERIMENTS_PATH, "work", project_id, "model_*pkl.gz"))
    #         if len(model_files) == 1:
    #             logger.info("Copying model for project '%s'", project_id)
    #             shutil.copyfile(model_files[0], os.path.join("interact", "static", "{}.pkl.gz".format(project_id)))

    def upload_structure(self, schema_file, structure_file, *args, **options):
        with open(schema_file, "rt") as ifd:
            schema = json.loads(ifd.read())
        with gzip.open(structure_file, "rt") as ifd:
            structure = json.loads(ifd.read())
        project_name = schema["meta"]["name"]
        project = models.Project.objects.get(name=project_name)            
        logger.info("Uploading model structure for project '%s'", project_name)
        models.StarcoderModel.objects.filter(project=project).delete()
        m = models.StarcoderModel.objects.create(project=project, structure=structure)
        m.save()
                
    def upload_topic(self, schema_file, topic_file, *args, **options):
        #schema_fname, topic_fname = options["rest"]
        with open(schema_file, "rt") as ifd:
            schema = json.loads(ifd.read())
        project_name = schema["meta"]["name"]
        project = models.Project.objects.get(name=project_name)
        models.TopicModel.objects.filter(project=project).delete()
        logger.info("Uploading topic model for project '%s'", project_name)
        items = []
        items_by_topic = {}
        with gzip.open(topic_file, "rt") as ifd:
            for line in ifd:
                j = json.loads(line)
                items_by_topic[j["topic"]] = items_by_topic.get(j["topic"], [])
                items_by_topic[j["topic"]].append(j)
                #if j["value"] >= 0.005:
                #    items.append(j)
            for topic, terms in items_by_topic.items():
                items += list(reversed(sorted(terms, key=lambda x : x["value"])))[:100]
            m = models.TopicModel(project=project, spec=items)
            m.save()

    def upload_tsne(self, schema_file, tsne_file, *args, **options):
        #schema_fname, tsne_fname = options["rest"]
        with open(schema_file, "rt") as ifd:
            schema = json.loads(ifd.read())
        project_name = schema["meta"]["name"]
        project = models.Project.objects.get(name=project_name)
        models.TSNE.objects.filter(project=project).delete()
        eidf = schema["meta"]["id_field"]
        etf = schema["meta"]["entity_type_field"]
        logger.info("Uploading TSNE for project '%s'", project_name)
        items = []
        with gzip.open(tsne_file, "rt") as ifd:
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
                
    def upload_liwc(self, schema_file, liwc_file, *args, **options):
        #schema_fname, liwc_fname = options["rest"]
        with open(schema_file, "rt") as ifd:
            schema = json.loads(ifd.read())
        project_name = schema["meta"]["name"]
        project = models.Project.objects.get(name=project_name)
        models.LIWC.objects.filter(project=project).delete()
        logger.info("Uploading LIWC for project '%s'", project_name)
        items = []
        with gzip.open(liwc_file, "rt") as ifd:
            for line in ifd:
                j = json.loads(line)
                j["liwc_features"] = {k : v for k, v in j.get("liwc_features", {}).items() if isinstance(v, float) and v > 0.0}
                items.append(j)
        m = models.LIWC(project=project, spec=items)
        m.save()
                
                
    def upload_data(self, schema_file, data_file, **args):
        id_lookup = {}
        #schema_fname, data_fname = options["rest"]
        with open(schema_file, "rt") as ifd:
            schema = json.loads(ifd.read())
        project_name = schema["meta"]["name"]
        project = models.Project.objects.get(name=project_name)
        logger.info("Uploading data for project '{}'".format(project_name))
        relationships = {}
        id_field_name = schema["meta"]["id_field"]
        entity_type_field_name = schema["meta"]["entity_type_field"]
        entity_type_objects = {}
        to_create = {}
        with gzip.open(data_file, "rt") as ifd:
            for i, line in enumerate(list(ifd)[0:50000]):
                jj = json.loads(line)
                if "original" in jj and "reconstruction" in jj:
                    j = jj["original"]
                    rj = jj["reconstruction"]
                else:
                    j = jj
                    rj = None
                entity_type_name = j[entity_type_field_name]
                et = getattr(models, models.make_name(project.id, entity_type_name))
                ret = getattr(models, models.make_name(project.id, "reconstructed^{}".format(entity_type_name)))
                eto = models.EntityType.objects.get(project=project, name=entity_type_name)

                field_values = {
                    "starcoder_id" : j[id_field_name],
                    "id" : i,
                    "entity_type" : eto, #entity_type_objects[j[entity_type_field_name]],
                }
                r_field_values = {
                    "starcoder_id" : j[id_field_name],
                    "id" : i,
                }

                id_lookup[j[id_field_name]] = i
                for k, v in j.items():
                    if k in schema["data_fields"]:
                        if schema["data_fields"][k].get("type") == "date":
                            formats = schema["data_fields"][k].get("format", "%d-%b-%Y")
                            formats = formats if isinstance(formats, list) else [formats]
                            s = v
                            v = None
                            for f in formats:
                                try:
                                    v = datetime.strptime(s, f)
                                    break
                                except:
                                    pass
                        elif schema["data_fields"][k].get("type") == "datetime":
                            formats = schema["data_fields"][k].get("format", "%d-%b-%Y")
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
                    elif k in schema["relationship_fields"]:
                        relationships[et] = relationships.get(et, {})
                        relationships[et][k] = relationships[et].get(k, {})
                        relationships[et][k][j[id_field_name]] = v
                to_create[et] = to_create.get(et, [])
                to_create[et].append(field_values)
                if rj != None:
                    for k, v in rj.items():
                        if k in schema["data_fields"]:
                            if schema["data_fields"][k].get("type") == "date":
                                formats = schema["data_fields"][k].get("format", "%d-%b-%Y")
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
                                r_field_values[k] = v
                        elif k in schema["relationship_fields"]:
                            pass
                    to_create[ret] = to_create.get(ret, [])
                    to_create[ret].append(r_field_values)
        ids = {}
        for et, vv in to_create.items():
            et.objects.all().delete()
            et.objects.bulk_create([et(**v) for v in vv])
            ids[et] = et.objects.values_list("starcoder_id", flat=True)
            for et, rels in relationships.items():
                objs = []
                fields = set()
                for rel, mapping in rels.items():
                    items = []
                    for source, targets in mapping.items():
                        st = schema["relationship_fields"][rel]["source_entity_type"]
                        tt = schema["relationship_fields"][rel]["target_entity_type"]
                        items += [(id_lookup[source], id_lookup[t]) for t in (targets if isinstance(targets, list) else [targets]) if t in id_lookup]
                    try:
                        getattr(et, rel).through.objects.bulk_create(
                            [getattr(et, rel).through(i, s, t) for i, (s, t) in enumerate(items)]
                        )
                    except:
                        pass

