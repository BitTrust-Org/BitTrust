from bs4 import BeautifulSoup as bs
from sqlalchemy import create_engine
import requests

# get the data and parse it
def data_parse(soup):
    body = soup.body
    # look for tbody tag
    table_currency = body.select('table > tbody')[1]
    # insert USD AMOUNT
    conn.execute("INSERT INTO currency (country, amount, abv) VALUES ('" + "United States Dollars" + "', " + "1.000000" + ",'" + "USD" + "')")
    results = str(table_currency).split("\n")
    # parse the rest of the data, perform web scrapping and store it into the table
    for i in range(1, len(results)-2,5):
        name = results[i+1][4:-5]
        key = results[i+2][(results[i+2].find("to=")+3):(results[i+2].find("to=")+6)]
        value = float(results[i+3][(results[i+3].find("USD\">")+5):(results[i+3].find("USD\">")+13)])
        conn.execute("INSERT INTO currency (country, amount, abv) VALUES ('" + str(name) + "', " + str(
            value) + ",'" + str(key) + "')")


def main():
    # Get the website, content, and html parser. Send the soup value to data_parse(soup) to parse.
    page = requests.get("https://www.x-rates.com/table/?from=USD&amount=1")
    page = page.content
    soup = bs(page, 'html.parser')
    data_parse(soup)
    print("--------End of Web Scrapping. Currencies are stored in the Database")


def init():
    print("--------Start WebScrapping www.x-rates.com")
    global conn
    conn = create_engine("sqlite:///mydb.db").connect()
    # Start Execution
    main()
