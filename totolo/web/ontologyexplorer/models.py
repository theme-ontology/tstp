from django.db import models

# Create your models here.


class Story(models.Model):
    idx = models.BigAutoField('idx', primary_key=True, editable=False)
    sid = models.CharField('sid', max_length=255, default="", db_index=True)
    title = models.CharField('Title', max_length=255, default="")
    date = models.CharField('Date', max_length=32, default="")
    parents = models.TextField('Parents', default="")
    children = models.TextField('Children', default="")
    description = models.TextField('Description', default="")
    description_short = models.TextField('Short Description', default="")
    source = models.TextField('source', default="")
    ratings = models.TextField('ratings', default="")

    def __str__(self):
        return self.title


class Theme(models.Model):
    idx = models.BigAutoField('idx', primary_key=True, editable=False)
    name = models.CharField('Name', max_length=255, default="", db_index=True)
    parents = models.TextField('Parents', default="")
    children = models.TextField('Children', default="")
    level = models.IntegerField('level', default=0)
    description = models.TextField('Description', default="")
    description_short = models.TextField('Short Description', default="")
    source = models.TextField('source', default="")

    def __str__(self):
        return self.name


class StoryTheme(models.Model):
    idx = models.BigAutoField('idx', primary_key=True, editable=False)
    sid = models.CharField('sid', max_length=255, default="", db_index=True)
    theme = models.TextField('Theme', default="", db_index=True)
    weight = models.CharField('Weight', max_length=16, default="")
    motivation = models.TextField('Motivation', default="")
    capacity = models.TextField('Capacity', default="")
    notes = models.TextField('Notes', default="")

    def __str__(self):
        return "{} :: {}".format(self.sid, self.theme)


class Statistic(models.Model):
    idx = models.BigAutoField('idx', primary_key=True, editable=False)
    name = models.CharField('name', max_length=32, db_index=True)
    timestamp = models.CharField('timestamp', max_length=32, db_index=True)
    data = models.BinaryField('data', default=b'')

    def __str__(self):
        return self.name


class S3Link(models.Model):
    idx = models.BigAutoField('idx', primary_key=True, editable=False)
    bucket = models.CharField('bucket', max_length=255, db_index=True, default="")
    key = models.CharField('key', max_length=255, db_index=True, default="")
    name = models.CharField('name', max_length=32, default="")
    description = models.TextField('description', default="")
    url = models.TextField('url', default="")

    def __str__(self):
        return self.name


