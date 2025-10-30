from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from music_tracker.tracker.models import (
    Album,
    Artist,
    ObsessionList,
    ObsessionSongs,
    SpotifyTop100List,
    SpotifyTop100Songs,
    TopTenAlbumsList,
)


def index(request):
    most_recent_top_ten = TopTenAlbumsList.get_most_recent()

    return redirect("top_ten", year=most_recent_top_ten.year)


def get_navigation_links():
    top_ten_lists = TopTenAlbumsList.get_published().order_by("year")
    obsessions_lists = ObsessionList.get_published().order_by("year")
    spotify_lists = SpotifyTop100List.get_published().order_by("year")

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

    spotify_links = [
        {
            "title": list.title,
            "year": list.year,
        }
        for list in spotify_lists
    ]

    spotify_links.append({"title": "Spotify Top 100 Stats", "year": "stats"})

    return {
        "top_tens": top_ten_links,
        "obsessions": obsession_links,
        # "spotify_top_100": spotify_links,
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


def spotify_top_100_stats(request):
    # Get all published Spotify Top 100 lists ordered by year
    published_lists = SpotifyTop100List.get_published().order_by("year")

    if not published_lists.exists():
        context = {
            "page_title": "Spotify Top 100 Stats",
            "years_data": [],
            "navigation": get_navigation_links(),
        }
        return render(request, "tracker/spotify-top-100-stats.html", context)

    years_data = []
    previous_year_data = {}  # Store artist song counts from the previous year
    all_artists_by_years = {}  # Track which artists appear in which years

    for current_list in published_lists:
        # Get all songs for this year's list
        songs_this_year = (
            SpotifyTop100Songs.objects.filter(top_100_list=current_list)
            .select_related("song")
            .prefetch_related("song__artists")
        )

        # Count songs per artist for this year
        artist_counts = {}
        for song_entry in songs_this_year:
            for artist in song_entry.song.artists.all():
                if artist.id not in artist_counts:
                    artist_counts[artist.id] = {"name": artist.name, "count": 0}
                artist_counts[artist.id]["count"] += 1

                # Track this artist for the years club calculation
                if artist.id not in all_artists_by_years:
                    all_artists_by_years[artist.id] = {
                        "name": artist.name,
                        "years": set(),
                    }
                all_artists_by_years[artist.id]["years"].add(current_list.year)

        # Create the data structure for this year
        year_data = {
            "year": current_list.year,
            "is_first_year": len(years_data) == 0,
            "artists": [],
        }

        # Create artist entries with previous year comparison
        for artist_id, data in artist_counts.items():
            artist_entry = {
                "name": data["name"],
                "id": artist_id,
                "current_count": data["count"],
                "previous_count": previous_year_data.get(artist_id, {}).get("count", 0),
            }

            # Calculate change (only meaningful if not the first year)
            if not year_data["is_first_year"]:
                artist_entry["change"] = (
                    artist_entry["current_count"] - artist_entry["previous_count"]
                )

            year_data["artists"].append(artist_entry)

        # Sort artists by count (descending) then name (ascending)
        year_data["artists"].sort(key=lambda x: (-x["current_count"], x["name"]))

        # Count unique artists for this year
        year_data["total_artists"] = len(artist_counts)

        years_data.append(year_data)

        # Store this year's data for next iteration
        previous_year_data = artist_counts

    # Calculate years groups data
    total_published_lists = len(published_lists)
    years_groups = {}

    for artist_id, artist_data in all_artists_by_years.items():
        num_years = len(artist_data["years"])
        if num_years >= 2:  # Only include artists with 2+ years
            if num_years not in years_groups:
                years_groups[num_years] = []
            years_groups[num_years].append(
                {"name": artist_data["name"], "id": artist_id}
            )

    # Sort artists alphabetically within each group
    for num_years in years_groups:
        years_groups[num_years].sort(key=lambda x: x["name"])

    # Create ordered list of groups (2 years through total years)
    ordered_groups = []
    for num_years in range(2, total_published_lists + 1):
        if num_years in years_groups:
            ordered_groups.append(
                {"num_years": num_years, "artists": years_groups[num_years]}
            )
        else:
            ordered_groups.append({"num_years": num_years, "artists": []})

    context = {
        "page_title": "Spotify Top 100 Stats",
        "years_data": years_data,
        "years_groups": ordered_groups,
        "navigation": get_navigation_links(),
    }

    return render(request, "tracker/spotify-top-100-stats.html", context)
