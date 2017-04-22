# Net Value

![Net Value Icon](https://raw.githubusercontent.com/goods37/Net-Value/master/client/icon.png "Net Value Icon")

A Google Chrome extension that allows you to find out how much any European footballer is worth. All data provided by Transfermarkt.

Available now on the Chrome Web Store! [Link](https://chrome.google.com/webstore/detail/net-value/afofcnmhimjdhmlijebpbdlhlhcjjchj)

## Client
* The client contains the Chrome extension itself. I'm using Bootstrap because I wanted it to look like every website ever (kidding, I'm just not much of a front end developer but I also did not want to sacrifice UI aesthetics). I did my best to change the color scheme around to make it appear less framework-based.
* The autocomplete search bar was done using JQuery UI.

## Server
The server is a simple Flask application with routes for two different API calls.
* The search API is an extension of Transfermarkt's search engine (I chose to list the results in descending order of player value, but this is done on the client side). Making a GET request to /api/search/ with a player's name appended will return a json list of players with their name, club, value, and the path to their Transfermarkt page.
* The player API retrieves data about a specific player, using the unique URL string after http://www.Transfermarkt.de as a key (with all “/“ replaced with “|”). Making a GET request to /api/player/ with this URL string appended will return a JSON containing the player’s name, club, value, position, age, a link to an image, and a list of of all their transfers.

