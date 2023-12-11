# Music Tracker

A very simple li'l Django application for managing various music-related year-end-lists I like to make. This is primarily a replacement for a bunch of spreadsheets and notes scattered across Airtable, Google Sheets, and Apple Notes for the past near-decade, but also an excuse to learn a bit more about how to use Django!

You can see it running live at [https://music-tracking.andrewwhipple.com](https://music-tracking.andrewwhipple.com). It's just deployed on a simple Digital Ocean droplet with a SQLite db and running behind nginx.

<img width="1629" alt="Screenshot 2023-12-11 at 4 36 56 PM" src="https://github.com/andrewwhipple/music-tracker/assets/80973139/25efac28-de48-4049-afe7-8f2c35fb13fe">

## How it works

The app is a fairly simple Django application that leverages the built-in Django admin tool as its CMS and calculates various year-end-lists and year-end stats dynamically. 

As an example, I can create a bunch of `Album` records through the year and mark down if I've listened to them, give them rating, link them to `Artists`, etc. Then at the end of the year, if I give my favorites a `rank` from 1-20 and create a simple `TopTenAlbumsList` record, the app will automatically render a "Top Albums Of [whatever year]" list based off that data. 

## Supported Lists

Right now this supports two types of lists:

* Top Ten Albums Of The Year: ranking my 10 favorite albums (plus up to 10 honorable mentions that didn't make the cut)
* Annual Obsessions: a running list of songs (that may or may not be from this given year) that I was "obsessed" with at some point during the year

As well as some rudimentary stats showing which artists have the most songs on the annual obsession lists and show up on the most lists over the years. 

## Next Lists

Next up I want to replicate:

* A complicated spreadsheet that tracks my Spotify Top 100 songs over time
* A complicated spreadsheet that tracks my definitive ranking of Taylor Swift songs over time
* More stats, such as artist pages that calculate their stats across all these various lists, or visualizations for some of the data
