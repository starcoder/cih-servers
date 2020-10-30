import json
import textwrap
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Field
from interact import models
from primary_server.settings import SCHEMAS
from .visualization import figure_types, ProjectGrid, Topics, Bottlenecks, LIWC, SchemaGraph
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
import sys

independent_field_types = {
    #"categorical" : "grid-3x3-gap", "graph-up"
    "categorical" : "bar-chart-line",
    "place" : "globe2",
    "date" : "clock",
}

dependent_field_types = {
    "categorical" : None,
    "scalar" : None,
}

class ProjectListView(ListView):
    template_name = "interact/project_list.html"
    model = models.Project
    context_object_name = "objects"
    def get_queryset(self):
        by_domain = {}
        for project in models.Project.objects.all():
            schema = models.Schema.objects.get(project=project)
            domain = schema.schema["meta"].get("domain", "Unknown")
            by_domain[domain] = by_domain.get(domain, [])
            by_domain[domain].append(project)
        return [(i, a, b) for i, (a, b) in enumerate(sorted(by_domain.items()))]
    
class ProjectDetailView(DetailView):
    template_name = "interact/project_detail.html"
    model = models.Project
    context_object_name = "object"
    def get_context_data(self, object):
        project = object
        schema = models.Schema.objects.get(project=project).schema
        schema = {v : {k : vv if v != "entity_types" else {kk : vvv for kk, vvv in vv.items() if kk != "meta"} for k, vv in schema[v].items() if k != "meta"} for v in ["meta", "entity_types", "data_fields", "relationship_fields"]}
        entity_types = models.EntityType.objects.filter(project=project) #schema["entity_types"].keys()
        topics = models.TopicModel.objects.filter(project=project)
        liwc = models.LIWC.objects.filter(project=project)
        tsne = models.TSNE.objects.filter(project=project)
        fields = []
        for etn, et in schema["entity_types"].items():
            for fn in et.get("data_fields", []):
                ft = schema["data_fields"][fn]["type"]
                if ft in independent_field_types and len([f for f in et["data_fields"] if f != fn and schema["data_fields"][f]["type"] in dependent_field_types]) > 0:
                    fields.append((etn, fn, ft, independent_field_types[ft]))
        del schema["meta"]
        return {
            "project" : project,
            "schema_text" : json.dumps(schema, indent=4),
            "entity_types" : entity_types,
            "topics" : topics,
            "liwc" : liwc,
            "tsne" : tsne,
            "independent_fields" : fields,
        }
    
class EntityListView(ListView):
    template_name = "interact/entity_list.html"
    context_object_name = "objects"
    paginate_by = 20
    def get_queryset(self):
        etid = self.kwargs["entity_type_id"]
        et = models.EntityType.objects.get(id=etid)
        etype = getattr(models, models.make_name(et.project.starcoder_id, et.name))
        self.extra_context = {"project" : et.project, "entity_type" : et}
        return etype.objects.all()

class EntityDetailView(DetailView):
    template_name = "interact/entity_detail.html"
    model = models.Project
    context_object_name = "object"
    def get_object(self, **kwargs):
        entity_id = self.kwargs["pk"]
        entity_type_id = self.kwargs["entity_type_id"]
        entity_type = models.EntityType.objects.get(id=entity_type_id)
        etype = getattr(models, models.make_name(entity_type.project.starcoder_id, entity_type.name))
        return etype.objects.get(id=entity_id)
    def get_context_data(self, object):
        entity_type = models.EntityType.objects.get(id=self.kwargs["entity_type_id"])
        entity = {"normal_fields" : {},
                  "one_to_many" : {},
                  "many_to_one" : {},
                  "many_to_many" : {},
        }
        normal_fields = {}
        relationships = {}
        reverse_relationships = {}
        etype = models.make_name(entity_type.project.starcoder_id, entity_type.name)
        recon = models.starcoder_reconstruction_models[etype].objects.get(starcoder_id=object.starcoder_id)
        print(recon)
        for f in object._meta.get_fields(include_hidden=True):
            name = f.name.rstrip("+")
            if name in ["id", "starcoder_id", "entity_type"]:
                pass
            elif f.is_relation:
                if not f.name.endswith("+"):
                    relationships[f.name] = getattr(object, f.name).select_related()
                elif "ManyToManyRel" in str(f): # HACK!
                    reverse_relationships[f.remote_field.name] = list(
                        f.related_model.objects.filter(
                            **{f.remote_field.name : object.id}
                        )
                    )
            else:
                normal_fields[f.name] = f.value_from_object(object)
        print(reverse_relationships)
        return {
            "project_id" : entity_type.project.id,
            "entity_type" : entity_type,
            "object" : object,
            "entity" : entity,
            "normal_fields" : normal_fields,
            "relationships" : relationships,
            "reverse_relationships" : reverse_relationships,
        }

def figure(request, project_id, entity, field):
    project = models.Project.objects.get(id=project_id)
    return render(request, "interact/figure.html", {"project" : project, "entity" : entity, "independent_field" : field})

starcoder_list_views = {}
for model_name, model_type in models.starcoder_models.items():
    class_name = "{}ListView".format(model_name)
    class_attr = {"model" : model_type, "paginate_by" : 20, "template_name" : "interact/entity_list.html"}
    globals()[class_name] = type(class_name, (ListView,), class_attr)
    starcoder_list_views[model_name] = globals()[class_name]

