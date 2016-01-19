# coding:utf-8
import requests
import bs4
import json

class luoo:
    BASE_URL = "http://www.luoo.net/tag/?p={p}"
    LUOO_URL = "http://www.luoo.net/music/{vol}"
    MP3_URL = "http://luoo-mp3.kssws.ks-cdn.com/low/luoo/radio{vol}/{music}.mp3"


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
                    print(music_name, author, music_url)
                data[vol_number] = {
                    "vol": vol_number,
                    "title": vol.get_text(),
                    "url": vol["href"],
                    "musics": music_data
                }
        file = open("luoo.json", "w")
        file.write(json.dumps(data))






luoo = luoo()
luoo.get_musics()
