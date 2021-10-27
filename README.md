# Tokpedia Product Scrapping

The code used in this repository are used for Information System class in Bandung State Polytechnics CS 2021.

## Usage

1. Create a new python environment

   1. Use venv to create a new virtual environment for Pyhton `python -m venv .env`
   2. Activate the virtual environment

      In Windows, `./.env/Scripts/activate`.
      Or in Linux/Mac `source ./.env/Scripts/activate`

   3. Install all dependencies, `pip install -r requirements.txt`

2. Get Stable MS-Edge driver from the [official website](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/) and unpack it into `./drivers`
3. Run the code using `python main.py`

### GQL Scraping

This script is using the graphql API of Tokopedia to get data much faster, and way more detailed. To use it follows the first step from above, and call the function `python gql_scraping.py`.

### Sentiment Script

To use the sentiment script follows the first step above, and then call the function `python sentiment.py` to start the server.

To call the the API, send POST data with the pattern of `{ "text": "the theing sentiment that's going to be analyzed" }` and the result will be `{ "polarity": 0 }`

Note that the text to do sentiment analysis with are set for Indonesian languages.

## License

MIT
