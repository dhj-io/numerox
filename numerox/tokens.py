import datetime
import requests

import pandas as pd

import numerox as nx


def nmr_at_addr(addr_str):
    "Number of NMR (float) at given address."
    url = 'https://api.etherscan.io/api?module=account&action=tokenbalance&'
    url += 'contractaddress=0x1776e1F26f98b1A5dF9cD347953a26dd3Cb46671&'
    url += 'address=%s'
    r = requests.get(url % addr_str)
    data = r.json()
    nmr = int(data['result']) / 1e18
    return nmr


def token_price_data(ticker='nmr'):
    "Most recent price (and return) data for given ticker; returns dictionary."
    tickers = {'nmr': 'numeraire',
               'btc': 'bitcoin',
               'eth': 'ethereum',
               'ltc': 'litecoin'}
    if ticker in tickers:
        ticker = tickers[ticker]
    url = 'https://api.coinmarketcap.com/v1/ticker/%s/' % ticker
    r = requests.get(url)
    data = r.json()[0]
    price = {}
    price['name'] = ticker
    price['price'] = float(data['price_usd'])
    price['ret1h'] = float(data['percent_change_1h']) / 100.0
    price['ret1d'] = float(data['percent_change_24h']) / 100.0
    price['ret7d'] = float(data['percent_change_7d']) / 100.0
    price['date'] = datetime.datetime.fromtimestamp(int(data['last_updated']))
    return price


def historical_price(ticker, one_per_day=False):
    "Historical prices as a dataframe with date as index"
    tickers = {'nmr': 'currencies/numeraire',
               'btc': 'currencies/bitcoin',
               'eth': 'currencies/ethereum',
               'ltc': 'currencies/litecoin',
               'mkt': 'global/marketcap-total'}
    url = 'https://graphs2.coinmarketcap.com/%s'
    r = requests.get(url % tickers[ticker])
    data = r.json()
    if ticker == 'mkt':
        data = data['market_cap_by_available_supply']
    else:
        data = data['price_usd']
    dates = []
    prices = []
    for date, price in data:
        d = datetime.datetime.fromtimestamp(date / 1e3)
        if one_per_day:
            d = d.date()
        dates.append(d)
        prices.append(price)
    if one_per_day:
        p = []
        d = []
        for i in range(len(prices) - 1):
            d1 = dates[i]
            d2 = dates[i+1]
            if d1 != d2:
                p.append(prices[i])
                d.append(d1)
        if dates[-1] != d[-1]:
            p.append(prices[-1])
            d.append(dates[-1])
        prices = p
        dates = d
    prices = pd.DataFrame(data=prices, columns=['usd'], index=dates)
    return prices


def nmr_resolution_price(tournament=1):
    "Price of NMR in USD and date versus round number as a dataframe."
    price = nx.historical_price('nmr', one_per_day=True)
    dates = nx.round_resolution_date(tournament=tournament)
    price = pd.merge(dates, price, how='inner', left_on='date',
                     right_index=True)
    return price
