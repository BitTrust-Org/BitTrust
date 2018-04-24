import BitFinex
import bitstamp
import Currency
import BitCoinPrice
from threading import Thread
from sqlalchemy import create_engine
import sys
import matplotlib.pyplot as plt
from datetime import timedelta
import pandas as pd

def getAveragePrices(Query):
    results = conn.execute(Query)
    values = []
    for rows in results:
        data = str(rows).split(",")
        values.append(float(data[0][1:].strip()))
    return sum(values) / len(values)

# Return Min Price/Count of Bid
def userBuyingBitcoin():
    results = conn.execute("SELECT price, count from orderBooks WHERE type = 'bid'")
    prices = []
    counts = []
    for rows in results:
        data = str(rows).split(", ")
        count = float((data[1])[0:-2])
        price = float(data[0][1:].strip())
        if count > 0:
            prices.append(price)
            counts.append(count)
    price_per_bitcoin = []
    for i in range(0, len(prices)):
        ratio = float(prices[i]/counts[i])
        if ratio > float(6000) and ratio < float(12000):
            price_per_bitcoin.append(float(prices[i]/counts[i]))
    return min(price_per_bitcoin)

# Return Max Price/Count of Ask
def userSellingBitcoin():
    results = conn.execute("SELECT price, count from orderBooks WHERE type = 'ask'")
    prices = []
    counts = []
    for rows in results:
        data = str(rows).split(", ")
        count = float((data[1])[0:-2])
        price = float(data[0][1:].strip())
        if count > 0:
            prices.append(price)
            counts.append(count)
    price_per_bitcoin = []
    for i in range(0, len(prices)):
        ratio = float(prices[i] / counts[i])
        if ratio > float(6000) and ratio < float(12000):
            price_per_bitcoin.append(float(prices[i] / counts[i]))
    return max(price_per_bitcoin)

def trendAnalysis():
    results = conn.execute("SELECT average from bitcoinAvg")
    prices = []
    for rows in results:
        data = str(rows).split(",")
        prices.append(float(data[0][1:].strip()))
    mean_total = sum(prices) / len(prices)
    mean_half = sum(prices[1:(int(len(prices) / 2))]) / (len(prices) / 2)
    if mean_total >= mean_half:
        return "BUY"
    else:
        return "SELL"

def BitcoinPriceGraph():
    results = conn.execute("SELECT average, time from bitcoinAvg")
    average = []
    time = []
    for rows in results:
        data = str(rows).split(", ")
        average.append(float(data[0][1:].strip()))
        time_string = str(data[1])[1:-2] + ".000000"
        time.append(pd.to_datetime(time_string) - timedelta(hours=4))
    plt.plot(time, average)
    plt.gcf().autofmt_xdate()
    plt.show()

def AskBidPriceGraph():
    pass

def printAllCurrencyOption():
    results = conn.execute("SELECT abv from currency")
    currencies = []
    for rows in results:
        data = str(rows).split(",")
        currencies.append(str(data[0][2:-1].strip()))
    return currencies

def CurrencyConvertor(amount, home_currency, target_currency):
    currencies = printAllCurrencyOption()
    if home_currency in currencies and target_currency in currencies:
        queryResult = conn.execute("SELECT amount from currency WHERE abv is'"+str(home_currency)+"'")
        for rows in queryResult:
            data = str(rows).split(",")
            home_factor = (float(data[0][1:].strip()))

        queryResult = conn.execute("SELECT amount from currency WHERE abv is'" + str(target_currency) + "'")
        for rows in queryResult:
            data = str(rows).split(",")
            away_factor = (float(data[0][1:].strip()))

        if str(home_currency) == 'USD':
            factor = 1/away_factor
        elif str(target_currency) == 'USD':
            factor = home_factor
        else:
            factor = CurrencyConvertor(CurrencyConvertor(amount,home_currency,'USD'),'USD',target_currency)
        return factor * float(amount)
    else:
        print("Currency Format not supported. Press 10. to see all available currency format")

