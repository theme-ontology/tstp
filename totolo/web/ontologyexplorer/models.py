from django.db import models

# Create your models here.


class Story(models.Model):
    idx = models.IntegerField('idx', primary_key=True)
    sid = models.CharField('sid', max_length=255, default="", db_index=True)
    title = models.CharField('Title', max_length=255, default="")
    date = models.CharField('Date', max_length=32, default="")
    parents = models.TextField('Parents', default="")
    children = models.TextField('Children', default="")
    description = models.TextField('Description', default="")
    source = models.TextField('source', default="")
    ratings = models.TextField('ratings', default="")

    def __str__(self):
        return self.title


class Theme(models.Model):
    idx = models.IntegerField('idx', primary_key=True)
    name = models.CharField('Name', max_length=255, default="", db_index=True)
    parents = models.TextField('Parents', default="")
    children = models.TextField('Children', default="")
    description = models.TextField('Description', default="")
    source = models.TextField('source', default="")

    def __str__(self):
        return self.name


class StoryTheme(models.Model):
    idx = models.IntegerField('idx', primary_key=True)
    sid = models.CharField('sid', max_length=255, default="", db_index=True)
    theme = models.TextField('Theme', default="", db_index=True)
    weight = models.CharField('Weight', max_length=16, default="")
    motivation = models.TextField('Motivation', default="")
    capacity = models.TextField('Capacity', default="")
    notes = models.TextField('Notes', default="")

    def __str__(self):
        return self.theme
