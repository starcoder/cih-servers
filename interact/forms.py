from django.forms import ModelForm
import types
from .models import starcoder_models

starcoder_forms = {}
for class_name, model in starcoder_models.items():
    class Meta:
        model = model
        exclude = ["starcoder_id"]
    starcoder_forms[class_name] = type("{}Form".format(class_name), (ModelForm,), {"Meta" : Meta})
