from data import all_player_data_from_id, search, contains_digits
from flask import Flask, jsonify, abort

___author___ = "Eric Goodman"

app = Flask(__name__)

#Search API
@app.route('/api/search/<string:query>', methods=['GET'])
def get_query(query):
    if len(query) == 0:
        abort(404)
    if contains_digits(query):
        abort(400)
    results = search(query)
    return jsonify({'results':results})

#Player API
@app.route('/api/player/<string:query>', methods=['GET'])
def get_player(query):
    query = query.replace("|","/")
    results = all_player_data_from_id(query)
    return jsonify({'query_results':results})

if __name__ == '__main__':
    app.run()
