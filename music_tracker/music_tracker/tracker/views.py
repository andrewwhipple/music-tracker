from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from music_tracker.tracker.models import (
    Album,
    Artist,
    ObsessionList,
    ObsessionSongs,
    TopTenAlbumsList,
)


def index(request):
    most_recent_top_ten = (
        TopTenAlbumsList.objects.filter(published=True).order_by("-year").first()
    )

    return redirect("top_ten", year=most_recent_top_ten.year)


def get_navigation_links():
    top_ten_lists = TopTenAlbumsList.objects.filter(published=True).order_by("year")
    obsessions_lists = ObsessionList.objects.filter(published=True).order_by("year")

    top_ten_links = [
        {
            "title": list.title,
            "year": list.year,
        }
        for list in top_ten_lists
    ]

    obsession_links = [
        {
            "title": list.title,
            "year": list.year,
        }
        for list in obsessions_lists
    ]

    obsession_links.append({"title": "Obsession Stats", "year": "stats"})

    return {
        "top_tens": top_ten_links,
        "obsessions": obsession_links,
    }


def top_ten_list(request, year):
    list_record = get_object_or_404(TopTenAlbumsList, year=year, published=True)

    albums = Album.objects.filter(year=year, rank__isnull=False)
    top_ten_records = albums.filter(rank__lt=11).order_by("rank")
    honorable_mentions_records = albums.filter(rank__gt=10).order_by("rank")

    context = {
        "list_title": list_record.title,
        "year": list_record.year,
        "top_ten": [
            {
                "album_title": album.title,
                "artist": album.artist,
                "rank": album.rank,
            }
            for album in top_ten_records
        ],
        "honorable_mentions": [
            {
                "album_title": album.title,
                "artist": album.artist,
            }
            for album in honorable_mentions_records
        ],
        "navigation": get_navigation_links(),
    }
    return render(request, "tracker/top-ten-albums.html", context)


def obsessions_list(request, year):
    if year == "stats":
        return obsessions_stats(request)

    list_record = get_object_or_404(ObsessionList, year=year, published=True)

    obsession_songs = ObsessionSongs.objects.filter(
        obsession_list=list_record.id
    ).order_by("ordering")

    context = {
        "list_title": list_record.title,
        "year": list_record.year,
        "songs": [
            {
                "title": obsession.song.title,
                "les_artistes": [
                    artist for artist in obsession.song.artists.all().order_by("name")
                ],
                "artists": ", ".join(
                    [str(a) for a in obsession.song.artists.all().order_by("name")]
                ),
            }
            for obsession in obsession_songs.all()
        ],
        "navigation": get_navigation_links(),
    }

    return render(request, "tracker/obsessions.html", context)


def obsessions_stats(request):
    all_songs = ObsessionSongs.objects.filter(obsession_list__published=True)
    by_artist = all_songs.values("song__artists__name", "song__artists__id")

    song_count = by_artist.annotate(Count("song_id", distinct=True)).order_by(
        "-song_id__count",
        "song__artists__name",
    )
    list_count = by_artist.annotate(Count("obsession_list_id", distinct=True)).order_by(
        "-obsession_list_id__count",
        "song__artists__name",
    )

    context = {
        "page_title": "Obsessions Stats",
        "by_songs": [
            {
                "name": record["song__artists__name"],
                "id": record["song__artists__id"],
                "songs": record["song_id__count"],
            }
            for record in song_count.all()
        ],
        "by_years": [
            {
                "name": record["song__artists__name"],
                "id": record["song__artists__id"],
                "years": record["obsession_list_id__count"],
            }
            for record in list_count.all()
        ],
        "navigation": get_navigation_links(),
    }

    return render(request, "tracker/obsessions-stats.html", context)


def artist_stats(request, id):
    artist_record = get_object_or_404(Artist, id=id)

    # Show a table of each top ten year and whether they have albums in the list or honorable mentions
    albums = Album.objects.filter(artist=artist_record.id, listened=True)
    published_top_tens = list(
        TopTenAlbumsList.objects.filter(published=True).values_list("year", flat=True)
    )

    charted = albums.filter(rank__lt=11, year__in=published_top_tens).order_by(
        "year", "rank"
    )
    honorable_mentions = albums.filter(
        rank__isnull=False, rank__gt=10, year__in=published_top_tens
    ).order_by("year", "rank")
    other_albums = albums.filter(
        rank__isnull=True, year__in=published_top_tens
    ).order_by("year", "title")

    # Show a table of which years they have songs on the obsessions list
    obsession_list_songs = ObsessionSongs.objects.filter(
        obsession_list_id__published=True, song__artists=artist_record.id
    ).order_by()

    song_count = obsession_list_songs.aggregate(Count("song_id", distinct=True))
    list_count = obsession_list_songs.aggregate(
        Count("obsession_list_id", distinct=True)
    )

    by_year = obsession_list_songs.values("obsession_list_id__year")
    song_count_by_year = by_year.annotate(Count("song_id")).order_by(
        "obsession_list_id__year"
    )

    context = {
        "artist_name": artist_record.name,
        "artist_id": artist_record.id,
        "albums": {
            "charted": [
                {
                    "title": album.title,
                    "year": album.year,
                    "rank": album.rank,
                }
                for album in charted.all()
            ],
            "honorable_mentions": [
                {
                    "title": album.title,
                    "year": album.year,
                }
                for album in honorable_mentions.all()
            ],
            "other_albums": [
                {
                    "title": album.title,
                    "year": album.year,
                }
                for album in other_albums
            ],
        },
        "obsessions": {
            "song_count": song_count["song_id__count"],
            "list_count": list_count["obsession_list_id__count"],
            "lists": [
                {
                    "year": obsession_list["obsession_list_id__year"],
                    "song_count": obsession_list["song_id__count"],
                }
                for obsession_list in song_count_by_year
            ],
        },
        "navigation": get_navigation_links(),
    }

    return render(request, "tracker/artist-stats.html", context)
