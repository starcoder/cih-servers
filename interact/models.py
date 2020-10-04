from django.db import models
from django.forms import ModelForm
from starcoder_server.settings import SCHEMAS
import types

def make_name(project_id, entity_type_name):
    return "{}^{}".format(project_id, entity_type_name).replace("_", " ").title().replace(" ", "").replace("^", "_")

class Project(models.Model):
    name = models.CharField(max_length=500, unique=True)
    starcoder_id = models.CharField(max_length=500, unique=True)
    description = models.TextField()
    
class EntityType(models.Model):
    name = models.CharField(max_length=500)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

class Schema(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    schema = models.JSONField(default=dict)

class SchemaForm(ModelForm):
    class Meta:
        model = Schema
        fields = ["schema"]

# class Place(models.Field):
#     description = "A geographic coordinate"

#     def __init__(self, *args, **kwargs):
#         kwargs['max_length'] = 104
#         super().__init__(*args, **kwargs)    pass

#     def deconstruct(self):
#         name, path, args, kwargs = super().deconstruct()
#         del kwargs["max_length"]
#         return name, path, args, kwargs

        
model_mapping = {
    "text" : (models.TextField, {"null" : True}),
    "categorical" : (models.CharField, {"max_length" : 500, "null" : True}),
    "boolean" : (models.CharField, {"max_length" : 500, "null" : True}),
    "distribution" : (models.JSONField, {"null" : True}),    
    "numeric" : (models.FloatField, {"null" : True}),
    "integer" : (models.IntegerField, {"null" : True}),
    "datetime" : (models.DateTimeField, {"null" : True}),
    "date" : (models.DateField, {"null" : True}),
    "place" : (models.JSONField, {"null" : True}),
    "audio" : (models.URLField, {"null" : True}),
    "video" : (models.URLField, {"null" : True}),
    "image" : (models.URLField, {"null" : True}),
}

class TopicModel(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    spec = models.JSONField(null=False)

class TSNE(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    spec = models.JSONField(null=False)
    
class LIWC(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    spec = models.JSONField(null=False)
    
class Visualization(models.Model):
    name = models.CharField(max_length=500)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    spec = models.JSONField(null=False, unique=True)
    def __str__(self):
        return self.name #str(self.spec)

#class TopicModel(models.Model):
#    project = models.ForeignKey(Project, on_delete=models.CASCADE)

#class Topic(models.Model):
#    pass
    
starcoder_models = {}
starcoder_reconstruction_models = {}

for project_id, schema in SCHEMAS.items():
    fields = {}    
    for field_name, field_spec in schema["data_fields"].items():
        class_name = "{}Field".format(make_name(project_id, field_name))
        class_attr = {"__module__" : Project.__module__}
        #print(field_name, field_spec)
        globals()[class_name] = type(class_name, (model_mapping[field_spec["type"]][0],), class_attr)
        fields[field_name] = globals()[class_name]
    id_field_name = schema["meta"]["id_field"]
    entity_type_field_name = schema["meta"]["entity_type_field"]
    id_class_name = "{}Field".format(make_name(project_id, "starcoder_id"))
    id_class_attr = {"__module__" : Project.__module__, "starcoder_name" : id_field_name}
    globals()[id_class_name] = type(id_class_name, (models.CharField,), id_class_attr)
    fields["starcoder_id"] = globals()[id_class_name]
    for entity_type_name, entity_type_spec in schema["entity_types"].items():
        editable_fields = []  
        class_name = make_name(project_id, entity_type_name)
        rclass_name = make_name(project_id, "reconstructed^{}".format(entity_type_name))
        class_attr = {
            "__module__" : Project.__module__,
            "entity_type" : entity_type_name,
        }
        disp = entity_type_spec.get("meta", {}).get("display", "")
        if disp != "":
            class_attr["_display"] = disp
            class_attr["__str__"] = lambda x : x._display.format(x)
        rclass_attr = {"__module__" : Project.__module__, "entity_type" : entity_type_name}
        class_attr["starcoder_id"] = fields["starcoder_id"](unique=True, max_length=500)
        rclass_attr["starcoder_id"] = fields["starcoder_id"](unique=True, max_length=500)
        for field_name in entity_type_spec["data_fields"]:
            class_attr[field_name] = fields[field_name](**model_mapping[schema["data_fields"][field_name]["type"]][1])
            rclass_attr[field_name] = fields[field_name](**model_mapping[schema["data_fields"][field_name]["type"]][1])
            editable_fields.append(field_name)
        for field_name, field_spec in schema["relationship_fields"].items():
            if field_spec["source_entity_type"] == entity_type_name:
                target_entity_name = make_name(project_id, field_spec["target_entity_type"])
                rtarget_entity_name = make_name(project_id, "reconstructed^{}".format(field_spec["target_entity_type"]))
                class_attr[field_name] = models.ManyToManyField("{}".format(target_entity_name), related_name="rev_{}".format(field_name))
                rclass_attr[field_name] = models.ManyToManyField("{}".format(rtarget_entity_name), related_name="rev_{}".format(field_name))
                #editable_fields.append(field_name)

        globals()[class_name] = type(class_name, (models.Model,), class_attr)
        starcoder_models[class_name] = globals()[class_name]
        #starcoder_models.append(globals()[class_name])
        rclass_attr["_bottleneck"] = models.JSONField()
        globals()[rclass_name] = type(rclass_name, (models.Model,), rclass_attr)        
        starcoder_reconstruction_models[rclass_name] = globals()[rclass_name]
        #starcoder_reconstruction_models.append(globals()[rclass_name])
        
starcoder_forms = {}
for class_name, model in starcoder_models.items():
    class Meta:
        model = model
        exclude = []
    starcoder_forms[class_name] = type("{}Form".format(class_name), (ModelForm,), {"Meta" : Meta})
        
