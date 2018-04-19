# BitTrust
To be your personal techno-intelligent bitcoin investment counsellor; to help you navigate the bitcoin market with ease!

BitcoinPredict (API)
When the user enters our web page, he will see the previous 28 hours(1680 minutes) of bitcoin prices in USD. It also shows the trend in the data, if it is increasing or decreasing.
Based on this data, we will predict if the user should buy or sell bitcoins.
If the trend is decreasing, the user must buy bitcoins, otherwise sell bitcoins.
It also gives the average bitcoin price for the past 28 hours
For this, we are using the API: BitcoinPredict https://apiv2.bitcoinaverage.com/
The trend changes every minute, as it appends rows to the database.
The data collected has 2 parameters – the time and the average price of Bitcoin (USD) for that minute.
Using this data, we will plot a graph, showing the trend of the average price of Bitcoin (USD) v/s the time and recommend if the user should sell or buy.

CurrencyConvertor (Webscraping)
We will perform currency conversion based on current market rates from https://www.x-rates.com/table/?from=USD&amount=1. This data is pretty much the same during the day, and hence we don’t update it every second. 
Based on the amount entered by the user in a particular currency, the amount is converted to the corresponding amount in USD.
We scrape two values from the same, the country and its corresponding factor.
If for Indian Rupee, the corresponding factor is 65.7, then we take our given amount and divide it by the factor, to convert from INR to USD.

Once the user enters the corresponding amount, its currency and ask/bid, we now use the below two API’s to display the max price at which the user should bid or the minimum price to ask for a bitcoin. We will also show the max number of bitcoin user can buy/sell for a particular amount (Multi-Currency Support). 
