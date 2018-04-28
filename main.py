from datetime import timedelta
from threading import Thread
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import BitFinex
import bitstamp
import Currency
import BitCoinPrice
import sys

# this function is used as by bitstamp and bitfinex python progams, to get rid of garbage values in orderBooks Data
def getMeanAndStDevBitCoinPrice():
    # get all the value of bitcoin prices
    results = create_engine("sqlite:///mydb.db").connect().execute("SELECT average from bitcoinAvg")
    values = []
    # for each entry in result, parse data and store it in values
    for rows in results:
        data = str(rows).split(",")
        values.append(float(data[0][1:].strip()))
    # get the mean and std deviation of these values
    meanValue = np.mean(values)
    stdValue = np.std(values)
    # return the range to Bitfinex.py and bitstamp.py. The range includes 99% of data and excludes outliers
    range = [(meanValue - (3*stdValue)), (meanValue + (3*stdValue))]
    return range

# User menu option #1,2 & 3 to get the average prices of bitcoin, bid, ask.
def getAveragePrices(Query):
    # perform the query
    results = conn.execute(Query)
    values = []
    # for each entry in result, parse data and store it in values
    for rows in results:
        data = str(rows).split(",")
        values.append(float(data[0][1:].strip()))
    # Return average value
    return sum(values) / len(values)

# Return Min Price/Count of Bid or Max Price/Count of ask. Used in option #4,5 & 6
def userBuyingSellingBitcoin(Query):
    results = conn.execute(Query)
    values = []
    for rows in results:
        data = str(rows).split(", ")
        values.append(float(data[0][1:-2].strip()))
    # Check if we need to return min or max value
    if str(Query).__contains__("bid"):
        return min(values)
    else:
        return max(values)

# should the user sell or buy. Option# 6 & 10
def trendAnalysis():
    results = conn.execute("SELECT average from bitcoinAvg")
    prices = []
    for rows in results:
        data = str(rows).split(",")
        prices.append(float(data[0][1:].strip()))
    # get the mean of all the datapoints and half of the latest datapoints.
    mean_total = sum(prices) / len(prices)
    mean_half = sum(prices[1:(int(len(prices) / 2))]) / (len(prices) / 2)
    # if the later half has a mean <= the mean of all the values, we buy. Otherwise we sell.
    if mean_total >= mean_half:
        return "BUY"
    else:
        return "SELL"

# Option #7. This method deal with ploting the bitcoin prices with respect to time
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
    pass

# Option #8. Get abv from currency and print every currency our method can take care of
def printAllCurrencyOption():
    results = conn.execute("SELECT abv from currency")
    currencies = []
    for rows in results:
        data = str(rows).split(",")
        currencies.append(str(data[0][2:-1].strip()))
    return currencies

# Option 9, 10. Convert currency from home_currency to target_currency
def CurrencyConvertor(amount, home_currency, target_currency):
    # check if both the currencies is supported by our program
    currencies = printAllCurrencyOption()
    if home_currency in currencies and target_currency in currencies:
        queryResult = conn.execute("SELECT amount from currency WHERE abv is'"+str(home_currency)+"'")
        # First we will convert home_currency to USD, take home_currency factor
        for rows in queryResult:
            data = str(rows).split(",")
            home_factor = (float(data[0][1:].strip()))

        # Second we will convert USD amount to target currency
        queryResult = conn.execute("SELECT amount from currency WHERE abv is'" + str(target_currency) + "'")
        for rows in queryResult:
            data = str(rows).split(",")
            away_factor = (float(data[0][1:].strip()))

        # if the home_currency was USD, we need the inverse of the factor
        if str(home_currency) == 'USD':
            factor = 1/away_factor
        # else if target_currency was USD, the factor is straight away given
        elif str(target_currency) == 'USD':
            factor = home_factor
        # if both currencies (home, target) are not in USD, then convert home_currency to USD and then to target_currency
        else:
            factor = CurrencyConvertor(CurrencyConvertor(amount,home_currency,'USD'),'USD',target_currency)
        # return the amount
        return factor * float(amount)
    else:
        print("Currency Format not supported. Press 8. to see all available currency format")

# check if the tables exist in the database. If it does, drop all the tables and then create
def checkIfDatabaseTablesExist():
    result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bitcoinAvg'")
    results = str(result.first())
    if 'bitcoinAvg' not in results:
        createDatabaseTables()
    else:
        # Table exists, drop all the table and then recreate the tables.
        # Two modes of execution if possible from here.
        # First: we can either remove this else block, such that each time we run the program, the database table grows.
        # Second: the approach we followed, to start with a fresh set of data everytime the program runs
        conn.execute("DROP TABLE currency")
        conn.execute("DROP TABLE bitcoinAvg")
        conn.execute("DROP TABLE orderBooks")
        createDatabaseTables()

# Create Database Table
def createDatabaseTables():
    # Create currency table
    conn.execute("CREATE TABLE currency (id INTEGER PRIMARY KEY AUTOINCREMENT, country TEXT, amount REAL, abv TEXT)")
    # Create table for bitcoinAvg
    conn.execute("CREATE TABLE bitcoinAvg (id INTEGER PRIMARY KEY AUTOINCREMENT, average REAL, time TEXT)")
    # Create orderBooks table
    conn.execute("CREATE TABLE orderBooks (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, price REAL, amount REAL, bitcoinCount REAL, exchange TEXT)")

