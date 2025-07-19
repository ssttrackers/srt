import csv
import datetime
import yfinance as yf
import pandas as pd
import tempfile
import pygsheets
from urllib.request import urlopen
import json
import ta

url = "https://raw.githubusercontent.com/satyendrasarat/json-creds/main/creds.json"

# store the response of URL
response1 = urlopen(url)
response = json.loads(response1.read())


def _google_creds_as_file():
    temp = tempfile.NamedTemporaryFile()
    temp.write(json.dumps(response).encode('utf-8'))
    temp.flush()
    return temp


creds_file = _google_creds_as_file()
gc = pygsheets.authorize(service_account_file=creds_file.name)
sh = gc.open('SRTbk1')

#select the first sheet
wks = sh[0]


def get_stock_data(symbol, start_date, end_date):
    stock_data = yf.download(symbol + ".NS", start=start_date, end=end_date)
    return stock_data


def get_ltp_and_dma(ticker, start_date, end_date, dma_periods):
    stock_data = get_stock_data(ticker, start_date, end_date)

    dma_columns = [f"{period}DMA" for period in dma_periods]
    df = pd.DataFrame(index=stock_data.index)
    df['LTP'] = stock_data['Close']

    for period in dma_periods:
        df[f"{period}DMA"] = df['LTP'].rolling(window=period).mean()

    return df


def evaluate_strategy(df, stock_name):
    buy_price = None
    sell_price = None
    in_observation = False
    trades = []

    for i in range(len(df)):
        date = df.index[i]
        rsi = df.iloc[i]['rsi']
        ratio = df.iloc[i]['Ratio']
        ltp = df.iloc[i]['LTP']

        if not in_observation:
            if rsi < 30 and ratio < 0.7:
                in_observation = True

        if in_observation:
            if rsi > 40:
                if buy_price is None:
                    buy_price = ltp
                    trades.append({
                        "Stock": stock_name,
                        "Date": date,
                        "Action": "Buy",
                        "Price": buy_price,
                        "RSI": rsi,
                        "Ratio": ratio
                    })
                    in_observation = False

        if ratio > 1.3 or rsi > 73:
            if buy_price is not None and sell_price is None:
                sell_price = ltp
                trades.append({
                    "Stock": stock_name,
                    "Date": date,
                    "Action": "Sell",
                    "Price": sell_price,
                    "RSI": rsi,
                    "Ratio": ratio
                })
                trades.append({
                    "Stock": stock_name,
                    "Date": date,
                    "Action": "Profit/Loss",
                    "Price": (sell_price - buy_price),
                    "RSI": rsi,
                    "Ratio": ratio
                })
                buy_price = None
                sell_price = None
                in_observation = False

    return trades


