# Steps to execute
0. be in a empty directory {let's say /myAwesomeProject}
1. git init
2. git pull https://github.com/BitTrust-Org/BitTrust.git
3. cd env\scripts
4. activate
5. cd..
6. cd..
Catution: make sure you are in the /myAwesomeProject directory
7. pip install -r requirements.txt
8. python main.py

# BitcoinPredict (API)
When the user enters our web page, he will see the previous 28 hours(1680 minutes) of bitcoin prices in USD. It also shows the trend in the data, if it is increasing or decreasing.
Based on this data, we will predict if the user should buy or sell bitcoins.
If the trend is decreasing, the user must buy bitcoins, otherwise sell bitcoins.
It also gives the average bitcoin price for the past 28 hours
For this, we are using the API: BitcoinPredict https://apiv2.bitcoinaverage.com/
The trend changes every minute, as it appends rows to the database.
The data collected has 2 parameters – the time and the average price of Bitcoin (USD) for that minute.
Using this data, we will plot a graph, showing the trend of the average price of Bitcoin (USD) v/s the time and recommend if the user should sell or buy.
 
# CurrencyConvertor (Webscraping)
We will perform currency conversion based on current market rates from https://www.x-rates.com/table/?from=USD&amount=1. This data is pretty much the same during the day, and hence we don’t update it every second. 
Based on the amount entered by the user in a particular currency, the amount is converted to the corresponding amount in USD.
We scrape two values from the same, the country and its corresponding factor.
If for Indian Rupee, the corresponding factor is 65.7, then we take our given amount and divide it by the factor, to convert from INR to USD.
 
Once the user enters the corresponding amount, its currency and ask/bid, we now use the below two API’s to display the max price at which the user should bid or the minimum price to ask for a bitcoin. We will also show the max number of bitcoin user can buy/sell for a particular amount (Multi-Currency Support). 

# Bitfinex (API):
Bitfinex API continously relays information about their orderbook table. The data flow is nearly 20,000 data points per second. However, the data response is in JSON format we had to convert it into a format so that we could store it in sqlite database. We did JSON Parsing. Alon with it there were multiple values we need to take care of sometimes an error bit "hb" is sent by Bitfinex, we made sure to get rid of these values. We have used Websocket connection for Handling taking data from Bitfinex.

# BitStamp(API):
BitStamo is pretty prompt in sending data. Just for a comparision we receive nearly 30,000 data points per second. Again the data is in JSON. We performed JSON Parsing. The amount portion of the returned values (tuples) needs to be checked if it was -ve it meant ask and if +ve it meant bid. We need to clean and perform these operation as ameasure to clean the data
 
We have merged data from the bitfinex and bitstamp API, to make our analysis accurate and better.

# Note
All the three 3 API send data continuously, This data is stored in SQLite Database and would we continuously relay it with each request/update.
