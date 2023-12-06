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


class YearField(models.CharField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["max_length"] = 4
        kwargs["validators"] = [is_valid_year]
        super().__init__(*args, **kwargs)


class Artist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=250)

    def __str__(self) -> str:
        return self.name


class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
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
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        return self.title


class List(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=250)
    published = models.BooleanField(default=False)


class TopTenAlbumsList(List):
    year = YearField(unique=True)


# class Song(UUIDPrimaryKeyMixin, models.Model):
#    title = models.CharField(max_length=250)
#    year = models.CharField(max_length=4, validators=[is_valid_year])
#    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True)
#    artists = models.ManyToManyField(Artist, null=True)
