# Generated by Django 5.0 on 2023-12-18 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tracker", "0004_alter_song_album_alter_song_artists_alter_song_year"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="album",
            unique_together={("rank", "year")},
        ),
        migrations.AddField(
            model_name="album",
            name="artists",
            field=models.ManyToManyField(
                blank=True, default=None, null=True, to="tracker.artist"
            ),
        ),
        migrations.RemoveField(
            model_name="album",
            name="artist",
        ),
    ]
