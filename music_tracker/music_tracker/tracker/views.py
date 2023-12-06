from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from music_tracker.tracker.models import Album, TopTenAlbumsList


def index(request):
    return HttpResponse("Hello world")


def top_ten_list(request, year):
    list_record = get_object_or_404(TopTenAlbumsList, year=year, published=True)

    albums = Album.objects.filter(year=year, rank__isnull=False)
    top_ten_records = albums.filter(rank__lt=11).order_by("rank")
    honorable_mentions_records = albums.filter(rank__gt=10).order_by("rank")

    context = {
        "list_title": list_record.title,
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
    }
    return render(request, "tracker/top-ten-albums.html", context)
