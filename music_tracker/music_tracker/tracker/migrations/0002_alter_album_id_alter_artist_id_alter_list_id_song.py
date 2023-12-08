# Generated by Django 5.0 on 2023-12-08 21:17

import uuid

import django.db.models.deletion
from django.db import migrations, models

import music_tracker.tracker.models


class Migration(migrations.Migration):

    dependencies = [
        ("tracker", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="album",
            name="id",
            field=music_tracker.tracker.models.UUIDPKField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="artist",
            name="id",
            field=music_tracker.tracker.models.UUIDPKField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="list",
            name="id",
            field=music_tracker.tracker.models.UUIDPKField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
        migrations.CreateModel(
            name="Song",
            fields=[
                (
                    "id",
                    music_tracker.tracker.models.UUIDPKField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(max_length=250)),
                (
                    "year",
                    music_tracker.tracker.models.YearField(
                        max_length=4,
                        validators=[music_tracker.tracker.models.is_valid_year],
                    ),
                ),
                (
                    "album",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="tracker.album",
                    ),
                ),
                ("artists", models.ManyToManyField(null=True, to="tracker.artist")),
            ],
        ),
    ]