import sys
from datetime import datetime
import logging
import gzip
from django.core.management.base import BaseCommand
import json
from interact import models
from primary_server.settings import SCHEMAS, STARCODER_EXPERIMENTS_PATH
import os.path
from glob import glob

PROJECT_IDS = list(SCHEMAS.keys())
# categorical -> choices
to_consider = ["categorical", "boolean", "numeric", "place", "date", "datetime"]

def potential_figures(schema, project_id):
    # numeric, categorical
    #field_buckets = {}
    #for k, v in schema["data_fields"].items():
    #    t = v["type"]
    #    t = "categorical" if t == "boolean" else t
    #    field_buckets[t] = field_buckets.get(t, []) + [k]

    #field_to_entities = {}
    #entity_to_fields = {e : set() for e in schema["entity_types"].keys()}
    #for ek, ev in schema["entity_types"].items():        
    #    for f in ev["data_fields"]:
    # ##       field_to_entities[f] = field_to_entities.get(f, set())
    # #       field_to_entities[f].add(ek)
    # #       entity_to_fields[ek] = entity_to_fields.get(ek, set())
    # #       entity_to_fields[ek].add(f)

    specs = {}
    for entity_type, entity_spec in schema["entity_types"].items():
        fields = entity_spec["data_fields"]
        for field_a, field_b in [(x, y) for x in fields for y in fields]:
            # bprint(field_a)
            field_a_type = schema["data_fields"][field_a]["type"]
            field_b_type = schema["data_fields"][field_b]["type"]
            if field_a != field_b: #  and all([f in to_consider for f in [field_a_type, field_b_type]]):                
                #plot = "{}.{}".format(entity_type, field_a)
                #against = "{}.{}".format(entity_type, field_b)
                #figure_type = "{}-{}".format(field_a_type, field_b_type)
                key = (schema["meta"]["name"], entity_type, field_a, entity_type, field_b)
                specs[key] = {
                    "project" : project_id,
                    "entity_a_type" : entity_type,
                    "field_a" : field_a,
                    "field_a_type" : field_a_type,
                    "entity_b_type" : entity_type,
                    "field_b" : field_b,
                    "field_b_type" : field_b_type,
                    "relationship" : None,
                    "direction" : None,
                }
                
        for field in fields:
            for rel_name, rel_spec in schema["relationship_fields"].items():
                source = rel_spec["source_entity_type"]
                target = rel_spec["target_entity_type"]
                if source == entity_type or target == entity_type:
                    for other_field in schema["entity_types"][target]["data_fields"]:
                        field_a = field                        
                        field_b = other_field
                        field_a_type = schema["data_fields"][field_a]["type"]
                        field_b_type = schema["data_fields"][field_b]["type"]
                        direction = "forward" if source == entity_type else "backward"
                        key = (schema["meta"]["name"], source, field_a, target, field_b, rel_name, direction)
                        #plot = "{}.{}".format(entity_type, field_a)
                        #against = "{}.{}.{}".format(rel_name, entity_type, field_b)
                        #figure_type = "{}-{}".format(field_a_type, field_b_type)
                        specs[key] = {
                            "project" : project_id,
                            "entity_a_type" : source,
                            "field_a" : field_a,
                            "field_a_type" : field_a_type,
                            "entity_b_type" : target,
                            "field_b" : field_b,
                            "field_b_type" : field_b_type,
                            "relationship" : rel_name,
                            "direction" : direction,
                        }
                        
                        #specs.append((schema["meta"]["name"], plot, against, figure_type))
                # elif target == entity_type:
                #     for other_field in schema["entity_types"][source]["data_fields"]:
                #         field_a = other_field                        
                #         field_b = field
                #         field_a_type = schema["data_fields"][field_a]["type"]
                #         field_b_type = schema["data_fields"][field_b]["type"]
                #         #plot = "{}.{}".format(entity_type, field_a)
                #         #against = "{}.{}.{}".format(rel_name, entity_type, field_b)
                #         #figure_type = "{}-{}".format(field_a_type, field_b_type)
                #         #specs.append((schema["meta"]["name"], plot, against, figure_type))
                #         specs.append(
                #             {
                #                 "project_name" : schema["meta"]["name"],
                #                 "entity_a_type" : source,
                #                 "field_a" : field_a,
                #                 "field_a_type" : field_a_type,
                #                 "entity_b_type" : target,
                #                 "field_b" : field_b,
                #                 "field_b_type" : field_b_type,
                #                 "relationship" : rel_name,
                #             }
                #         )
                        
                        #items.add((rel_name, None, "cat-num", j["meta"]["name"], (source, target), (cat, num)))
                #if num in entity_to_fields[source] and cat in entity_to_fields[target]:
                #    items.add((None, "{}".format(rel_name), "cat-num", j["meta"]["name"], (target, source), (cat, num)))

                #for other_field in fields:
                #other_field_type = schema["data_fields"][other_field]["type"]
                #if other_field != field and other_field_type in to_consider:
                #    against = "{}.{}".format(entity_type, field)
    #print(specs) #len(specs))
    return specs

    sys.exit()
    #print(field_buckets)
    items = set()
    for cat in field_buckets.get("categorical", []):
        for num in field_buckets.get("numeric", []):
            if cat != num:
                for etype in set.intersection(field_to_entities.get(cat, set()), field_to_entities.get(num, set())):
                    items.add((None, None, "cat-num", j["meta"]["name"], (etype,), (cat, num)))
                for rel_name, rel_spec in j["relationship_fields"].items():
                    source = rel_spec["source_entity_type"]
                    target = rel_spec["target_entity_type"]
                    if cat in entity_to_fields[source] and num in entity_to_fields[target]:
                        items.add((rel_name, None, "cat-num", j["meta"]["name"], (source, target), (cat, num)))
                    if num in entity_to_fields[source] and cat in entity_to_fields[target]:
                        items.add((None, "{}".format(rel_name), "cat-num", j["meta"]["name"], (target, source), (cat, num)))

                
        for catb in field_buckets.get("categorical", []):
            if cat != catb:
                for etype in set.intersection(field_to_entities.get(cat, set()), field_to_entities.get(catb, set())):
                    items.add((None, None, "cat-cat", j["meta"]["name"], (etype,), (cat, catb)))
                for rel_name, rel_spec in j["relationship_fields"].items():
                    source = rel_spec["source_entity_type"]
                    target = rel_spec["target_entity_type"]
                    if cat in entity_to_fields[source] and catb in entity_to_fields[target]:
                        items.add((rel_name, None, "cat-cat", j["meta"]["name"], (source, target), (cat, catb)))
                    if catb in entity_to_fields[source] and cat in entity_to_fields[target]:
                        items.add((None, "{}".format(rel_name), "cat-cat", j["meta"]["name"], (target, source), (cat, catb)))
    return items