# List of stocks
stocks = [
    'ABB', 'ACC', 'AUBANK', 'ABBOTINDIA', 'ADANIENT', 'ADANIGREEN',
    'ADANIPORTS', 'ADANIPOWER', 'ATGL', 'ADANITRANS', 'AWL', 'ABCAPITAL',
    'ABFRL', 'ALKEM', 'AMBUJACEM', 'APOLLOHOSP', 'APOLLOTYRE', 'ASHOKLEY',
    'ASIANPAINT', 'ASTRAL', 'AUROPHARMA', 'DMART', 'AXISBANK', 'BAJAJ-AUTO',
    'BAJFINANCE', 'BAJAJFINSV', 'BAJAJHLDNG', 'BALKRISIND', 'BANDHANBNK',
    'BANKBARODA', 'BANKINDIA', 'BATAINDIA', 'BERGEPAINT', 'BEL', 'BHARATFORG',
    'BHEL', 'BPCL', 'BHARTIARTL', 'BIOCON', 'BOSCHLTD', 'BRITANNIA', 'CGPOWER',
    'CANBK', 'CHOLAFIN', 'CIPLA', 'COALINDIA', 'COFORGE', 'COLPAL', 'CONCOR',
    'COROMANDEL', 'CROMPTON', 'CUMMINSIND', 'DLF', 'DABUR', 'DALBHARAT',
    'DEEPAKNTR', 'DELHIVERY', 'DEVYANI', 'DIVISLAB', 'DIXON', 'LALPATHLAB',
    'DRREDDY', 'EICHERMOT', 'ESCORTS', 'NYKAA', 'FEDERALBNK', 'FORTIS', 'GAIL',
    'GLAND', 'GODREJCP', 'GODREJPROP', 'GRASIM', 'FLUOROCHEM', 'GUJGASLTD',
    'HCLTECH', 'HDFCAMC', 'HDFCBANK', 'HDFCLIFE', 'HAVELLS', 'HEROMOTOCO',
    'HINDALCO', 'HAL', 'HINDPETRO', 'HINDUNILVR', 'HINDZINC', 'HONAUT', 'HDFC',
    'ICICIBANK', 'ICICIGI', 'ICICIPRULI', 'IDFCFIRSTB', 'ITC', 'INDIANB',
    'INDHOTEL', 'IOC', 'IRCTC', 'IRFC', 'IGL', 'INDUSTOWER', 'INDUSINDBK',
    'NAUKRI', 'INFY', 'INDIGO', 'IPCALAB', 'JSWENERGY', 'JSWSTEEL',
    'JINDALSTEL', 'JUBLFOOD', 'KOTAKBANK', 'L&TFH', 'LTTS', 'LICHSGFIN',
    'LTIM', 'LT', 'LAURUSLABS', 'LICI', 'LUPIN', 'MRF', 'M&MFIN', 'M&M',
    'MARICO', 'MARUTI', 'MFSL', 'MAXHEALTH', 'MSUMI', 'MPHASIS', 'MUTHOOTFIN',
    'NHPC', 'NMDC', 'NTPC', 'NAVINFLUOR', 'NESTLEIND', 'OBEROIRLTY', 'ONGC',
    'OIL', 'PAYTM', 'OFSS', 'POLICYBZR', 'PIIND', 'PAGEIND', 'PATANJALI',
    'PERSISTENT', 'PETRONET', 'PIDILITIND', 'PEL', 'POLYCAB', 'POONAWALLA',
    'PFC', 'POWERGRID', 'PRESTIGE', 'PGHH', 'PNB', 'RECLTD', 'RELIANCE',
    'SBICARD', 'SBILIFE', 'SRF', 'MOTHERSON', 'SHREECEM', 'SHRIRAMFIN',
    'SIEMENS', 'SONACOMS', 'SBIN', 'SAIL', 'SUNPHARMA', 'SUNTV', 'SYNGENE',
    'TVSMOTOR', 'TATACHEM', 'TATACOMM', 'TCS', 'TATACONSUM', 'TATAELXSI',
    'TATAMOTORS', 'TATAPOWER', 'TATASTEEL', 'TTML', 'TECHM', 'RAMCOCEM',
    'TITAN', 'TORNTPHARM', 'TORNTPOWER', 'TRENT', 'TRIDENT', 'TIINDIA', 'UPL',
    'ULTRACEMCO', 'UNIONBANK', 'UBL', 'MCDOWELL-N', 'VBL', 'VEDL', 'IDEA',
    'VOLTAS', 'WHIRLPOOL', 'WIPRO', 'YESBANK', 'ZEEL', 'ZOMATO', 'ZYDUSLIFE'
]
# Example usage
start_date = "2018-10-22"  # Start date of the date range
end_date = datetime.datetime.today().strftime('%Y-%m-%d')  # End date as today
dma_periods = [200, 50, 20, 124]  # List of DMA periods

# Data container for all stocks
all_data = []

# Iterate over stocks and collect data
for stock in stocks:
    # Fetch historical data and calculate indicators
    ltp_and_dma_table = get_ltp_and_dma(stock, start_date, end_date,
                                        dma_periods)
    ltp_and_dma_table['rsi'] = ta.momentum.RSIIndicator(
        ltp_and_dma_table['LTP']).rsi()
    ltp_and_dma_table[
        'Ratio'] = ltp_and_dma_table['LTP'] / ltp_and_dma_table['124DMA']

    # Evaluate the strategy and get the trades for the current stock
    trades = evaluate_strategy(ltp_and_dma_table, stock)

    # Append the trades to the combined data container
    all_data.append((stock, trades))

# Combine all trade data into a single DataFrame
combined_trades = pd.concat([pd.DataFrame(trades) for _, trades in all_data],
                            keys=stocks)

# Print the combined trade data
print(combined_trades)
wks.set_dataframe(combined_trades, start='A2')
#run