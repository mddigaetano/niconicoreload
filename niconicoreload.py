# -*- coding: utf-8 -*-

import os
import sys
import subprocess

from twitter import Twitter, OAuth

import youtube_dl

from mutagen.mp3 import MP3
from mutagen.id3 import TIT2, TPE1, TALB


class MyLogger(object):
    def debug(self, msg):
        print("DBG: " + msg)

    def warning(self, msg):
        print("WARN: " + msg)

    def error(self, msg):
        print("ERROR: " + msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}


class NicoNicoLoad:

    CHUNK_SIZE = 1024
    NICONICO_BASE_VIDEO_URL = "http://www.nicovideo.jp/watch/"

    corrections = {
        u"1-6 -out of the gravity-": u"1/6 -out of the gravity-",
        u"World - Lampshade": u"World·Lampshade",
        u"Heart \' Palette": u"Heart＊Palette",
        u"Re-flection": u"Re:flection",
        u"\'Hello, Planet": u"*Hello, Planet",
        u"Vaicarious": u"√aicarious",
        u"The Flower of Raison d\'Etre": u"The Flower of Raison d\'Être"
    }

    def __init__(self, username, songs_count, oat, oats, ak, asecret):
        self.username = username
        self.songs_count = songs_count

        self.api = Twitter(auth=OAuth(oat, oats, ak, asecret))

    def videoConverter(self, filename):
        subprocess.run("ffmpeg -i ./Video/\"" + filename + ".mp4\" "
                       "-vn ./Music/\"" + filename + ".mp3\" "
                       ">/dev/null 2>&1",
                       shell=True)

    def tagEditor(self, filename):
        mp3 = MP3("./Music/" + filename + ".mp3")
        if mp3.tags == None:
            mp3.add_tags()
        name = filename.split("] ")
        artists = name[0]
        title = name[1]
        artists = artists[1:] \
            .replace(" feat.", ";") \
            .replace(" &", ";") \
            .replace("'", "*")
        try:
            title = self.corrections[title]
        except KeyError:
            pass

        mp3.tags.add(TIT2(encoding=3, text=title))
        mp3.tags.add(TALB(encoding=3, text=u"Vocaloid"))
        mp3.tags.add(TPE1(encoding=3, text=artists))
        mp3.save(v1=2)

    def tweetParser(self, tweet):
        split = tweet['text'].split(" https")
        if len(split) == 1:
            split = tweet['text'].split(" #sm")
        filename = split[0].replace("&amp;", "&")
        song_id = tweet['entities']['hashtags'][0]['text']
        return filename, song_id

    def start(self):
        tweets = self.api.statuses.user_timeline(screen_name=self.username,
                                                 count=self.songs_count)
        to_download = []
        for tweet in tweets:
            filename, song_id = self.tweetParser(tweet)
            to_download.append(self.NICONICO_BASE_VIDEO_URL + song_id)

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(to_download)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Syntax error: niconicoreload <twitter_username> <song_count> <twitter_tokens_file>")
        exit()

    twitter_username = sys.argv[1]
    song_count = sys.argv[2]
    twitter_tokens_file = sys.argv[3]

    with open(twitter_tokens_file, 'r') as file:
        oat = file.readline()
        oats = file.readline()
        ak = file.readline()
        asecret = file.readline()

    nnl = NicoNicoLoad(twitter_username, song_count, oat, oats, ak, asecret)
    nnl.start()
