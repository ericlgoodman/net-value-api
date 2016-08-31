"""
Script to retrieve data from Transfermarkt. Used for the search and player API
"""

import urllib
import urllib2
import requests
import re
from bs4 import BeautifulSoup
import httplib

__author__ = "Eric Goodman"

class AppURLOpener(urllib.FancyURLopener):
    """
    Class to disguise server requests as incoming from Mozilla Firefox
    """
    version = "Mozilla/5.0"
urllib._urlopener = AppURLOpener()


def contains_digits(d):
    """
    Check if a string contains digits.

    Args:
        d: A string.

    Returns:
        A boolean indicating whether or not the string contains one or more
        digits.
    """
    _digits = re.compile('\d')
    return bool(_digits.search(d))


def getTableInfo(table):
    """
    Gets a player's age, position, and nationality from a table of data.

    Args:
        table: An HTML table containing that can be parsed to extract the
        relevant data.

    Returns:
        A tuple of strings containing the player's age, position, and
        nationality.
    """
    text = table.text
    try:
        age = text.split("Age:")[1].strip().split("\n")[0] \
            .encode("ascii", "ignore")
    except:
        age = "N/A"
    try:
        nationality = text.split("Nationality:")[1].strip().split("\n")[0] \
            .strip()
    except:
        nationality = "N/A"
    try:
        position = text.split("Position:")[1].strip().split("\n")[0].strip() \
            .encode("ascii", "ignore")
    except:
        position = "N/A"
    return (nationality, position, age)

def getValue(text):
    """
    Parses the player's value from a string.

    Args:
        text: The standard string of a player's value from Transfermarkt.

    Returns:
        A float representing the player's value. If the value cannot be parsed,
        returns -1.
    """
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
    """
    Gets a player's transfer history, storing the results in a list of tuples.

    Args:
        table: An HTML table containing that can be parsed to extract the
        relevant data.

    Returns:
        A list of tuples, with each tuple containing the date, origin club,
        destination club, and fee for a given transfer.
    """
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

def getPlayerInfo(url):
    """
    Overarching method to extract all relevant data regarding a player.

    Args:
        url: The Transfermarkt url of a player

    Returns:
        A tuple, containing a player's value, nationality, position, age, a link
        to an image, and a list of their transfer history.
    """
    #the HTML of the player's page
    html = BeautifulSoup(urllib.urlopen(url), 'html.parser')

    #Transfer history
    transfer_rows = html.find_all("tr", class_="zeile-transfer")
    transfers = getTransferHistory(transfer_rows)

    #Player image
    image_link = html.find("div", class_="dataBild").img['src']

    #Player value div
    value_text = html.find("div", class_="dataMarktwert").a.text \
        .split("Last")[0]
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

def getInfoFromId(_id):
    """
    Helper method for getPlayerInfo. Implemented to avoid requesting the server
    multiple times for the same player.

    Args:
        _id: The string containing the path to the player's page on
        Transfermarkt.

    Returns:
        getPlayerInfo
    """
    url = "http://www.transfermarkt.com/" + _id
    return getPlayerInfo(url)

def search(query):
    """
    Function for search API.

    Args:
        query: A string containing the search term.

    Returns:
        A dictionary. The keys are the names of the player's as strings (unless
        in the case of a duplicate player name, in which case the key is the
        player name + "| duplicate"), the values are tuples containing the
        player's name, club, value, and a link to their Transfermarkt profile.
    """

    new_query = "http://www.transfermarkt.de/schnellsuche/ergebnis/schnell" \
        "suche?query=" + query + "&x=0&y=0"

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
                team = player.find("a", "vereinprofil_tooltip").text \
                    .encode("ascii", "ignore")
            else:
                team = None

            if player.find("td", class_="rechts hauptlink"):
                value = player.find("td", class_="rechts hauptlink").text \
                    .replace(",", ".").encode("ascii", "ignore")
                value = getValue(value)
                if value == -1:
                    value = None
            else:
                value = None

            if name is not None and link is not None and team is not None and \
                value is not None:
                if name not in results:
                    results[name] = (name, team, value, link)
                else:
                    name+="|duplicate"
                    results[name] = (name, team, value, link)
    return results
