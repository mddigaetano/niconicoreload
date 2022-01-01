# niconicoreload
Python script that lets you download Videos from NicoNico (thanks to [yt-dlp](https://github.com/yt-dlp/yt-dlp)) and convert them into tagged mp3 files

## About
The script is made of several steps:
1. fetch `SONGS_COUNT` tweets from `TWITTER_USER_ID`'s timeline;
    - to fetch the id from the username, launch `curl "https://api.twitter.com/2/users/by/username/$username" -H "Authorization: Bearer $BEARER_TOKEN"`
1. downloads and converts the video via `yt-dlp`
   - if the song title is not the one you want thanks to OS constraints in naming files, the `corrections` dict corrects it
1. finally, it sets the right mp3 tags, with `Vocaloid` as album entry

Every tweet is written following a specific format:
* `[author 1 & author 2 & ... & final author feat. vocalist 1 & ... & final vocalist] song title http://link.to.song #smXXXXX`
where the http link is optional and the hashtag is the video id.

## Run with Docker
To run the container with docker just copy:
```sh
docker run -it --rm \
     --name niconicontainer \
     --mount type=bind,source=/path/to/desired/folder,target=/app/Music \
     -e TWITTER_USER_ID=<your_twitter_id> \
     -e SONGS_COUNT=<how_many_songs_to_download> \
     -e TWITTER_BEARER_TOKEN=<your_twitter_bearer_token> \
     mddigaetano/niconicoreload
```
alternatively, you can pass the needed arguments as command parameters
```sh
... \
mddigaetano/niconicoreload <your_twitter_id> <how_many_songs_to_download> <your_twitter_bearer_token>
```

where:
* `TWITTER_BEARER_TOKEN`
is the OAUTH2 token the Twitter API needs (the app just needs read-only permissions)

If you want to run it in detached mode just type `-d` instead of `-it`
To change the location of the converted songs edit the `source=` parameters after `--mount`
