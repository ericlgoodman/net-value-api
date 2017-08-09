import urllib
import re
from bs4 import BeautifulSoup

__author__ = "Eric Goodman"

class AppURLOpener(urllib.FancyURLopener):
    """
    Class to disguise server requests as incoming from Mozilla Firefox
    """
    version = "Mozilla/5.0"

urllib._urlopener = AppURLOpener()

"""
=== FUNCTIONS ===
"""

def contains_digits(d):
    """
    Check if a string contains digits.

    Args:
        d: A string.

    Returns:
        True if the string contains digits
    """
    return bool(re.compile('\d').search(d))


def get_player_data_from_table(table):
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


def player_value_to_string(text):
    """
    Parses the player's value from a string.

    Args:
        text: The standard string of a player's value from Transfermarkt.

    Returns:
        A float representing the player's value. If the value cannot be parsed,
        returns None.
    """

    # Free transfer
    if "Free" in text:
        value = 0

    elif "M" in text:
        value = float(text.split("M")[0].replace(",", "."))

    elif "T" in text:
        value = float(text.split("T")[0].replace(",", ".")) / 1000

    else:
        return None

    return value


def get_transfer_history_from_table(table):
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
        cells = row.find_all("td")

        transfer_date = cells[1].text
        origin = cells[2].a.img['alt']
        destination = cells[6].a.img['alt']

        raw_fee = cells[11].text.encode("ascii", "ignore")
        fee = player_value_to_string(raw_fee)

        if fee is not None:
            transfers.append((transfer_date, origin, destination, fee))
    return transfers


def get_player_info(url):
    """
    Overarching method to extract all relevant data regarding a player.

    Args:
        url: The Transfermarkt url of a player

    Returns:
        A tuple, containing a player's value, nationality, position, age, a link
        to an image, and a list of their transfer history.
    """

    html = BeautifulSoup(urllib.urlopen(url), 'html.parser')

    # Transfer history
    transfer_rows = html.find_all("tr", class_="zeile-transfer")
    transfers = get_transfer_history_from_table(transfer_rows)

    # Player image
    image_link = html.find("div", class_="dataBild").img['src']

    # Player value div
    value_text = html.find("div", class_="dataMarktwert").a.text.split("Last")[0]
    value = player_value_to_string(value_text)

    # Table where other data is located
    table = html.find("div", class_="spielerdaten").table
    table_data = get_player_data_from_table(table)

    nationality = table_data[0]
    position = table_data[1]
    age = table_data[2]

    return (value, nationality, position, age, image_link, transfers)


def all_player_data_from_id(_id):
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
    return get_player_info(url)


def search_for_player(player_name):
    """
    Function for search API.

    Args:
        player_name: A string containing the search term.

    Returns:
        A dictionary. The keys are the names of the player's as strings (unless
        in the case of a duplicate player name, in which case the key is the
        player name + "| duplicate"), the values are tuples containing the
        player's name, club, value, and a link to their Transfermarkt profile.
    """

    url = 'http://www.transfermarkt.de/schnellsuche/ergebnis/schnellsuche?query={}&x=0&y=0'.format(player_name)
    html = BeautifulSoup(urllib.urlopen(url), 'html.parser')
    results = {}

    if not html.find("table", class_="items"):
        return {}

    table = html.find("table", class_="items").tbody

    for player in table.find_all(True, {'class': ['odd', 'even']}):
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
            raw_player_value = player.find("td", class_="rechts hauptlink").text.replace(",", ".").encode("ascii",
                "ignore")
            player_value = player_value_to_string(raw_player_value)

        else:
            player_value = None

        if name and link and team and player_value:
            if name not in results:
                results[name] = (name, team, raw_player_value, link)

            else:  # Duplicate
                name += "|duplicate"
                results[name] = (name, team, raw_player_value, link)
    return results
