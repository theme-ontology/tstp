from django.db import models
from lib.func import memoize

# Create your models here.

@memoize
def get_ontology():
    import themeontology
    return themeontology.read()


class Theme(models.Model):
    score = models.FloatField('Score')
    name = models.CharField('Name', max_length=255)
    parents = models.TextField('Parents')
    description = models.TextField('Description')

    class Meta:
        ordering = ['score']

    def __str__(self):
        return self.name

    def all(self):
        to = get_ontology()
        for theme in to.themes:
            yield Theme(
                score=1.0,
                name=theme.name,
                parents=', '.join(theme.parents),
                description=theme.description
            )


