from bs4 import BeautifulSoup as bs
import requests

from sqlalchemy import create_engine

id = 1


def data_parse(soup):
    body = soup.body
    table_currency = body.select('table > tbody')[1]
    conn.execute("INSERT INTO currency (country, amount, abv) VALUES ('" + "United States Dollars" + "', " + "1.000000" + ",'" + "USD" + "')")
    results = str(table_currency).split("\n")
    for i in range(1, len(results)-2,5):
        name = results[i+1][4:-5]
        key = results[i+2][(results[i+2].find("to=")+3):(results[i+2].find("to=")+6)]
        value = float(results[i+3][(results[i+3].find("USD\">")+5):(results[i+3].find("USD\">")+13)])
        conn.execute("INSERT INTO currency (country, amount, abv) VALUES ('" + str(name) + "', " + str(
            value) + ",'" + str(key) + "')")


def main():
    page = requests.get("https://www.x-rates.com/table/?from=USD&amount=1")
    page = page.content
    soup = bs(page, 'html.parser')
    data_parse(soup)
    print("--------End of Web Scrapping. Currencies are stored in the Database")


def init():
    print("--------Start WebScrapping www.x-rates.com")
    global eng
    global conn
    eng = create_engine("sqlite:///mydb.db")
    conn = eng.connect()
    result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='currency'")
    results = str(result.first())
    if 'currency' not in results:
        conn.execute("CREATE TABLE currency (id INTEGER PRIMARY KEY AUTOINCREMENT, country TEXT, amount REAL, abv TEXT)")
    else:
        conn.execute("DROP TABLE currency")
        conn.execute("CREATE TABLE currency (id INTEGER PRIMARY KEY AUTOINCREMENT, country TEXT, amount REAL, abv TEXT)")
    main()