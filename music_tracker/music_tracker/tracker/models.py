from typing import Any
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models


# Create your models here.
def is_valid_year(input):
    try:
        if int(input) > 2100 or int(input) < 1900:
            raise ValidationError(f"{input} is not a valid year")
    except ValueError:
        raise ValidationError(f"{input} is not a valid year")


class UUIDPKField(models.UUIDField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["primary_key"] = True
        kwargs["default"] = uuid4
        kwargs["editable"] = False
        super().__init__(*args, **kwargs)


class YearField(models.CharField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["max_length"] = 4
        kwargs["validators"] = [is_valid_year]
        super().__init__(*args, **kwargs)


class Artist(models.Model):
    id = UUIDPKField()
    name = models.CharField(max_length=250)

    def __str__(self) -> str:
        return self.name


class Album(models.Model):
    id = UUIDPKField()
    title = models.CharField(max_length=250)
    year = YearField()
    release_date = models.DateField(null=True, blank=True)
    listened = models.BooleanField(default=False)
    priority = models.BooleanField(default=False)
    original_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 4)], null=True, default=None, blank=True
    )
    re_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 4)], null=True, default=None, blank=True
    )
    rank = models.IntegerField(
        choices=[(i, i) for i in range(1, 21)], null=True, default=None, blank=True
    )
    artists = models.ManyToManyField(Artist, null=True, blank=True, default=None)

    def __str__(self) -> str:
        return self.title

    def display_artists(self):
        return ", ".join([str(a) for a in self.artists.all()])

    class Meta:
        unique_together = [("rank", "year")]


class List(models.Model):
    id = UUIDPKField()
    title = models.CharField(max_length=250)
    published = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title


class TopTenAlbumsList(List):
    year = YearField(unique=True)


class Song(models.Model):
    id = UUIDPKField()
    title = models.CharField(max_length=250)
    year = YearField(null=True, blank=True, default=None)
    album = models.ForeignKey(
        Album, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )
    artists = models.ManyToManyField(Artist, null=True, blank=True, default=None)

    def __str__(self) -> str:
        return self.title

    def display_artists(self):
        return ", ".join([str(a) for a in self.artists.all()])


class ObsessionList(List):
    year = YearField(unique=True)


class ObsessionSongs(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    obsession_list = models.ForeignKey(ObsessionList, on_delete=models.CASCADE)
    ordering = models.IntegerField()

    class Meta:
        unique_together = [("ordering", "obsession_list"), ("song", "obsession_list")]
