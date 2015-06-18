import requests
import json
import mutagen
import zipfile
import os
from bs4 import BeautifulSoup
from clint.textui import progress
from queue import Queue
from threading import Thread


class soundDown:
    def Zip(self):
        with zipfile.ZipFile("files.zip", "w") as f:
            for file in os.listdir(os.curdir):
                if ".mp3" in file:
                    f.write(file)

    def __download(self, q, url):

        request = requests.session()
        ID = self.__getTrakeId(url)
        fullurl = "http://api.soundcloud.com/i1/tracks/{0}/streams?client_id=b45b1aa10f1ac2941910a7f0d10f8e28&app_version=8bae64e".format(
            ID)
        response = request.get(fullurl).text
        j = json.loads(response)
        link = j["http_mp3_128_url"]
        if link is not None:
            url = link
        else:
            raise Exception("Failed to get download link")

        request = requests.session()

        response = request.get(url, stream=True)

        a, c = self.__getTrackInfo(ID)

        filename = c + ".mp3"

        with open(filename, 'wb') as fd:

            total_length = int(response.headers.get('content-length'))  # taken from http://stackoverflow.com/a/20943461
            for chunk in progress.bar(response.iter_content(chunk_size=1024), expected_size=(total_length / 1024)):
                if chunk:
                    fd.write(chunk)
                    fd.flush()
        filename = [filename, a, c]

        self.__addtags(filename)

        q.task_done()

    def __addtags(self, filename):

        try:
            audio = mutagen.EasyID3(filename[0])
        except Exception:
            audio = mutagen.File(filename[0], easy=True)
        finally:
            audio['title'] = filename[2]
            audio['artist'] = filename[1]
            audio.save(filename[0], v1=2)


    def __getTrakeId(self, url):

        request = requests.session()
        a = request.get(url).text

        soup = BeautifulSoup(a)

        try:
            names = soup.find("meta", {"property": "twitter:app:url:googleplay"})
            names = names['content']
            names = names.replace("soundcloud://sounds:", "")
            ID = names

            return ID

        except Exception:
            raise BaseException("Not a valid track")


    def __getTrackInfo(self, ID):

        request = requests.session()
        link = 'http://api.soundcloud.com/tracks/{0}.json?client_id=b45b1aa10f1ac2941910a7f0d10f8e28'.format(ID)
        response = request.get(link).text

        j = json.loads(response)

        artist = j["user"]["username"]
        title = j["title"]

        return (artist, title)

    def Download(self, url, Zip):

        threads = len(url)
        q = Queue(maxsize=0)

        for i in range(threads):
            worker = Thread(target=self.__download, args=(q, url[i]))
            worker.setDaemon(True)
            worker.start()

        for i in url:
            q.put(i)
            print("Downloading %s" % i)

        q.join()

        if Zip:
            self.Zip()