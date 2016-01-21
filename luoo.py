# coding:utf-8
import requests
import bs4
import json
import argparse
import os
import sys
from gevent import monkey; monkey.patch_socket()
import gevent
import logging


class luoo:
    BASE_URL = "http://www.luoo.net/tag/?p={p}"
    LUOO_URL = "http://www.luoo.net/music/{vol}"
    MP3_URL = "http://luoo-mp3.kssws.ks-cdn.com/low/luoo/radio{vol}/{music}.mp3"
    MUSIC_NAME = "{name}.mp3"

    def __init__(self):
        logging.basicConfig(filename="gap.log", level=logging.WARNING)


    def get_musics(self):
        response = requests.get("http://www.luoo.net/music/")
        pages = bs4.BeautifulSoup(response.content, "lxml").find_all("a", class_="page")
        page_num = pages[-1].get_text()
        data = {}
        music_data = {}
        for page in range(1, int(page_num) + 1):
            sub_response = requests.get(self.BASE_URL.format(p=page))
            vols = bs4.BeautifulSoup(sub_response.content, "lxml").find_all("a", class_="name")
            for vol in vols:
                musics_page = requests.get(vol["href"])
                musics = bs4.BeautifulSoup(musics_page.content, "lxml")
                vol_number = musics.find("span", class_="vol-number").get_text()
                music_detail = musics.find_all("a", class_="trackname")
                for music in music_detail:
                    author = music.find_next_sibling("span").get_text()
                    music_name = music.get_text()
                    music_number = int(music_name.split('.')[0])
                    music_url = self.MP3_URL.format(vol=vol_number, music=music_number)
                    if music_number not in music_data.keys():
                        music_data[music_number] = {}
                    music_data[music_number] = {
                        'name': music_name,
                        'author': author,
                        'mp3': music_url
                    }
                data[vol_number] = {
                    "vol": vol_number,
                    "title": vol.get_text(),
                    "url": vol["href"],
                    "musics": music_data
                }
        file = open("luoo.json", "w")
        file.write(json.dumps(data))
        file.close()



    def get_song_list(self, v):
        r = requests.get(self.LUOO_URL.format(vol=v))
        r.encoding = "utf-8"
        res = bs4.BeautifulSoup(r.content, "html.parser")
        vol_num = res.find("span", class_="vol-number").get_text()
        vol_title = res.find("span", class_="vol-title").get_text()
        mp3_dir = 'd:\\music\\' + vol_num + '. ' + vol_title
        musics = res.find_all("a", class_="trackname")
        if not os.path.exists(mp3_dir):
            os.makedirs(mp3_dir)
            os.chdir(mp3_dir)
        else:
            os.chdir(mp3_dir)
        print(u"正在下载第{v_num}期. {v_title}".format(v_num=vol_num, v_title=vol_title))
        for music in musics:
            author = music.find_next_sibling("span",class_="artist").get_text()
            music_name = music.get_text()
            music_num = music_name.split(".")[0]
            mp3_url = self.MP3_URL.format(vol=v, music=music_num)
            r = requests.get(mp3_url, stream=True)
            try:
                if r.status_code == 404:
                    mp3_url = self.MP3_URL.format(vol=v, music=int(music_num))
                    r = requests.get(mp3_url, stream=True)
            except e:
                logging.warning("error: {}".format(music_name))
                continue
            print(u"正在下载: {} --- {}".format(music_name, r.status_code))
            r.encoding = "utf-8"
            with open(self.MUSIC_NAME.format(name=music_num), "wb") as fd:
                fd.write(r.content)
                fd.close()
        os.chdir("../")




luoo = luoo()
parser = argparse.ArgumentParser()
parser.add_argument("-vol", type=int, nargs='+')
parser.add_argument("-m", type=int, nargs='+')
args = parser.parse_args()
if args.vol is not None and len(args.vol) == 1:
    for i in xrange(33,788):
        gevent.spawn(luoo.get_song_list(i)).join()

elif args.m is not None and len(args.vol) == 1:
    pass

# luoo.get_musics()
