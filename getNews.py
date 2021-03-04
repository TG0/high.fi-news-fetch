import os
import sys
from platform import python_version
import requests as req
import json
import html
from time import sleep
import codecs

from HTML_template import *


LIST_SKIPPED_NEWS    = True  # | False  List the skipped news in the end of the .html page
PAGE_COUNT_RETRIEVED = 4     # retrieve this many high.fi pages of news titles, can be overriden with -c=<count>
RETRIEVE_INTERVAL_S  = 0.57  # retrieve each page with this intervals
NEWS_UNDER_TIME      = 10    # put max. this many titles before showing time line
OPEN_WITH_BROWSER    = False # Open the result file after fetching the news. -o sets this to True. By def. is asked if opened.


HIGHLIGHT_STAR_ICON  = """<i class="fa fa-star" id="star" aria-hidden="true"></i>"""


HELP_TEXT = """

Ohjelma noutaa uutisotsikoita high.fi -sivulta ja tallettaa ne tiedotoon results.html, joka voidaan avata internetselaimella.

Usage: python getNews.py [-c=<haettu sivumäärä>] [-o]

Oletuksena ohjelma hakee 4 sivua uutisia ja käyttäjältä kysytään, haluaako hän avata tulostiedoston selaimella.

Example: python getNews.py -c=3

Example: python getNews.py -c=3 -o     // avaa myös tulostiedoston selaimella


Configuration:
--------------

Ao. asetustiedostoille käy kokonaisen sanan lisäksi myös osa sanasta, kunhan tämä löytyy uutisotsikosta tai median nimestä.
Esim: 'moottor' suodattaa: 'moottorit', 'moottoreja', 'moottoripyörä', 'moottoriajoneuvo', jne.

avoid_media.txt     - määritä mediat, joiden uutiset oletuksena ohitetaan
avoid_words.txt     - määritä sanat* joita havaitessa otsikossa, uutinen ohitetaan (jollei ole jo ed. säännöllä ohitettu)

exception_words.txt - määritä sanat* joita otsikosta löydettäessä uutista ei ohiteta, 2 edellisestä säännöstä huolimatta
exception_media.txt - määritä mediat joiden uutisia ei koskaan ohiteta, edellisistä säännöistä huolimatta

 * Huom: jos määrität tiedostoon sanan 'seat', ohjelma hakee kuitenkin ' seat' (välilyönnillä edessä). 
   Ts. sana ' useat' ei jää filtteriin kiinni. Sen sijaan ' Seat-autoilija' jää. 
   Jos otsikko kuitenkin alkaa sanalla, välilyöntiä edessä ei käytetä. Esim: 'Seat ei ole auto' suodattuu pois.

highlighted_media.txt - määritä ne mediat, joiden otsikkojen eteen laitetaan tähti korostukseksi
highlighted_words.txt - määritä ne sanat, joiden löytyessä otsikosta, otsikon eteen laitetaan tähti korostukseksi


Tulostiedoston ulkoasun voi muuttaa muokkaamalla css-tyylitiedostoa style.css

"""


URL = "https://high.fi/uutiset/%d/json"

RESULT_FILE          = "results.html"
RESULT_FILE_BY_MEDIA = "results_by_media.html"

CSS_STYLE  = ""  # content of style.css read here
  
TITLE = 0
LINK  = 1
TIME  = 2
AUTH  = 3 
SKIP  = 4 

lstHighlightMedia = ""
lstHighlightWord  = ""


def getCSS():
    """
    get style.css lines for 
    the result html file
    """
    global CSS_STYLE

    if not os.path.isfile("style.css"):
        print("\n*** HUOM!! ***  Tiedostoa style.css ei löytynyt, tulostiedosto näyttää kököltä :(\n")
        CSS_STYLE = "<!-- style.css puuttuu hakemistosta -->"
    else:
      fp = open("style.css")
      CSS_STYLE = fp.read()
      fp.close()


def fileLinesToList(fileName):
    """
    Read each line in file to list returned
    Skip lines with leght < 3 and those
    which start with '#'
    """
    _tmp = []

    for line in codecs.open(fileName, "r", encoding="utf-8"):
        if line.startswith("#") or line.startswith("  ") or len(line) < 4:  # line is: '#' -> len=3
            continue
        _tmp.append(line.lower().strip())
    return _tmp


