from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from music_tracker.tracker.models import (
    Album,
    Artist,
    ObsessionList,
    ObsessionSongs,
    SpotifyTop100List,
    TopTenAlbumsList,
)


def index(request):
    most_recent_top_ten = TopTenAlbumsList.get_most_recent()

    return redirect("top_ten", year=most_recent_top_ten.year)


def get_navigation_links():
    top_ten_lists = TopTenAlbumsList.get_published().order_by("year")
    obsessions_lists = ObsessionList.get_published().order_by("year")

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

    top_ten_records = Album.get_top_ten(year)
    honorable_mentions_records = Album.get_honorable_mentions(year)

    context = {
        "list_title": list_record.title,
        "year": list_record.year,
        "top_ten": [
            {
                "album_title": album.title,
                "artists": [artist for artist in album.artists.all().order_by("name")],
                "rank": album.rank,
            }
            for album in top_ten_records
        ],
        "honorable_mentions": [
            {
                "album_title": album.title,
                "artists": [artist for artist in album.artists.all().order_by("name")],
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

    context = {
        "list_title": list_record.title,
        "year": list_record.year,
        "songs": [
            {
                "title": obsession.song.title,
                "artists": [
                    artist for artist in obsession.song.artists.all().order_by("name")
                ],
            }
            for obsession in list_record.get_songs().all()
        ],
        "navigation": get_navigation_links(),
    }

    return render(request, "tracker/obsessions.html", context)


def spotify_top_100_list(request, year):
    list_record = get_object_or_404(SpotifyTop100List, year=year, published=True)

    context = {
        "list_title": list_record.title,
        "year": list_record.year,
        "songs": [
            {
                "title": entry.song.title,
                "artists": [
                    artist for artist in entry.song.artists.all().order_by("name")
                ],
                "ordering": entry.ordering,
            }
            for entry in list_record.get_songs().all()
        ],
        "navigation": get_navigation_links(),
    }

    return render(request, "tracker/top-100.html", context)


def obsessions_stats(request):
    all_songs = ObsessionSongs.get_songs()
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
    artist = get_object_or_404(Artist, id=id)

    # Show a table of which years they have songs on the obsessions list
    obsession_list_songs = artist.get_obsession_list_songs()

    song_count = obsession_list_songs.aggregate(Count("song_id", distinct=True))
    list_count = obsession_list_songs.aggregate(
        Count("obsession_list_id", distinct=True)
    )

    by_year = obsession_list_songs.values("obsession_list_id__year")
    song_count_by_year = by_year.annotate(Count("song_id")).order_by(
        "obsession_list_id__year"
    )

    # Get album ranking for this artist
    album_ranking = artist.get_published_album_ranking()
    ranking_data = None
    if album_ranking:
        ranking_data = {
            "albums": [
                {
                    "title": entry.album.title,
                    "year": entry.album.year,
                    "rank": entry.rank,
                    "notes": entry.notes,
                }
                for entry in album_ranking.get_ranked_albums()
            ]
        }

    context = {
        "artist_name": artist.name,
        "artist_id": artist.id,
        "album_ranking": ranking_data,
        "albums": {
            "charted": [
                {
                    "title": album.title,
                    "year": album.year,
                    "rank": album.rank,
                }
                for album in artist.get_top_ten_albums().all()
            ],
            "honorable_mentions": [
                {
                    "title": album.title,
                    "year": album.year,
                }
                for album in artist.get_honorable_mention_albums().all()
            ],
            "other_albums": [
                {
                    "title": album.title,
                    "year": album.year,
                }
                for album in artist.get_other_albums().all()
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
