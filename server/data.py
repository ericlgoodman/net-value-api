from bs4 import BeautifulSoup
import re
import textract
import urllib
import urllib2
import requests
import tempfile
import httplib
from textblob import TextBlob

#Make web scraper appear as an innocent Firefox browser
class AppURLOpener(urllib.FancyURLopener):
    version = "Mozilla/5.0"
urllib._urlopener = AppURLOpener()

#Function for API to check if string contains digits
def contains_digits(d):
    _digits = re.compile('\d')
    return bool(_digits.search(d))

#Get player's age, position, and nationality from table of data
def getTableInfo(table):
    text = table.text
    try:
        age = text.split("Age:")[1].strip().split("\n")[0].encode("ascii", "ignore")
    except:
        age = "N/A"
    try:
        nationality = text.split("Nationality:")[1].strip().split("\n")[0].strip()
    except:
        nationality = "N/A"
    try:
        position = text.split("Position:")[1].strip().split("\n")[0].strip().encode("ascii", "ignore")
    except:
        position = "N/A"
    return (nationality, position, age)

#Get player's value
def getValue(text):
    try:
        if "Free" in text:
            value = 0
        elif "M" in text:
            value = float(text.split("M")[0].replace(",", "."))
        elif "T" in text:
            value = float(text.split("T")[0].replace(",", "."))/1000
        else:
            value = -1
        return value
    except:
        return -1

def getTransferHistory(table):
    transfers = []
    for row in table:
        #Get all the cells
        cells = row.find_all("td")

        transfer_date = cells[1].text
        origin = cells[2].a.img['alt']
        destination = cells[6].a.img['alt']

        raw_fee = cells[11].text.encode("ascii", "ignore")
        fee = getValue(raw_fee)

        if fee != -1:
            transfers.append((transfer_date, origin, destination, fee))
    return transfers

#Get a player's basic info
def getPlayerInfo(url):
    #the HTML of the player's page
    html = BeautifulSoup(urllib.urlopen(url), 'html.parser')

    #Transfer history
    transfer_rows = html.find_all("tr", class_="zeile-transfer")
    transfers = getTransferHistory(transfer_rows)

    #Player image
    image_link = html.find("div", class_="dataBild").img['src']

    #Player value div
    value_text = html.find("div", class_="dataMarktwert").a.text.split("Last")[0]
    value = getValue(value_text)

    #Table where other data is located
    table = html.find("div", class_="spielerdaten").table

    #Get the info
    info = getTableInfo(table)

    #Assign
    nationality = info[0]
    position = info[1]
    age = info[2]

    #Return
    return (value, nationality, position, age, image_link, transfers)

#Helper function
def getInfoFromId(_id):
    url = "http://www.transfermarkt.com/" + _id
    return getPlayerInfo(url)

#Function for search API
def search(queryString):
    query = "http://www.transfermarkt.de/schnellsuche/ergebnis/schnellsuche?query=" + queryString + "&x=0&y=0"

    #Get the HTML
    html = BeautifulSoup(urllib.urlopen(query), 'html.parser')

    results = {}
    if html.find("table", class_="items"):
        table = html.find("table", class_="items").tbody

        #Iterate over every player
        for player in table.find_all(True, {'class':['odd', 'even']}):
            if player.find("a", class_="spielprofil_tooltip"):
                name = player.find("a", class_="spielprofil_tooltip").text
                link = player.find("a", class_="spielprofil_tooltip")['href']
            else:
                name = None
                link = None

            if player.find("a", "vereinprofil_tooltip"):
                team = player.find("a", "vereinprofil_tooltip").text.encode("ascii", "ignore")
            else:
                team = None

            if player.find("td", class_="rechts hauptlink"):
                value = player.find("td", class_="rechts hauptlink").text.replace(",", ".").encode("ascii", "ignore")
                value = getValue(value)
                if value == -1:
                    value = None
            else:
                value = None

            if name is not None and link is not None and team is not None and value is not None:
                if name not in results:
                    results[name] = (name, team, value, link)
                else:
                    name+="|duplicate"
                    results[name] = (name, team, value, link)
    return results
