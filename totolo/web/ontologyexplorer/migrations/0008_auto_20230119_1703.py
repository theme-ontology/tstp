# Generated by Django 3.2.13 on 2023-01-19 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ontologyexplorer', '0007_auto_20230116_2114'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='description_short',
            field=models.TextField(default='', verbose_name='Short Description'),
        ),
        migrations.AddField(
            model_name='theme',
            name='description_short',
            field=models.TextField(default='', verbose_name='Short Description'),
        ),
    ]
