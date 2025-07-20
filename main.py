import data_model

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
                    if ticker not in stock_scores:
                        stock_scores[ticker] = 0
                    stock_scores[ticker] += score

            # Sort stocks by their total score in descending order
            top_stocks = sorted(stock_scores.items(), key=lambda item: item[1], reverse=True)[:3]
            selected_stocks[date] = [ticker for ticker, _ in top_stocks]

        return selected_stocks


    def portfolio_allocation(self):
        pass

if __name__ == "__main__":
    PrimeModel = PrimeModel(data_model.load_stock_data())
    print(PrimeModel.select_stocks())
    
