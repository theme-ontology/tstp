# Copyright 2023, themeontology.org
# Tests:
from django.core.management.base import BaseCommand, CommandError
import ontologyexplorer.models as oms


class Command(BaseCommand):
    help = 'Remove all object data in database.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        oms.Story.objects.all().delete()
        oms.Theme.objects.all().delete()
        oms.StoryTheme.objects.all().delete()
        oms.Statistic.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Ran command: {}'.format(__name__)))
        return
