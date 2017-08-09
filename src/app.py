from data import all_player_data_from_id, search_for_player, contains_digits
from flask import Flask, jsonify, abort
import os

___author___ = "Eric Goodman"

app = Flask(__name__)

#Search API
@app.route('/api/search/<player_name>', methods=['GET'])
def query_for_player_name(player_name):
    if not player_name:
        abort(404)
    if contains_digits(player_name):
        abort(400)
    results = search_for_player(player_name)
    return jsonify({'results':results})

#Player API
@app.route('/api/player/<string:query>', methods=['GET'])
def get_player(query):
    query = query.replace("|","/")
    results = all_player_data_from_id(query)
    return jsonify({'query_results':results})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