def readHighLightedMedia():
    global lstHighlightMedia
    global lstHighlightWord

    lstHighlightMedia = fileLinesToList("highlighted_media.txt")
    lstHighlightWord  = fileLinesToList("highlighted_words.txt")


def replace(_in):
    """
    replace e.g. ö with &#228;
    etc.
    """
    return _in.encode('ascii', 'xmlcharrefreplace').decode("utf-8") 


def corrTime(_time):
    """
    Add 2 hours to time:
    09:12 -> 11:12
    """
    hour, min = _time.split(":")
    iHour = int(hour)

    if iHour == 22:
      iHour = -2 
    elif iHour == 23:
      iHour = -1

    return str(iHour + 2) + ":" + min


def fetchNewsJSON():
    """
    Fetch news titles with links from hihg.fi
    as JSON data.
    """
    lstNews = []
    lstSkippedNews = []

    lstAvoidMedia  = fileLinesToList("avoid_media.txt")
    lstExceptMedia = fileLinesToList("exception_media.txt")
    lstAvoidWords  = fileLinesToList("avoid_words.txt")
    lstExceptWords = fileLinesToList("exception_words.txt")


    for i in range(PAGE_COUNT_RETRIEVED):

        dicNews = json.loads(req.get(URL % (i + 1)).text)

        skipReason = ""

        for dicItem in dicNews["responseData"]["feed"]["entries"]:

            skip = False

            for media in lstAvoidMedia:
                if dicItem["author"].lower().find(media) > -1:
                    skip = True
                    skipReason = media
                    break

            if not skip:
                for text in lstAvoidWords:
                    if dicItem["title"].lower().find(" " + text) > -1 or \
                       dicItem["title"].lower().startswith(text):
                        skip = True
                        skipReason = text
                        break

            if skip:
                for text in lstExceptWords:
                    if dicItem["title"].lower().find(" " + text) > -1 or \
                       dicItem["title"].lower().startswith(text):
                        skip = False
                        skipReason = text
                        break

            if skip:
                for media in lstExceptMedia:
                    if dicItem["author"].lower().find(media) > -1:
                        skip = False
                        skipReason = media
                        break
                    
            if skip:
                lstSkippedNews.append((replace(dicItem["title"]), 
                                       dicItem["link"], 
                                       dicItem["publishedDate"],
                                       replace(dicItem["author"]),
                                       skipReason))
                continue
            else:
                lstNews.append((replace(dicItem["title"]), 
                                dicItem["link"], 
                                dicItem["publishedDate"],
                                replace(dicItem["author"]) ))
        
        print(" - %d. haettu" % (i + 1))

        if not PAGE_COUNT_RETRIEVED == (i + 1):
            sleep(RETRIEVE_INTERVAL_S)

    return lstNews, lstSkippedNews


def getHighLight(_media, _title):
    """
    Put a start in front of the title to resuts
    if the media is listed in highlighted_media.txt
    or title contains a word listed in highlighted_words.txt
    """
    global lstHighlightMedia
    global lstHighlightWord
    
    highLight = False

    for media in lstHighlightMedia:
        if _media.lower().find(media) > -1:
            highLight = True

    for txt in lstHighlightWord:
        if _title.lower().find(txt) > -1:
            highLight = True

    return HIGHLIGHT_STAR_ICON if highLight else ""


def writeNewsToHtmlFile(_in):
    """
    Write collected and filtered news 
    items to html result file.
    """
    global CSS_STYLE

    lstNews, lstSkippedNews = _in

    fp = open(RESULT_FILE, "w")

    content = ""

    for i, tupItem in enumerate(lstNews):

        hl = getHighLight(tupItem[AUTH], tupItem[TITLE])

        content += hl + """<a href="%s">%s &nbsp; </a><span id="dimmer">%s</span><br>\n""" % (tupItem[LINK], 
                                                                                              tupItem[TITLE], 
                                                                                              tupItem[AUTH])

        time = ":".join(tupItem[TIME].split()[-2].split(":")[:2])         # 'March, 01 2021 12:10:15 +0000' => '12:10'
        content += "<h2 class=\"subtitleTime\"> &#126;%s</h2><br>" % corrTime(time) if i % NEWS_UNDER_TIME == 0 else ""


    if LIST_SKIPPED_NEWS:

        content += "<br><hr><br><h2 class=\"subtitleTime\">Ohitetut uutiset:</h2><br></br>\n"

        for i, tupItem in enumerate(lstSkippedNews):

            hl = getHighLight(tupItem[AUTH], tupItem[TITLE])

            content += hl + """<a href="%s">%s &nbsp;</a> <span id="dimmer">%s &nbsp; \
                               Syy: '%s'</span><br>\n""" % (tupItem[LINK],
                                                            tupItem[TITLE],
                                                            tupItem[AUTH],
                                                            replace(tupItem[SKIP]))
    fp.write(TEMPL_PAGE.substitute(link="results_by_media.html", 
                                   linktitle="N&auml;yt&auml; medioittain",
                                   extraspace="<br>",
                                   content=content,
                                   style=CSS_STYLE))
    fp.close()



