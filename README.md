# PRIME_equity
Passive Return Index with Multi-factor Exposure

## Setup

### Prerequisites

This project requires an Alpha Vantage API key to fetch stock market data. You can obtain a free API key by:

1. Visiting [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Signing up for a free account
3. Getting your API key from the dashboard

### Environment Configuration

1. Create a `.env` file in the root directory of this project
2. Add your Alpha Vantage API key to the file:

```bash
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

**Note:** The `.env` file is already included in `.gitignore` to prevent accidentally committing your API key to version control.

## Usage

### Configuration

#### 1. Stock Ticker Configuration

To customize the list of stocks analyzed by the model, edit the `stock_list` variable in `data_model.py`:

```python
# In data_model.py, line 8
stock_list = ["NVDA", "AMD", "AVGO", "MRVL", "ADSK", "QCOM", "MU", "ASML"]
```

You can add or remove ticker symbols as needed. The model will automatically fetch data for all tickers in this list.

#### 2. Selection Rules Configuration

The PrimeModel uses a multi-factor ranking system to select the top 3 stocks for each quarter. The current selection criteria include:

- **reportedEPS**: Earnings per share (higher is better)
- **pe_ratio**: Price-to-earnings ratio (lower is better)
- **quarterly_return_six_month**: 6-month quarterly return (higher is better)
- **quarterly_return_one_year**: 1-year quarterly return (higher is better)
- **yoy_return**: Year-over-year return (higher is better)

To modify the selection rules, edit the `rank_stocks()` method in `main.py`:

```python
# In main.py, line 8
for metric in ['reportedEPS', 'pe_ratio', 'quarterly_return_six_month', 'quarterly_return_one_year', 'yoy_return']:
```

You can:
- Add new metrics by including them in this list
- Remove metrics by excluding them
- Change the ranking logic for specific metrics

### Running the Model

1. **First Run**: The model will fetch data from Alpha Vantage API and cache it locally
   ```bash
   python main.py
   ```

2. **Subsequent Runs**: The model will use cached data for faster execution
   ```bash
   python main.py
   ```

### Output

The model outputs a dictionary where:
- Keys are quarterly dates (format: `YYYY_qQ`)
- Values are lists of the top 3 selected ticker symbols for that quarter

Example output:
```python
{
    '2023_q1': ['NVDA', 'AMD', 'AVGO'],
    '2023_q2': ['AMD', 'NVDA', 'MRVL'],
    '2023_q3': ['NVDA', 'AVGO', 'AMD']
}
```

### Data Sources

The model fetches the following data for each ticker:
- Earnings per share (EPS) data
- Price-to-earnings ratios
- Quarterly returns (6-month and 1-year periods)
- Year-over-year returns

All data is sourced from Alpha Vantage API and cached locally in the `cache/` directory for performance.
