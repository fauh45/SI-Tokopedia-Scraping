from textblob import TextBlob
import sys
import json

try:
    target_text = sys.argv[1]

    analysis = TextBlob(target_text)
    an = analysis.translate(from_lang='id', to='en')
    print(json.dumps(an.sentiment.polarity))

except IndexError:
    print("Error: Text arguments not found", file=sys.stderr)
    print(0)
except Exception as err:
    print("System error: " + str(err), file=sys.stderr)
    print(0)
