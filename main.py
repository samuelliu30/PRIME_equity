import data_model
import data_utils
from datetime import datetime
import matplotlib.pyplot as plt
import csv


class PrimeModel:
    def __init__(self, data: dict):
        self.data = data

    def rank_stocks(self):
        ranked_stocks_by_date = {}
        for date in self.data:
            ranked_stocks = {}
            for metric in ['reportedEPS', 'pe_ratio', 'quarterly_return_six_month', 'quarterly_return_one_year', 'yoy_return']:
                if metric == 'pe_ratio':
                    # Sort the stocks based on pe_ratio in ascending order
                    ranked_stocks[metric] = sorted(self.data[date].items(), key=lambda item: (item[1][metric] == 0, item[1][metric]))
                else:
                    # Sort the stocks based on the current metric in descending order
                    ranked_stocks[metric] = sorted(self.data[date].items(), key=lambda item: item[1][metric], reverse=True)
            ranked_stocks_by_date[date] = ranked_stocks

        '''
        # Print or store the ranked stocks for each date
        for date, ranked_stocks in ranked_stocks_by_date.items():
            print(f"Date: {date}")
            for metric, rankings in ranked_stocks.items():
                print(f"Rankings for {metric}:")
                for rank, (ticker, data) in enumerate(rankings, start=1):
                    print(f"{rank}. {ticker}: {data[metric]}")
        '''

        return ranked_stocks_by_date

    def select_stocks(self):
        selected_stocks = {}
        ranked_stocks_by_date = self.rank_stocks()
        for date, ranked_stocks in ranked_stocks_by_date.items():
            stock_scores = {}
            for metric, rankings in ranked_stocks.items():
                num_stocks = len(rankings)
                for rank, (ticker, _) in enumerate(rankings, start=1):
                    score = num_stocks - rank + 1  # First place gets the highest score
                    if metric in ['pe_ratio', 'yoy_return']:
                        score /= 2  # Cut the score in half for 'pe_ratio' and 'yoy_return'
                    if ticker not in stock_scores:
                        stock_scores[ticker] = 0
                    stock_scores[ticker] += score

            # Sort stocks by their total score in descending order
            top_stocks = sorted(stock_scores.items(), key=lambda item: item[1], reverse=True)[:3]
            selected_stocks[date] = [ticker for ticker, _ in top_stocks]

        return selected_stocks

    def portfolio_allocation(self):
        pass

    def calculate_portfolio_return(self, selected_stocks: dict):
        previous_quarter_stocks = {}
        for date in selected_stocks:
            # Calculate the previous quarter
            year, quarter = map(int, date.split('_q'))
            if year < 2013:
                continue  # Skip any data before 2013
            if quarter == 1:
                previous_quarter = f"{year - 1}_q4"
            else:
                previous_quarter = f"{year}_q{quarter - 1}"
            
            # Get the selected stocks from the previous quarter
            if previous_quarter in selected_stocks:
                previous_quarter_stocks[date] = selected_stocks[previous_quarter]
            else:
                previous_quarter_stocks[date] = []

        portfolio_return = {}
        for date, stocks in previous_quarter_stocks.items():
            total_compounded_return = 0
            for stock in stocks:
                # Convert the quarter date to a real date
                year, quarter = map(int, date.split('_q'))
                if quarter == 1:
                    start_date = datetime(year, 1, 31)
                elif quarter == 2:
                    start_date = datetime(year, 4, 30)
                elif quarter == 3:
                    start_date = datetime(year, 7, 31)
                else:
                    start_date = datetime(year, 10, 31)
                
                # Calculate the compounded return for each stock
                compounded_return_df = data_utils.quarterly_return(stock, start_date, 90)  # Assuming 1 quarter
                compounded_return = float(compounded_return_df.iloc[0, 0])  # Get the value of Compounded Return
                total_compounded_return += compounded_return
            
            # Store the total compounded return for the portfolio in the dictionary
            portfolio_return[date] = total_compounded_return

        return portfolio_return

def plot_portfolio_return(portfolio_return: dict):
    plt.figure(figsize=(10, 6))
    plt.plot(portfolio_return.keys(), portfolio_return.values(), label='Portfolio Return')
    plt.xlabel('Date')
    plt.ylabel('Return')
    plt.title('Portfolio Return')
    plt.legend()

def visualize_portfolio(selected_stocks: dict):
    # Export the selected stocks dictionary to a CSV file
    with open('selected_stocks.csv', 'w', newline='') as csvfile:
        fieldnames = ['Date', 'Stocks']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        def custom_sort_key(item):
            year, quarter = item[0].split('_q')
            return year * 10 + quarter

        sorted_selected_stocks = dict(sorted(selected_stocks.items(), key=custom_sort_key, reverse=True))
        for date, stocks in sorted_selected_stocks.items():
            year, _ = map(int, date.split('_q'))
            if year >= 2013:
                writer.writerow({'Date': date, 'Stocks': ', '.join(stocks)})

if __name__ == "__main__":
    PrimeModel = PrimeModel(data_model.load_stock_data())
    selected_stocks = PrimeModel.select_stocks()
    portfolio_return = PrimeModel.calculate_portfolio_return(selected_stocks)
    visualize_portfolio(selected_stocks)
    #plot_portfolio_return(portfolio_return)
    #plt.show()
