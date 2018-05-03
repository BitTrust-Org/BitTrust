# Steps to execute
1. In command prompt navigate to an empty directory {let's say /bittrade}
2. git init
3. git pull https://github.com/BitTrust-Org/BitTrust.git
4. cd env\scripts
5. activate
6. cd..
7. cd..

Catution: make sure you are in the /bittrade directory

8. pip install -r requirements.txt
9. python main.py

# Introduction
Our mission is to be your personal techno-intelligent bitcoin investment counsellor. Our platform allows the customers to enter the amount they want to invest, and based on the current trend of the market the platform recommends the quantity of bitcoins the customer should buy or sell.
Following are our product features:
1. Continuous data stored and accessed in the database using threads.
2. Make predictions using TimeSeries forecasting.
3. Currency conversion.
4. Recommending the best possible transaction for a given dollar amount.
5. Market Analysis

# Data Sources (In Brief)
1. Bitfinex (Web-socket) - thread based - continous relay of data
2. BitStamp (API) 
3. BitcoinAverage (API) 
4. www.x-rates.com (Web Scrapping) 

# Data Cleaning
We have applied data cleaning in three places:
1. When we are identifiying if the data coming from Bitfinex is complete. we don't take incomplete transaction request from bitfinex.
2. Also, we need to get rid of falsified data. We are only accepting those bid/ask values which lies in the range of 10 standard deviation of the average price at current time. 10 standard deviation is like taking care of 99.9999999% values.
3. In Bitfinex we needed to check if the amount bit was negative or positive. It meant that +ve was for ask and -ve for bid. This was a crucial element in merging Bitfinex and Bitstamp.

# Data Merging
Bitfinex continous relays the data information. Bitstamp gives around 30,000 (unfilltered) data points. These two seprate channel (read python program) store the same table (orderBooks) in the same data. We have made sure that the data is altered to support both the result's schema.

# Bitfinex (API):
Bitfinex API continously relays information about their orderbook table. The data flow is nearly 20,000 data points per second. However, the data response is in JSON format we had to convert it into a format so that we could store it in sqlite database. We did JSON Parsing. Along with it there were multiple values we need to take care of sometimes an error bit "hb" is sent by Bitfinex, we made sure to get rid of these values. We have used Websocket connection for Handling taking data from Bitfinex. The amount portion of the returned values (tuples) needs to be checked if it was -ve it meant ask and if +ve it meant bid. We need to clean and perform these operation as ameasure to clean the data

# BitStamp(API):
BitStamp is pretty prompt in sending data. Unlike Bitfinex, the data is not continous. With each request, we are getting around 30,000 data points. For the sake of simplicity, we are running this api only one time. However, what we can do is to make this call to API after every minute, and store the reponse in the Database. Again the data is in JSON. We performed JSON Parsing. 

# BitcoinAverage (API)
We are storing the previous 28 hours(1680 minutes) of bitcoin prices in USD in the DB. Based on this data, we will predict if the user should buy or sell bitcoins. If the trend is decreasing, the user must buy bitcoins, otherwise sell bitcoins. The trend changes every minute, as it appends rows to the database. The data collected has 2 parameters – the time and the average price of Bitcoin (USD) for that minute. Using this data, we will plot a graph, showing the trend of the average price of Bitcoin (USD) v/s the time and recommend if the user should sell or buy.
 
# CurrencyConvertor (Webscraping)
Our program support currency conversion based on current market rates from x-rates.com. This data is pretty much the same during the day, and hence we don’t update it every second.  Based on the amount entered by the user in a particular currency, the amount is converted to the corresponding amount in USD. We scrape two values from the same, the country and its corresponding factor.