def writeNewsToHtmlFileByMedia(_in):
    """
    Write collected and filtered news 
    items to html result file listed under 
    the medias found.
    """
    global CSS_STYLE

    lstNews, lstSkippedNews = _in

    fp = open(RESULT_FILE_BY_MEDIA, "w")

    content = ""
    dicNewsByMedia = {}


    for tupItem in lstNews:

        if tupItem[AUTH] not in dicNewsByMedia:
            dicNewsByMedia[tupItem[AUTH]] = [list(tupItem)]

        else:
            dicNewsByMedia[tupItem[AUTH]].append(list(tupItem))



    for media in sorted(dicNewsByMedia.keys()):

        content += "<br><h2 class=\"subtitleAuthor\">%s</h2><br>" % media

        for title, link, time, auth in dicNewsByMedia[media]:

            hl = getHighLight(auth, title)

            _time = ":".join(time.split()[-2].split(":")[:2])

            content += hl + """<a href="%s">%s &nbsp;</a><span id="dimmer">%s</span><br>\n""" % (link, 
                                                                                                  title, 
                                                                                                  corrTime(_time))

    if LIST_SKIPPED_NEWS:

        content += "<br><hr><br><h2 class=\"subtitleAuthor\">Ohitetut uutiset:</h2><br></br>\n"

        for i, tupItem in enumerate(lstSkippedNews):

            hl = getHighLight(tupItem[AUTH], tupItem[TITLE])

            content += hl + """<a href="%s">%s &nbsp;</a> <span id="dimmer">%s &nbsp; \
                               Syy: '%s'</span><br>\n""" % (tupItem[LINK],
                                                            tupItem[TITLE],
                                                            tupItem[AUTH],
                                                            replace(tupItem[SKIP]))
    fp.write(TEMPL_PAGE.substitute(link="results.html", 
                                   linktitle="N&auml;yt&auml; aikaj&auml;rjestyksess&auml;",
                                   extraspace="",
                                   content=content,
                                   style=CSS_STYLE))
    fp.close()



def askIfOpenedWithBrowser():
    """
    Ask the user if the result file
    is opened with the program associated with .html
    """
    global OPEN_WITH_BROWSER

    if not OPEN_WITH_BROWSER:
      if input("Avataanko html-tulostiedosto oletusohjelmalla? k/e: ").lower() in ("y", "k"):
          os.startfile(RESULT_FILE)
    else:
        os.startfile(RESULT_FILE)


def verifyPython3():
    """
    make sure the user does not try to run
    this script with python2
    """
    if python_version().startswith("2"):
        print("\n\n *** Ohjelma ei toimi Pythonin versiolla 2. Asenna Python3: https://python.org ***\n")
        sys.exit(1)


def parseCLIArgs():
    """
    See what command arguments are given
    for this script
    """
    global PAGE_COUNT_RETRIEVED
    global OPEN_WITH_BROWSER

    for arg in sys.argv:
        
        if arg.find("-h") > -1:
            print(HELP_TEXT)
            sys.exit(0)

        if arg.find("-c=") > -1:
            PAGE_COUNT_RETRIEVED = int(arg.split("=")[1])

        if arg.find("-o") > -1:
            OPEN_WITH_BROWSER = True



def main():
    """
    Main program
    """
    verifyPython3()

    parseCLIArgs()

    readHighLightedMedia()

    getCSS()

    print("\nHaetaan %d sivullista uutisia...\n" % PAGE_COUNT_RETRIEVED)

    data = fetchNewsJSON()

    writeNewsToHtmlFile(data)

    writeNewsToHtmlFileByMedia(data)

    print("\nValmis!\n")

    askIfOpenedWithBrowser()

    sys.exit(0)


if __name__ == '__main__':
  main()
