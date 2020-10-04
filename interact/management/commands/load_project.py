from datetime import datetime
import logging

from django.core.management.base import BaseCommand

from interact import models




class Command(BaseCommand):
    help = ()

    def handle(self, *args, **options):
        print(dir(models))
