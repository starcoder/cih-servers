import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from interact import models
from starcoder_server.settings import SCHEMAS
from .visualization import figure_types, ProjectGrid, Topics, Bottlenecks, LIWC

def visualization(request, project_id, visualization_id):
    project = models.Project.objects.get(id=project_id)
    visualization = models.Visualization.objects.get(id=visualization_id)
    #print(visualization.spec)
    return render(request, "interact/visualization.html", {"project" : project, "visualization" : visualization})

def index(request):
    projects = models.Project.objects.all()
    return render(request, "interact/index.html", {"projects" : projects})

def project(request, project_id):
    project = models.Project.objects.get(id=project_id)
    schema = models.Schema.objects.get(project=project)
    entity_types = models.EntityType.objects.filter(project=project) #schema["entity_types"].keys()
    #topic_model = models.TopicModel.objects.get(project=project)
    #tsne = models.TSNE.objects.get(project=project)
    #liwc = models.LIWC.objects.get(project=project)
    #print(topic_model.count(), tsne.count(), liwc.count())
    #visualizations = models.Visualization.objects.filter(project=project)
    #vis_lookup = {}
    #for v in visualizations:
    #    vis_lookup[(v.spec["field_a"], v.spec["field_b"])] = v
    #print(vis_lookup)
    #schema_form = models.SchemaForm(instance=schema)
    return render(request, "interact/project.html", {
        "project" : project,
        "schema_text" : json.dumps(schema.schema, indent=4),
        "entity_types" : entity_types,
        #"tsne" : tsne,
        #"topic_model" : topic_model,
        #"liwc" : liwc,
        #"visualizations" : visualizations,
    })

def entity_type(request, project_id, entity_type_id):
    project = models.Project.objects.get(id=project_id)
    entity_type_obj = models.EntityType.objects.get(id=entity_type_id)
    etype = getattr(models, models.make_name(entity_type_obj.project.starcoder_id, entity_type_obj.name))
    return render(
        request,
        "interact/entity_type.html",
        {
            "project" : project,
            "entity_type" : entity_type_obj,
            "entities" : etype.objects.all()
        }
    )

def entity(request, project_id, entity_type_id, entity_id):
    project = models.Project.objects.get(id=project_id)    
    entity_type_obj = models.EntityType.objects.get(id=entity_type_id)
    ename = models.make_name(entity_type_obj.project.starcoder_id, entity_type_obj.name)
    etype = getattr(models, ename)
    entity = etype.objects.get(id=entity_id)
    form = models.starcoder_forms[ename](instance=entity)
    return render(
        request,
        "interact/entity.html",
        {
            "project" : project,
            "entity_type" : entity_type_obj,
            "entity" : entity,
            "form" : form,
        }
    )

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

def vega(request, project_id, visualization_id):
    vis = models.Visualization.objects.get(id=visualization_id).spec
    proj = models.Project.objects.get(id=project_id)
    plot_type = (vis["independent_field"]["field_type"], vis["dependent_fields"]["field_type"])
    spec = figure_types[plot_type](vis).json
    #print(json.dumps(spec, indent=4))
    return JsonResponse(spec)

def vega_grid(request, project_id):
    items = []
    for v in models.Visualization.objects.filter(project=project_id):
        item = v.spec
        item["url"] = "/{}/visualization/{}".format(project_id, v.id)
        items.append(item)
    retval = ProjectGrid(items).json
    #print(json.dumps(retval, indent=4))
    return JsonResponse(retval)

def vega_topics(request, project_id):
    proj = models.Project.objects.get(id=project_id)
    tm = models.TopicModel.objects.get(project=proj)
    retval = Topics(tm.spec).json
    print(json.dumps(retval, indent=4))
    return JsonResponse(retval)

def vega_liwc(request, project_id):
    proj = models.Project.objects.get(id=project_id)
    l = models.LIWC.objects.get(project=proj)
    retval = LIWC(l.spec).json
    print(json.dumps(retval, indent=4))
    return JsonResponse(retval)


def vega_bottlenecks(request, project_id):
    proj = models.Project.objects.get(id=project_id)
    tm = models.TSNE.objects.get(project=proj)
    retval = Bottlenecks(tm.spec).json
    print(json.dumps(retval, indent=4))
    return JsonResponse(retval)


#     values = []
#     for v in vis:
#         s = v.spec
#         #plot = "{entity_a_type}.{field_a}".format(**s)
#         #against = "{entity_b_type}.{field_b}".format(**s)
#         plot = "{field_a}".format(**s)
#         against = "{field_b}".format(**s)
#         #if s["relationship"] != None:
#         #    against = "{}.{}".format(s["relationship"], against) if s["direction"] == "forward" else "{}.{}".format(against, s["relationship"])
#         values.append(
#             {
#                 "field_a" : plot.replace(".", "\n"),
#                 "field_b" : against.replace(".", "\n"),
#                 "plot_type" : "{field_a_type}.{field_b_type}".format(**s),
#                 "url" : "/{}/visualization/{}".format(project_id, v.id)
#             }
#         )
#     spec = figure_types["project_grid"](values).json
# #    print(json.dumps(spec, indent=4))
#     return JsonResponse(spec)
