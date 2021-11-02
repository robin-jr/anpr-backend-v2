# Generated by Django 3.2.6 on 2021-11-01 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rlvd', '0002_auto_20211031_1003'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='licenseplatesrlvd',
            name='object_id',
        ),
        migrations.AlterField(
            model_name='licenseplatesrlvd',
            name='anpr_image',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='licenseplatesrlvd',
            name='cropped_image',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='licenseplatesrlvd',
            name='reviewed',
            field=models.BooleanField(),
        ),
        migrations.AlterField(
            model_name='licenseplatesrlvd',
            name='violations',
            field=models.CharField(max_length=100),
        ),
    ]