def StartUserOperations():
    print("Start of User Queries")
    while(True):
        # User menu
        userChoice = input("1. Get Average price of a bitCoin (Current)\n"
                           "2. Get Average Bid Price\n"
                           "3. Get Average Ask Price\n"
                           "4. Minimum price to buy 1 bitCoin\n"
                           "5. Maximum price to sell 1 bitCoin\n"
                           "6. Display bitCoin Price Graph (Close the graph to proceed further)\n"
                           "7. Trend Analysis. (Should I buy or Sell)\n"
                           "8. See All Available Currency Format\n"
                           "9. Convert Currency\n"
                           "10. Curious! Know how many bitCoin you can buy at your currency choice\n"
                           "11. Exit\n")
        # Get the average price of bitcoin
        if int(userChoice) == 1:
            print("Current Average price of bitCoin is: " + str(getAveragePrices(Query ="SELECT average from bitcoinAvg")) + " USD")
        # Get the average bid price
        elif int(userChoice) == 2:
            print("Currently on average people are willing to buy 1 bitcoin for a price of: " + str(getAveragePrices(Query ="SELECT price FROM orderBooks WHERE type = 'bid'")) + " USD")
        # Get the average ask price
        elif int(userChoice) == 3:
            print("Currently on average people are willing to sell 1 bitcoin for a price of: " + str(getAveragePrices(Query="SELECT price FROM orderBooks WHERE type = 'ask'")) + " USD")
        # Get the minimum price to buy 1 bitcoin
        elif int(userChoice) == 4:
            print("The minimum amount, you would have to shell out (to buy 1 bitCoin): " + str(userBuyingSellingBitcoin(Query = "SELECT bitcoinCount from orderBooks WHERE type = 'bid'")) + " USD")
        # Get the maximum price at which there exists a buyer to buy 1 bitcoin
        elif int(userChoice) == 5:
            print("The maximum a buyer can pay (to buy 1 bitCoin): " + str(userBuyingSellingBitcoin(Query = "SELECT bitcoinCount from orderBooks WHERE type = 'ask'")) + " USD")
        # Display the price graph of bitcoin prices with respect to time
        elif int(userChoice) == 6:
            BitcoinPriceGraph()
            pass
        # Should you sell or buy
        elif int(userChoice) == 7:
            trend = str(trendAnalysis())
            if trend is 'BUY':
                print("This is the right time to " + trend + " bitCoin. At the price of " + str(userBuyingSellingBitcoin(Query = "SELECT bitcoinCount from orderBooks WHERE type = 'bid'")) + " USD")
            else:
                print("This is the right time to " + trend + " bitCoin. At the price of " + str(userBuyingSellingBitcoin(Query = "SELECT bitcoinCount from orderBooks WHERE type = 'ask'")) + " USD")
        # Print all currency options
        elif int(userChoice) == 8:
            print(printAllCurrencyOption())
        # convert currency
        elif int(userChoice) == 9:
            # input amount, home_currency, target_currency
            amount = input("Enter Amount\n")
            home_Currency = input("This Amount is in, which Currency?\n").upper()
            target_Currency = input("Convert " + str(amount) + " " + str(home_Currency) + " to what currency?\n").upper()
            # call the function and convert the amount
            print(str(amount) + " " + str(home_Currency) + " is " + str(
                CurrencyConvertor(amount, home_Currency, target_Currency)) + " " + str(target_Currency))
        # perform extra analysis
        elif int(userChoice) == 10:
            amount = input("Enter Amount\n")
            home_Currency = input("This Amount is in, which Currency?\n").upper()
            trend = str(trendAnalysis())
            # convert money to usd
            amountInUSD = CurrencyConvertor(amount,home_Currency,'USD')
            bitCoinToBuy = float(amountInUSD) / float(getAveragePrices(Query ="SELECT average from bitcoinAvg"))
            # display the analysis
            print("Based on our Analysis, This is the right time to " + trend + " bitCoins.\n"
                    "You can should be able to buy " + str(bitCoinToBuy) + ", bitCoins at the price of "+ str(amount) + " " + str(home_Currency))
        # exit user menu
        elif int(userChoice) == 11:
            sys.exit()
        else:
            print("Please Input correct Option!")

if __name__ == '__main__':
    global conn
    # SQLite engine created via SQLAlchemy
    eng = create_engine("sqlite:///mydb.db")
    print("Filling up database. Please wait! this process might take 5-8 min.")
    conn = eng.connect()

    # Check if tables already exist in the database. A simple way to enable re run of the program
    checkIfDatabaseTablesExist()
    # Start web scrapping currency information
    Currency.init()
    # BitcoinAvg API to get bitcoin price in database
    BitCoinPrice.init()
    # bitstamp API to get OrderBooks details
    bitstamp.init()
    # Start relay of orderBooks data from Bitfinex, using websocket. This is done on a thread to enable simuntaneous execution
    th = Thread(target=BitFinex.init)
    # To enable system.exit(0) set daemon to true
    th.daemon = True
    th.start()
    # Give users the option to perform actions on
    StartUserOperations()