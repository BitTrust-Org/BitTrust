from urllib.request import Request, urlopen

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


def data_parse(data, amount, currency_type):
    cut_left = data.find("rates") + len("rates") + 2
    data_format = data[cut_left:len(data) - 2]
    currency_map = dict(eval(data_format))
    for key in currency_map.keys():
        currency_map[key] = currency_map[key] / currency_map["USD"]
        c = Currency(key, float(currency_map[key]))
        c.addToDB(c)
    currency(amount, currency_type, currency_map)


def currency(amount, currency_type, currency_map):
    print(amount / currency_map[currency_type])


def main():
    request = Request('http://data.fixer.io/api/latest?access_key=989541bb7957f9df0190554d77bf0b68')
    response = urlopen(request)
    data = response.read()
    data_parse(str(data), 65, "INR")


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
