from django.shortcuts import get_object_or_404, redirect, render

from music_tracker.tracker.models import (
    Album,
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

    return {
        "top_tens": [
            {
                "title": list.title,
                "year": list.year,
            }
            for list in top_ten_lists
        ],
        "obsessions": [
            {
                "title": list.title,
                "year": list.year,
            }
            for list in obsessions_lists
        ],
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
                "artists": ", ".join(
                    [str(a) for a in obsession.song.artists.all().order_by("name")]
                ),
            }
            for obsession in obsession_songs.all()
        ],
        "navigation": get_navigation_links(),
    }

    return render(request, "tracker/obsessions.html", context)
