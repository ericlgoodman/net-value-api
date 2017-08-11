# Net Value Server
Flask application with routes for two different API calls.
* The search API is an extension of Transfermarkt's search engine (I chose to list the results in descending order of player value, but this is done on the client side). Making a GET request to /api/search/ with a player's name appended will return a json list of players with their name, club, value, and the path to their Transfermarkt page.
* The player API retrieves data about a specific player, using the unique URL string after http://www.Transfermarkt.de as a key (with all “/“ replaced with “|”). Making a GET request to /api/player/ with this URL string appended will return a JSON containing the player’s name, club, value, position, age, a link to an image, and a list of of all their transfers.

