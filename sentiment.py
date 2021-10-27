from flask.json import jsonify
from textblob import TextBlob
from flask import Flask
from flask import request
import json

app = Flask(__name__)


@app.route("/", methods=["POST"])
def sentiment():
    body = request.get_json()
    analysis = TextBlob(body["text"])
    an = analysis.translate(from_lang='id', to='en')

    return jsonify(json.dumps({"polarity": an.sentiment.polarity}))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
