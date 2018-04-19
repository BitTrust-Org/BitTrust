from bs4 import BeautifulSoup as bs
import requests

from sqlalchemy import create_engine

id = 1


class Currency:
    global id

    def __init__(self, country, amount):
        global id
        self.id = id
        self.country = country
        self.amount = amount
        id += 1

    def addToDB(self, currency):
        conn.execute("INSERT INTO currency (country, amount) VALUES ('" + str(currency.country) + "', " + str(
            currency.amount) + ")")
        pass


def data_parse(soup):
    body = soup.body
    table_currency = body.select('table > tbody')[1].text
    table_currency = table_currency.replace("\n\n", ",")
    table_currency[1:-1]
    result = table_currency[1:-1].split("\n")
    for i in range(0, len(result), 3):
        c = Currency(str(result[i]), float(result[i + 1].strip()))
        print(str(result[i]), float(result[i + 1].strip()))
        c.addToDB(c)
    #currency(amount, currency_type, currency_map)


def currency(amount, currency_type, currency_map):
    print(amount / currency_map[currency_type])


def main():
    page = requests.get("https://www.x-rates.com/table/?from=USD&amount=1")
    page = page.content
    soup = bs(page, 'html.parser')
    data_parse(soup)


if __name__ == '__main__':
    global eng
    global conn
    eng = create_engine("sqlite:///mydb.db")
    conn = eng.connect()
    result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='currency'")
    results = str(result.first())
    if 'currency' not in results:
        conn.execute("CREATE TABLE currency (id INTEGER PRIMARY KEY AUTOINCREMENT, country TEXT, amount REAL)")
    else:
        conn.execute("DROP TABLE currency")
        conn.execute("CREATE TABLE currency (id INTEGER PRIMARY KEY AUTOINCREMENT, country TEXT, amount REAL)")
    main()
