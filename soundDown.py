import requests
import json
import mutagen
from bs4 import BeautifulSoup
from clint.textui import progress




class soundDown:

    def __init__(self):

        self.trackID = None

    def download(self,url):

        s =requests.session()
        b = s.get(url,stream=True)
        a, c = self.getTrackInfo()
        filename = c + ".mp3"

        with open(filename, 'wb') as fd:
            total_length = int(b.headers.get('content-length'))#taken from http://stackoverflow.com/a/20943461
            for chunk in progress.bar(b.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1): 
                if chunk:
                    fd.write(chunk)
                    fd.flush()

        filename = [filename,a,c]
        self.addtags(filename)

    def addtags(self,filename):

        try:
            audio = mutagen.EasyID3(filename[0])
        except Exception:
            audio = mutagen.File(filename[0],easy=True)
        finally:
            audio['title'] = filename[2]
            audio['artist'] = filename[1]
            audio.save(filename[0],v1=2)

    def getdownload(self,url):

        s = requests.session()
        self.trackID = self.getTrakeId(url)
        work = "http://api.soundcloud.com/i1/tracks/{0}/streams?client_id=b45b1aa10f1ac2941910a7f0d10f8e28&app_version=8bae64e".format(self.trackID)
        response = s.get(work).text
        j = json.loads(response)
        link = j["http_mp3_128_url"]
        if link is not None:
            self.download(link)
        else:
            raise Exception("test")
     
    def getTrakeId(self,url):

        s = requests.session()
        a = s.get(url).text
        soup = BeautifulSoup(a)
        try:
            names = soup.find("meta", {"property":"twitter:app:url:googleplay"})
            names = names['content']
            names = names.replace("soundcloud://sounds:","")
            trakeid = names

            return trakeid
        except Exception:
            raise BaseException("Not a valid track")

    def getTrackInfo(self):

        s = requests.session()
        link = 'http://api.soundcloud.com/tracks/{0}.json?client_id=b45b1aa10f1ac2941910a7f0d10f8e28'.format(self.trackID)
        response = s.get(link).text

        j = json.loads(response)

        artist = j["user"]["username"]
        title = j["title"]
        return (artist,title)