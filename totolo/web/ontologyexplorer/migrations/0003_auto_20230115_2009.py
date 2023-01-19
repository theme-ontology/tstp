# Generated by Django 3.2.13 on 2023-01-15 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ontologyexplorer', '0002_auto_20230114_2110'),
    ]

    operations = [
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('parents', models.TextField(default='', verbose_name='Parents')),
                ('children', models.TextField(default='', verbose_name='Children')),
                ('description', models.TextField(default='', verbose_name='Description')),
                ('source', models.TextField(default='', verbose_name='source')),
                ('ratings', models.TextField(default='', verbose_name='ratings')),
            ],
        ),
        migrations.AddField(
            model_name='theme',
            name='source',
            field=models.TextField(default='', verbose_name='source'),
        ),
    ]
