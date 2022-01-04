# -*- coding: utf-8 -*-

import os
import sys
import re

import tweepy
from yt_dlp import YoutubeDL

from mutagen import MutagenError
from mutagen.mp3 import MP3
from mutagen.id3 import TIT2, TPE1, TALB


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        print("WARN: " + msg)

    def error(self, msg):
        print(msg)


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

TGREEN =  '\033[32m' # Green Text
TYELLOW = '\033[33m' # Yellow text
TRED = '\033[31m' # Red Text
ENDC = '\033[m' # reset to the defaults

class NicoNicoLoad:
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

        self.regex = re.compile(r'^(\[(.+ feat\. .+)\] (.+)) #([a-z]{2}[0-9]+)')
        self.re_http = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

        self.api = tweepy.Client(bearer_token=twitter_bearer_token)

    def tagEditor(self, filename):
        mp3 = MP3("./Music/" + filename.group(1) + ".mp3")
        if mp3.tags == None:
            mp3.add_tags()
        artists = filename.group(2)
        artists = artists \
            .replace(" feat.", ";") \
            .replace(" &", ";") \
            .replace("'", "*")

        title = filename.group(3)
        try:
            title = self.corrections[title]
        except KeyError:
            pass

        mp3.tags.add(TIT2(encoding=3, text=title))
        mp3.tags.add(TALB(encoding=3, text=u"Vocaloid"))
        mp3.tags.add(TPE1(encoding=3, text=artists))
        mp3.save(v1=2)

    def tweetParser(self, tweet):
        tweet = tweet.replace("&amp;", "&")
        temp = self.re_http.search(tweet)
        url = None
        if temp:
            url = temp.group(0)
            tweet = tweet.replace(url + " ", "")
        match = self.regex.match(tweet)
        return match, url

    def start(self):
        tweets = tweepy.Paginator(
            self.api.get_users_tweets, self.username, max_results=10).flatten(limit=self.songs_count)

        to_download = []
        urls = []
        for tweet in tweets:
            match, url = self.tweetParser(tweet.text)
            if match:
                to_download.append(match)
            elif url:
                urls.append(url)

        for match in to_download:
            if not os.path.isfile("./Music/"+ match.group(1) + ".mp3"):
                ydl_opts['outtmpl'] = "./Music/" + match.group(1) + ".%(ext)s"
                with YoutubeDL(ydl_opts) as ydl:
                    try:
                        ydl.download([self.NICONICO_BASE_VIDEO_URL + match.group(4)])
                        print(match.group(1) + " " + TGREEN + "SUCCESS" + ENDC)
                    except Exception:
                        pass
            else:
                print(match.group(1) + " " + TYELLOW + "SKIP" + ENDC)

        for song in to_download:
            try:
                self.tagEditor(song)
            except MutagenError:
                print(TRED + song.group(1) + " not found!" + ENDC)

        ydl_opts['outtmpl'] = "./Music/%(title)s.%(ext)s"
        with YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download(urls)
            except Exception:
                pass


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
