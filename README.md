# Predictive Investments

A modular FastAPI application to fetch and analyze financial data from multiple sources including Polygon.io and Finviz.

## Features

- **Stocks Data**: Fetch OHLC data, company details, and news for any stock ticker
- **Options Data**: Retrieve information about options contracts and their historical prices
- **Indices Data**: Get data for major market indices
- **Stock Screening**: Filter stocks based on various fundamental and technical criteria using Finviz

## Project Structure

```
api/
├── __init__.py
├── main.py                # Application entry point
├── dependencies.py        # FastAPI dependencies
├── routes/                # API route definitions
│   ├── __init__.py
│   ├── finviz.py          # Stock screening endpoints
│   ├── indices.py         # Market indices endpoints
│   ├── options.py         # Options data endpoints
│   └── stock.py           # Stock data endpoints
├── models/                # Pydantic data models
│   ├── __init__.py
│   ├── enums.py           # Enum definitions
│   ├── finviz.py          # Stock screening models
│   ├── options.py         # Options data models
│   ├── stocks.py          # Stock data models
│   └── tickers.py         # Ticker listing models
├── services/              # Business logic and external API clients
│   ├── __init__.py
│   ├── finviz.py          # Finviz scraping service
│   └── polygon.py         # Polygon.io API client
├── middleware/            # Custom middleware
│   ├── __init__.py
│   └── rate_limiter.py    # Polygon API rate limiter
└── core/                  # Core application components
    ├── __init__.py
    ├── config.py          # Application configuration
    └── exceptions.py      # Custom exceptions
```

## Setup

### Prerequisites

- Python 3.9+
- Polygon.io API key (sign up at [polygon.io](https://polygon.io))

### Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd financial-data-api
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your Polygon.io API key:
   ```
   POLYGON_API_KEY=your_polygon_api_key_here
   ```

### Running the API

Start the API with hot-reloading enabled:

```bash
uvicorn api.main:app --reload
```

The API will be available at:

- API endpoints: http://localhost:8000/api/v1/
- API documentation: http://localhost:8000/docs
- Alternative documentation: http://localhost:8000/redoc

## API Endpoints

### Stocks

- `GET /api/v1/stocks/{ticker}/ohlc/{multiplier}/{timespan}/{from_date}/{to_date}` - Get historical OHLC data for a stock
- `GET /api/v1/stocks/{ticker}/details` - Get detailed information about a stock
- `GET /api/v1/stocks/news` - Get news articles related to stocks

### Options

- `GET /api/v1/options/contracts` - List options contracts with various filters
- `GET /api/v1/options/{options_ticker}/ohlc/{multiplier}/{timespan}/{from_date}/{to_date}` - Get OHLC data for an options contract

### Indices

- `GET /api/v1/indices` - List all available indices
- `GET /api/v1/indices/{indices_ticker}/ohlc/{multiplier}/{timespan}/{from_date}/{to_date}` - Get OHLC data for an index

### Stock Screening

- `POST /api/v1/stocks/screener` - Get stock tickers based on specified filters
- `GET /api/v1/stocks/filters` - Get all available filters for the screener
- `POST /api/v1/stocks/options` - Get available options for specified filters

## Rate Limiting

The API includes a rate limiter middleware for Polygon.io endpoints that limits requests to 5 per minute to comply with their free tier limits.

## Development

### Adding New Endpoints

To add a new endpoint:

1. Define models in the appropriate file in the `models` directory
2. Add the necessary service methods in the `services` directory
3. Create a new route handler in the `routes` directory
4. Register the route in `api/routes/__init__.py`

## License

[MIT License](LICENSE)
