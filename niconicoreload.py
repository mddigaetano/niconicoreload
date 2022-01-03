# -*- coding: utf-8 -*-

import os
import sys

import tweepy
from yt_dlp import YoutubeDL

from mutagen.mp3 import MP3
from mutagen.id3 import TIT2, TPE1, TALB


class MyLogger(object):
    def debug(self, msg):
        pass

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
    NICONICO_BASE_VIDEO_URL = "https://www.nicovideo.jp/watch/"

    corrections = {
        u"1-6 -out of the gravity-": u"1/6 -out of the gravity-",
        u"World - Lampshade": u"World·Lampshade",
        u"Heart \' Palette": u"Heart＊Palette",
        u"Re-flection": u"Re:flection",
        u"\'Hello, Planet": u"*Hello, Planet",
        u"Vaicarious": u"√aicarious",
        u"The Flower of Raison d\'Etre": u"The Flower of Raison d\'Être"
    }

    def __init__(self, twitter_user_id, songs_count, twitter_bearer_token):
        self.username = twitter_user_id
        self.songs_count = songs_count
        self.api = tweepy.Client(bearer_token=twitter_bearer_token)

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
        splitted = tweet.split(" #sm")
        filename = splitted[0].split(" https")[0]
        filename = filename.replace("&amp;", "&")
        song_id = ""
        try:
            song_id = "sm" + splitted[1].split(' ')[0]
        except:
            print(tweet)
        return filename, song_id

    def start(self):
        tweets = tweepy.Paginator(
            self.api.get_users_tweets, self.username, max_results=10).flatten(limit=self.songs_count)

        to_download = []
        for tweet in tweets:
            filename, song_id = self.tweetParser(tweet.text)
            if song_id != '':
                to_download.append({"name": filename, "url": self.NICONICO_BASE_VIDEO_URL + song_id})

        for song in to_download:
            if not os.path.isfile("./Music/"+song['name'] + ".mp3"):
                ydl_opts['outtmpl'] = "./Music/" + song['name'] + ".%(ext)s"
                with YoutubeDL(ydl_opts) as ydl:
                    try:
                        ydl.download([song['url']])
                        print(song['name'] + " successfully downloaded")
                    except Exception:
                        pass
            else:
                print(song['name'] + " already downloaded")
        for song in to_download:
            self.tagEditor(song['name'])


if __name__ == "__main__":
    if len(sys.argv) < 4:
        twitter_user_id = os.environ['TWITTER_USER_ID']
        songs_count = int(os.environ['SONGS_COUNT'])
        twitter_bearer_token = os.environ['TWITTER_BEARER_TOKEN']
    else:
        twitter_user_id = sys.argv[1]
        songs_count = int(sys.argv[2])
        twitter_bearer_token = sys.argv[3]

    if twitter_user_id == "" or songs_count == "" or twitter_bearer_token == "":
        print("Syntax error: python niconicoreload.py <twitter_user_id> <songs_count> <twitter_bearer_token>")
        exit()

    nnl = NicoNicoLoad(twitter_user_id, songs_count, twitter_bearer_token)
    nnl.start()
