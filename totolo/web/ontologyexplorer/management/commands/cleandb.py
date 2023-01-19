# Copyright 2023, themeontology.org
# Tests:
from django.core.management.base import BaseCommand, CommandError
from ontologyexplorer.models import Story, Theme, StoryTheme


class Command(BaseCommand):
    help = 'Remove all object data in database.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        Story.objects.all().delete()
        Theme.objects.all().delete()
        StoryTheme.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Ran command: {}'.format(__name__)))
        return
