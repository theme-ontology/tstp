# Copyright 2023, themeontology.org
# Tests:
from django.core.management.base import BaseCommand, CommandError
import totolo.search



class Command(BaseCommand):
    help = 'Search the ontology.'

    def add_arguments(self, parser):
        parser.add_argument('-t', action='store_true', help='search themes')
        parser.add_argument('-s', action='store_true', help='search stories')
        parser.add_argument('-q', '--query', required=True, help='query string')


    def handle(self, *args, **options):
        query = options.get('query', '')
        if not query:
            raise CommandError('Must specify what to search for with -q "..."')
        if options.get('t') and not options.get('s'):
            for theme, weight in totolo.search.themes(query):
                print("{}: {}: {}".format(theme.idx, weight, theme.name))
                #break
        elif options.get('s') and not options.get('t'):
            for story, weight in totolo.search.stories(query):
                print("{}: {}: {}".format(story.idx, weight, story.title))
                #break
        else:
            raise CommandError('Must choose either -t (search themes) or -s (search stories), but not both.')


        self.stdout.write(self.style.SUCCESS('Ran command: {}'.format(__name__)))
        return