def StartUserOperations():
    print("Start of User Queries")
    while(True):
        userChoice = input("1. Get Average price of a bitCoin (Current)\n"
                           "2. Get Average Bid Price\n"
                           "3. Get Average Ask Price\n"
                           "4. Minimum price to buy 1 bitCoin\n"
                           "5. Maximum price to sell 1 bitCoin\n"
                           "6. Trend Analysis. (Should I buy or Sell)\n"
                           "7. Display bitCoin Price Graph\n"
                           "8. Display Ask/Bid Graph\n"
                           "9. Convert Currency\n"
                           "10. See All Available Currency Format\n"
                           "11. Curious! Know how many bitCoin you can buy at your currency choice\n"
                           "12. Exit\n")
        if userChoice is '1':
            print("Current Average price of bitCoin is: " + str(getAveragePrices(Query ="SELECT average from bitcoinAvg")) + " USD")
        elif userChoice is '2':
            print("Current Average Bid Price of bitCoin is: " + str(getAveragePrices(Query ="SELECT price FROM orderBooks WHERE type = 'bid'")) + " USD")
        elif userChoice is '3':
            print("Current Average Ask Price of bitCoin is: " + str(getAveragePrices(Query="SELECT price FROM orderBooks WHERE type = 'ask'")) + " USD")
        elif userChoice is '4':
            print("Minimum price to buy 1 bitCoin: " + str(userBuyingBitcoin()) + " USD")
        elif userChoice is '5':
            print("Maximum price to sell 1 bitCoin: " + str(userSellingBitcoin()) + " USD")
        elif userChoice is '6':
            trend = str(trendAnalysis())
            if trend is 'BUY':
                print("This is the right time to " + trend + " bitCoin. At the price of " + str(userBuyingBitcoin()) + " USD")
            else:
                print("This is the right time to " + trend + " bitCoin. At the price of " + str(userSellingBitcoin()) + " USD")
        elif userChoice is '7':
            BitcoinPriceGraph()
        elif userChoice is '8':
            AskBidPriceGraph()
        elif userChoice is '9':
            amount = input("Enter Amount\n")
            home_Currency = input("This Amount is in, which Currency?\n").upper()
            target_Currency = input("Convert " + str(amount) + " " + str(home_Currency) + " to what currency?\n").upper()
            print(str(amount) + " " + str(home_Currency) +" is " + str(CurrencyConvertor(amount, home_Currency, target_Currency )) + " " + str(target_Currency) )
        elif int(userChoice) == 10:
            print(printAllCurrencyOption())
        elif int(userChoice) == 11:
            amount = input("Enter Amount\n")
            home_Currency = input("This Amount is in, which Currency?\n").upper()
            trend = str(trendAnalysis())
            amountInUSD = CurrencyConvertor(amount,home_Currency,'USD')
            maxbitCoinToBuy = float(amountInUSD) / float(getAveragePrices(Query="SELECT average from bitcoinAvg"))
            print("Based on our Analysis, This is the right time to " + trend + " bitCoins.\n"
                    "You can at Max Buy " + str(maxbitCoinToBuy) + ", bitCoins at the price of "+ str(amount) + " " + str(home_Currency))
        elif int(userChoice) == 12:
            sys.exit()
        else:
            print("Please Input correct Option!")

    # --------------Static operations require no furthur user input
    # Get the average price of bitcoin
    # Get the average bid price
    # get the average ask price
    # display bitcoin price graph
    # display ask/bid graph

    # --------------Based on analysis
    # should I buy or sell (trend analysis)

    # convert currency (Input home currency, away currency and amount) => (output value in away currency)
    # Major operation (Input currency, amount [=> internally convert to USD]) => (display "You can buy x bitcoin at
    #                                                                                      this amount or can sell y
    #                                                                                       bitcoin with this")

if __name__ == '__main__':
    global conn
    global th
    eng = create_engine("sqlite:///mydb.db")
    print("Filling up database. Please wait! this process might take 3-5 min.")
    conn = eng.connect()
    Currency.init()
    BitCoinPrice.init()
    bitstamp.init()
    th1 = Thread(target=BitFinex.init)
    th1.daemon = True
    th1.start()
    StartUserOperations()