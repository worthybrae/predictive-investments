# API Usage Examples

This document provides practical examples of how to use the Financial Data API endpoints.

## Table of Contents

- [Stock Data](#stock-data)
- [Options Data](#options-data)
- [Indices Data](#indices-data)
- [Stock Screening](#stock-screening)

## Stock Data

### Get Historical OHLC Data for a Stock

**Request:**

```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/stocks/AAPL/ohlc/1/day/2023-01-01/2023-02-01' \
  -H 'accept: application/json'
```

**Python Example:**

```python
import requests

url = "http://localhost:8000/api/v1/stocks/AAPL/ohlc/1/day/2023-01-01/2023-02-01"
response = requests.get(url)
data = response.json()

# Print the first data point
print(data["results"][0])
```

### Get Stock Details

**Request:**

```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/stocks/TSLA/details' \
  -H 'accept: application/json'
```

**Python Example:**

```python
import requests

url = "http://localhost:8000/api/v1/stocks/TSLA/details"
response = requests.get(url)
data = response.json()

# Print company name and market cap
print(f"Company: {data['results']['name']}")
print(f"Market Cap: ${data['results']['market_cap']:,.2f}")
```

### Get Recent Stock News

**Request:**

```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/stocks/news?ticker=NVDA&limit=5' \
  -H 'accept: application/json'
```

**Python Example:**

```python
import requests

url = "http://localhost:8000/api/v1/stocks/news"
params = {
    "ticker": "NVDA",
    "limit": 5
}
response = requests.get(url, params=params)
data = response.json()

# Print news titles
for article in data["results"]:
    print(f"- {article['title']}")
```

## Options Data

### List Options Contracts

**Request:**

```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/options/contracts?underlying_ticker=SPY&contract_type=call&limit=5' \
  -H 'accept: application/json'
```

**Python Example:**

```python
import requests

url = "http://localhost:8000/api/v1/options/contracts"
params = {
    "underlying_ticker": "SPY",
    "contract_type": "call",
    "limit": 5
}
response = requests.get(url, params=params)
data = response.json()

# Print contract info
for contract in data["results"]:
    print(f"Ticker: {contract['ticker']}, Strike: ${contract['strike_price']}, Expires: {contract['expiration_date']}")
```

### Get Options OHLC Data

**Request:**

```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/options/O:SPY230317C00400000/ohlc/1/day/2023-01-01/2023-02-01' \
  -H 'accept: application/json'
```

**Python Example:**

```python
import requests

url = "http://localhost:8000/api/v1/options/O:SPY230317C00400000/ohlc/1/day/2023-01-01/2023-02-01"
response = requests.get(url)
data = response.json()

# Print the closing prices
for candle in data["results"]:
    # Convert timestamp to date
    from datetime import datetime
    date = datetime.fromtimestamp(candle["t"] / 1000).strftime('%Y-%m-%d')
    print(f"Date: {date}, Close: ${candle['c']}")
```

## Indices Data

### List Available Indices

**Request:**

```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/indices?limit=10' \
  -H 'accept: application/json'
```

**Python Example:**

```python
import requests

url = "http://localhost:8000/api/v1/indices"
params = {
    "limit": 10
}
response = requests.get(url, params=params)
data = response.json()

# Print indices
for index in data["results"]:
    print(f"{index['ticker']}: {index['name']}")
```

### Get Index OHLC Data

**Request:**

```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/indices/I:SPX/ohlc/1/day/2023-01-01/2023-02-01' \
  -H 'accept: application/json'
```

**Python Example:**

```python
import requests

url = "http://localhost:8000/api/v1/indices/I:SPX/ohlc/1/day/2023-01-01/2023-02-01"
response = requests.get(url)
data = response.json()

# Calculate the percent change over the period
first_close = data["results"][0]["c"]
last_close = data["results"][-1]["c"]
percent_change = ((last_close - first_close) / first_close) * 100

print(f"S&P 500 changed {percent_change:.2f}% over the period")
```

## Stock Screening

### Get Available Filters

**Request:**

```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/stocks/filters' \
  -H 'accept: application/json'
```

**Python Example:**

```python
import requests

url = "http://localhost:8000/api/v1/stocks/filters"
response = requests.get(url)
data = response.json()

# Print available filters
print(f"Available filters: {data['count']}")
for filter_name, filter_info in data["filters"].items():
    print(f"- {filter_name}: {filter_info['title']}")
```

### Get Filter Options

**Request:**

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/stocks/options' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"filters": ["sector", "index"]}'
```

**Python Example:**

```python
import requests

url = "http://localhost:8000/api/v1/stocks/options"
payload = {
    "filters": ["sector", "index"]
}
response = requests.post(url, json=payload)
data = response.json()

# Print options for the "sector" filter
sector_filter = data["filters"]["sector"]
print(f"Options for {sector_filter['title']}:")
for option_id, option_name in sector_filter["options"].items():
    print(f"- {option_name} ({option_id})")
```

### Run Stock Screener

**Request:**

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/stocks/screener' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"filters": {"index": "idx_sp500", "sector": "sec_technology", "marketcap": "mega"}}'
```

**Python Example:**

```python
import requests

url = "http://localhost:8000/api/v1/stocks/screener"
payload = {
    "filters": {
        "index": "idx_sp500",
        "sector": "sec_technology",
        "marketcap": "marketcap_mega"
    }
}
response = requests.post(url, json=payload)
data = response.json()

print(f"Found {data['count']} stocks matching criteria:")
for ticker in data["results"]:
    print(f"- {ticker}")
```

## Advanced Examples

### Create a Simple Moving Average Chart

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Get daily AAPL data for the past year
url = "http://localhost:8000/api/v1/stocks/AAPL/ohlc/1/day/2023-01-01/2023-12-31"
response = requests.get(url)
data = response.json()

# Convert to DataFrame
df = pd.DataFrame(data["results"])
df["date"] = pd.to_datetime(df["t"], unit="ms")
df.set_index("date", inplace=True)

# Calculate 20-day and 50-day SMAs
df["sma20"] = df["c"].rolling(window=20).mean()
df["sma50"] = df["c"].rolling(window=50).mean()

# Plot
plt.figure(figsize=(12, 6))
plt.plot(df.index, df["c"], label="AAPL Close Price")
plt.plot(df.index, df["sma20"], label="20-day SMA", linestyle="--")
plt.plot(df.index, df["sma50"], label="50-day SMA", linestyle="-.")
plt.title("AAPL Price with Simple Moving Averages")
plt.xlabel("Date")
plt.ylabel("Price ($)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
```

### Compare Multiple Stock Returns

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Function to get stock data and calculate returns
def get_returns(ticker, start_date, end_date):
    url = f"http://localhost:8000/api/v1/stocks/{ticker}/ohlc/1/day/{start_date}/{end_date}"
    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame(data["results"])
    df["date"] = pd.to_datetime(df["t"], unit="ms")
    df.set_index("date", inplace=True)
    df.sort_index(inplace=True)

    # Calculate returns
    df["return"] = df["c"] / df["c"].iloc[0] - 1

    return df["return"]

# Get returns for multiple stocks
start_date = "2023-01-01"
end_date = "2023-12-31"
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]

returns_df = pd.DataFrame()

for ticker in tickers:
    returns_df[ticker] = get_returns(ticker, start_date, end_date)

# Plot returns
plt.figure(figsize=(12, 8))
for ticker in tickers:
    plt.plot(returns_df.index, returns_df[ticker] * 100, label=ticker)

plt.title("Comparison of Stock Returns")
plt.xlabel("Date")
plt.ylabel("Return (%)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
```
