# Generated by Django 5.0 on 2023-12-08 22:49

import django.db.models.deletion
from django.db import migrations, models

import music_tracker.tracker.models


class Migration(migrations.Migration):

    dependencies = [
        ("tracker", "0003_obsessionlist_obsessionsongs"),
    ]

    operations = [
        migrations.AlterField(
            model_name="song",
            name="album",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="tracker.album",
            ),
        ),
        migrations.AlterField(
            model_name="song",
            name="artists",
            field=models.ManyToManyField(
                blank=True, default=None, null=True, to="tracker.artist"
            ),
        ),
        migrations.AlterField(
            model_name="song",
            name="year",
            field=music_tracker.tracker.models.YearField(
                blank=True,
                default=None,
                max_length=4,
                null=True,
                validators=[music_tracker.tracker.models.is_valid_year],
            ),
        ),
    ]
