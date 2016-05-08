from gensim.summarization import summarize,keywords
from pyquery import PyQuery as pq
from unidecode import unidecode
from pymongo import MongoClient
from lxml import etree
import unicodedata
import xmltodict
import urllib2
import json

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


url = "http://rss.elmundo.es/rss/"
d = pq(url = url)
links = d("tr td.texto a.texto")
mapa = {}
secciones = [e.text for e in links]
client = MongoClient()
db = client.test

# print "Secciones encontradas: "
# for l in links:
#     print l.text.lower() #+ ": " +l.attrib['href']
#     mapa[l.text.lower()]= l.attrib['href']
#     if(l.text == "Su Vivienda"):
#         break
# seccion = raw_input("De que quieres saber? ")
# print("Has elegido la seccion \"" +seccion+"\" ("+mapa[seccion]+")")




for l in links:
    seccion = unidecode(l.text.lower())
    mapa[seccion] = l.attrib['href']
    if(l.text == "Su Vivienda"):
        break
    url = mapa[seccion]
    data = urllib2.urlopen(url)
    doc = xmltodict.parse(str(data.read()))
    print "\n"
    items = doc["rss"]["channel"]["item"]
    for item in items:
        print "\t"+color.BOLD + item["title"] + color.END+ " - " + item["pubDate"]
        print "\t"+item["description"].split("&nbsp;")[0]
        url = item["link"]
        print item["link"]
        if(not db[seccion].find({'link':url}).limit(1).count()):
            d = pq(url = url)
            parrafos = d("div[itemprop='articleBody'].row.content p:not(.summary-lead)")
            texto = ""
            for p in parrafos:
                texto += p.text_content() + " "
                try:
                    if(not (texto == "")):
                        item['my-keywords'] = keywords(texto,0.15).split('\n')
                        item['my-summary'] = summarize(texto,0.15)
                except:
                    print "ERROR con keywords o summary"
            result = db[seccion].insert_one(item)
            print "\t"+"Insertando " + str(result.inserted_id)
        else:
            print "\t"+"Existe"
        print "\n"

# noticia = raw_input("Que numero de noticia quieres ver? ")
# noticia = items[int(noticia)]
# url = noticia["link"]
# d = pq(url = url)
# parrafos = d("div[itemprop='articleBody'].row.content p:not(.summary-lead)")
# texto = ""
# for p in parrafos:
#     texto += p.text_content() + " "
#
# print texto
# print "\n"
# noticia["resumen"] = summarize(texto,0.15)
# print "Su resumen: "
# print noticia["resumen"]
# print "\n"
# noticia["keywords"] = keywords(texto)
# print "Sus keywords: "
# print noticia["keywords"]
