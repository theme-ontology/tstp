# Generated by Django 3.2.13 on 2023-01-24 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ontologyexplorer', '0010_auto_20230123_1823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statistic',
            name='idx',
            field=models.BigAutoField(editable=False, primary_key=True, serialize=False, verbose_name='idx'),
        ),
        migrations.AlterField(
            model_name='story',
            name='idx',
            field=models.BigAutoField(editable=False, primary_key=True, serialize=False, verbose_name='idx'),
        ),
        migrations.AlterField(
            model_name='storytheme',
            name='idx',
            field=models.BigAutoField(editable=False, primary_key=True, serialize=False, verbose_name='idx'),
        ),
        migrations.AlterField(
            model_name='theme',
            name='idx',
            field=models.BigAutoField(editable=False, primary_key=True, serialize=False, verbose_name='idx'),
        ),
    ]
