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

    def get_albums(self, **kwargs):
        return Album.objects.filter(artists=self.id, **kwargs)

    def get_listed_albums(self):
        published_top_tens = list(
            TopTenAlbumsList.get_published().values_list("year", flat=True)
        )
        albums = self.get_albums(listened=True)
        return albums.filter(year__in=published_top_tens).order_by("year", "rank")

    def get_top_ten_albums(self):
        return self.get_listed_albums().filter(rank__lt=11)

    def get_honorable_mention_albums(self):
        return self.get_listed_albums().filter(rank__gt=10, rank__isnull=False)

    def get_other_albums(self):
        return self.get_listed_albums().filter(rank__isnull=True)

    def get_obsession_list_songs(self):
        return ObsessionSongs.get_songs().filter(song__artists=self.id)

    def get_published_album_ranking(self):
        try:
            return (
                self.artistalbumranking if self.artistalbumranking.published else None
            )
        except ArtistAlbumRanking.DoesNotExist:
            return None


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

    @classmethod
    def get_ranked_albums(cls, year):
        return cls.objects.filter(year=year, rank__isnull=False)

    @classmethod
    def get_top_ten(cls, year):
        return cls.get_ranked_albums(year).filter(rank__lt=11).order_by("rank")

    @classmethod
    def get_honorable_mentions(cls, year):
        return cls.get_ranked_albums(year).filter(rank__gt=10).order_by("rank")

    class Meta:
        unique_together = [("rank", "year")]


class List(models.Model):
    id = UUIDPKField()
    title = models.CharField(max_length=250)
    published = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title

    @classmethod
    def get_published(cls):
        return cls.objects.filter(published=True)


class TopTenAlbumsList(List):
    year = YearField(unique=True)

    @classmethod
    def get_most_recent(cls):
        return cls.get_published().order_by("-year").first()


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

    def get_songs(self):
        return ObsessionSongs.objects.filter(obsession_list=self.id).order_by(
            "ordering"
        )


class ObsessionSongs(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    obsession_list = models.ForeignKey(ObsessionList, on_delete=models.CASCADE)
    ordering = models.IntegerField()

    @classmethod
    def get_songs(cls):
        return cls.objects.filter(obsession_list__published=True)

    class Meta:
        unique_together = [("ordering", "obsession_list"), ("song", "obsession_list")]


class SpotifyTop100List(List):
    year = YearField(unique=True)

    def get_songs(self):
        return SpotifyTop100Songs.objects.filter(top_100_list=self.id).order_by(
            "ordering"
        )


class SpotifyTop100Songs(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    top_100_list = models.ForeignKey(SpotifyTop100List, on_delete=models.CASCADE)
    ordering = models.IntegerField()

    @classmethod
    def get_songs(cls):
        return cls.objects.filter(top_100_list__published=True)

    class Meta:
        unique_together = [("ordering", "top_100_list"), ("song", "top_100_list")]


class ArtistAlbumRanking(models.Model):
    id = UUIDPKField()
    artist = models.OneToOneField(Artist, on_delete=models.CASCADE)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.artist.name} - Album Ranking"

    def get_ranked_albums(self):
        return ArtistAlbumRankingEntry.objects.filter(ranking=self).order_by("rank")


class ArtistAlbumRankingEntry(models.Model):
    id = UUIDPKField()
    ranking = models.ForeignKey(ArtistAlbumRanking, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    rank = models.IntegerField()
    notes = models.TextField(
        blank=True, null=True, help_text="Optional notes about this album's ranking"
    )

    def __str__(self) -> str:
        return f"#{self.rank} - {self.album.title}"

    class Meta:
        unique_together = [("ranking", "rank"), ("ranking", "album")]
