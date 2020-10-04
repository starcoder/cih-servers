from django.contrib import admin
from .models import starcoder_models

for class_name, model in starcoder_models.items():
    admin.site.register(model)