starcoder_detail_views = {}
for model_name, model_type in models.starcoder_models.items():
    class_name = "{}DetailView".format(model_name)
    class_attr = {"model" : model_type, "template_name" : "interact/entity_detail.html"}
    globals()[class_name] = type(class_name, (DetailView,), class_attr)
    starcoder_detail_views[model_name] = globals()[class_name]
    
class EntityTypeListView(ListView):
    model = models.EntityType
    template_name = "interact/entity_type.html"
    pass

def schema(request, project_id):
    project = models.Project.objects.get(id=project_id)
    return None

# def project(request, project_id):
#     project = models.Project.objects.get(id=project_id)
#     schema = models.Schema.objects.get(project=project).schema
#     entity_types = models.EntityType.objects.filter(project=project) #schema["entity_types"].keys()
#     topics = models.TopicModel.objects.filter(project=project)
#     liwc = models.LIWC.objects.filter(project=project)
#     tsne = models.TSNE.objects.filter(project=project)
#     fields = []
#     for etn, et in schema["entity_types"].items():
#         for fn in et.get("data_fields", []):
#             ft = schema["data_fields"][fn]["type"]
#             if ft in independent_field_types:
#                 fields.append((etn, fn, ft))
#     return render(request, "interact/project_detail.html", {
#         "project" : project,
#         "schema_text" : json.dumps(schema, indent=4),
#         "entity_types" : entity_types,
#         "topics" : topics,
#         "liwc" : liwc,
#         "tsne" : tsne,
#         "independent_fields" : fields,
#     })

# def entity_type(request, project_id, entity_type_id):
#     project = models.Project.objects.get(id=project_id)
#     entity_type_obj = models.EntityType.objects.get(id=entity_type_id)
#     etype = getattr(models, models.make_name(entity_type_obj.project.starcoder_id, entity_type_obj.name))
#     return render(
#         request,
#         "interact/entity_type.html",
#         {
#             "project" : project,
#             "entity_type" : entity_type_obj,
#             "entities" : etype.objects.all()
#         }
#     )

# def entity_list(request, entity_type_id):
#     #project = models.Project.objects.get(id=project_id)
#     entity_type_obj = models.EntityType.objects.get(id=entity_type_id)
#     project = entity_type_obj.project
#     etype = getattr(models, models.make_name(entity_type_obj.project.starcoder_id, entity_type_obj.name))
#     return render(
#         request,
#         "interact/entity_type.html",
#         {
#             "project" : project,
#             "entity_type" : entity_type_obj,
#             "entities" : etype.objects.all()
#         }
#     )

# def entity(request, project_id, entity_type_id, entity_id):
#     project = models.Project.objects.get(id=project_id)    
#     entity_type_obj = models.EntityType.objects.get(id=entity_type_id)
#     ename = models.make_name(entity_type_obj.project.starcoder_id, entity_type_obj.name)
#     etype = getattr(models, ename)
#     entity = etype.objects.get(id=entity_id)
#     form = models.starcoder_forms[ename](instance=entity)
#     return render(
#         request,
#         "interact/entity.html",
#         {
#             "project" : project,
#             "entity_type" : entity_type_obj,
#             "entity" : entity,
#             "form" : form,
#         }
#     )

#class BottleneckListView(ListView):
#    model = models.EntityType
#    template_name = "interact/entity_type.html"

def bottlenecks(request, project_id):
    project = models.Project.objects.get(id=project_id)
    return render(
        request,
        "interact/bottlenecks.html",
        {
            "project" : project
        }
    )

def topics(request, project_id):
    project = models.Project.objects.get(id=project_id)
    return render(
        request,
        "interact/topics.html",
        {
            "project" : project
        }
    )

def liwc(request, project_id):
    project = models.Project.objects.get(id=project_id)    
    return render(
        request,
        "interact/liwc.html",
        {
            "project" : project
        }
    )

def vega(request, project_id, entity, independent_field):
    proj = models.Project.objects.get(id=project_id)
    schema = models.Schema.objects.get(project=proj).schema
    retval = figure_types[schema["data_fields"][independent_field]["type"]](
        project_id,
        schema,
        (entity, independent_field)
    ).json
    print(json.dumps(retval, indent=4))
    print(len(str(retval))/ (1000.0 * 1000.0))
    return JsonResponse(retval)

def vega_topics(request, project_id):
    proj = models.Project.objects.get(id=project_id)
    tm = models.TopicModel.objects.get(project=proj)
    retval = Topics(tm.spec).json
    #print(json.dumps(retval, indent=4))
    return JsonResponse(retval)

def vega_liwc(request, project_id):
    proj = models.Project.objects.get(id=project_id)
    schema = models.Schema.objects.get(project=proj).schema
    l = models.LIWC.objects.get(project=proj).spec
    retval = LIWC(proj.starcoder_id, l, schema, ("", "")).json
    print(json.dumps(retval, indent=4))
    return JsonResponse(retval)

def vega_schema(request, project_id):
    proj = models.Project.objects.get(id=project_id)
    schema = models.Schema.objects.get(project=proj).schema
    retval = SchemaGraph(schema).json
    #print(json.dumps(retval, indent=4))
    return JsonResponse(retval)

def vega_bottlenecks(request, project_id):
    proj = models.Project.objects.get(id=project_id)
    tm = models.TSNE.objects.get(project=proj)
    retval = Bottlenecks(tm.spec).json
    print(json.dumps(retval, indent=4))
    return JsonResponse(retval)