class Command(BaseCommand):
    help = ()
    def add_arguments(self, parser):
        parser.add_argument("--no_data", dest="no_data", default=False, action="store_true")
        #parser.add_argument("--schema_path", dest="schema_path", required=True)
        #parser.add_argument("--project_ids", dest="project_ids", nargs="*", default=[])
   
    def handle(self, *args, **options):
        #from django.db import connection from app.account.models
        #for model in models.starcoder_models + [models.Visualization, models.Schema, models.Project, models.EntityType]:
        #    qs = model.objects.all()
        #    qs._raw_delete(qs.db)
        id_lookup = {}
        #print(dir(models.Schema.objects))
        #sys.exit()
        #assert len(options.get("project_data", [])) % 2 == 0
        #for i in range(len(options["project_data"]) // 2):
        for project_id in PROJECT_IDS: #options["project_ids"]:
            #project_id = options["project_data"][i * 2]



            if options["no_data"] == True:
                models.Visualization.objects.all().delete()
                #print(1001010101)
                sys.exit()
            sys.exit()


            
            schema = SCHEMAS[project_id]
            project_name = schema["meta"].get("name", project_id)
            project_description = schema["meta"].get("description", "")
            print("Loading project '{}'".format(project_name))

            ps = models.Project.objects.filter(name=project_name, starcoder_id=project_id)
            project = models.Project.objects.create(name=project_name, description=project_description, starcoder_id=project_id) if ps.count() == 0 else ps[0]
            project.save()

            #for fwd, rev, tp, _, es, (fA, fB) in potential_figures(schema):
            for spec in potential_figures(schema, project_id).values():
                #via = " via {}".format(fwd) if fwd != None else " via {}".format(rev) if rev != None else ""
                
                #eA = es[0] if len(es) == 1 else es[0]
                #eB = es[0] if len(es) == 1 else es[1]
                #print(spec)
                name = "Plot {entity_a_type}.{field_a} against {entity_b_type}.{field_b}".format(**spec)
                if spec["relationship"] != None:
                    name += " via {} {} links".format(spec["relationship"], spec["direction"])
                v = models.Visualization.objects.create(
                    project=project,
                    name=name,
                    spec=spec,
                    #{
                    #    "plot_type" : tp,
                    #    "field_a" : fA,
                    #    "field_b" : fB,
                    #    "entity_a" : eA,
                    #    "entity_b" : eB,
                    ##    "relationship" : fwd if fwd != None else rev if rev != None else None,
                    # #   "direction" : "forward" if fwd != None else "reverse" if rev != None else None,
                    #    "project" : project.id,
                    #}
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
            #print(dir(models))
            #print(dir(getattr(models, "AffichesAmericaines_Listing").price_for))
            #print(dir(getattr(models, "AffichesAmericaines_Product").rev_price_for))
            #sys.exit()
            #fname = options["project_data"][i * 2 + 1]
            fname = glob(os.path.join(STARCODER_EXPERIMENTS_PATH, "work", project_id, "output*.json.gz"))
            if len(fname) == 1:
                to_create = {}
                with gzip.open(fname[0], "rt") as ifd:
                    for i, line in enumerate(list(ifd)):
                        jj = json.loads(line)
                        j = jj["original"]
                        et = getattr(models, models.make_name(project_id, j[entity_type_field_name]))
                        field_values = {"starcoder_id" : j[id_field_name], "id" : i}
                        #print(field_values)
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
                                    #if v == None:
                                    #    raise Exception(s)
                                if v != None:
                                    field_values[k] = v
                            elif k in SCHEMAS[project_id]["relationship_fields"]:
                                relationships[et] = relationships.get(et, {})
                                relationships[et][k] = relationships[et].get(k, {})
                                relationships[et][k][j[id_field_name]] = v
                                #field_values[k] = field_values.get(k, []) + (v if isinstance(v, list) else [v])
                                #if isinstance(v, list)
                                #field_values[k].append(v)
                        to_create[et] = to_create.get(et, [])
                        to_create[et].append(field_values)
                        if "reconstruction" in jj:
                            j = jj["reconstruction"]
                            et = getattr(models, models.make_name(project_id, "reconstructed^{}".format(j[entity_type_field_name])))
                            field_values = {"starcoder_id" : j[id_field_name], "id" : i}
                            #print(field_values)
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
                                        #raise Exception(s)
                                        
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

