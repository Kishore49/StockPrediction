from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import yfinance as yf

app = Flask(__name__)

load_dotenv()

STOCKS = [
    'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'JNJ', 'V',
    'WMT', 'PG', 'XOM', 'BAC', 'DIS', 'NFLX', 'CSCO', 'INTC', 'VZ', 'KO',
    'PFE', 'MRK', 'T', 'CVX', 'PEP', 'MCD', 'HD', 'IBM', 'NKE', 'ORCL',
    'ADBE', 'CRM', 'PYPL', 'CMCSA', 'ABT', 'ACN', 'QCOM', 'TXN', 'LLY', 'AVGO',
    'COST', 'DHR', 'NEE', 'WFC', 'MDT', 'UNH', 'HON', 'LIN', 'ABBV', 'AMGN',
    'BABA', 'BIDU', 'SPOT', 'SQ', 'ZM', 'ROKU', 'SHOP', 'UBER', 'LYFT', 'SNAP',
    'TWTR', 'BMY', 'GILD', 'CVS', 'WBA', 'SBUX', 'LMT', 'BA', 'CAT', 'MMM',
    'GS', 'MS', 'C', 'TGT', 'LOW', 'GE', 'GM', 'F', 'RIVN', 'LCID'
]

def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        return {
            'Symbol': symbol,
            'Name': info.get('longName', 'N/A'),
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'Price': info.get('currentPrice', 'N/A'),
            '52WeekHigh': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52WeekLow': info.get('fiftyTwoWeekLow', 'N/A'),
            'PERatio': info.get('trailingPE', 'N/A'),
            'ForwardPE': info.get('forwardPE', 'N/A'),
            'DividendYield': info.get('dividendYield', 'N/A'),
            'MarketCap': info.get('marketCap', 'N/A'),
            'EPS': info.get('trailingEps', 'N/A'),
            'Beta': info.get('beta', 'N/A'),
            'BookValue': info.get('bookValue', 'N/A'),
            'PriceToBook': info.get('priceToBook', 'N/A')
        }
    except Exception as e:
        return {
            'Symbol': symbol,
            'Error': f"Error fetching data for {symbol}: {str(e)}"
        }

def analyze_stock(data):
    if 'Error' in data:
        return [data['Error']]
    
    analysis = []
    
    pe_ratio = data['PERatio']
    if pe_ratio != 'N/A':
        pe_ratio = float(pe_ratio)
        if pe_ratio < 15:
            analysis.append("The stock has a low P/E ratio, which might indicate it's undervalued.")
        elif pe_ratio > 30:
            analysis.append("The stock has a high P/E ratio, which might indicate it's overvalued.")
        else:
            analysis.append("The P/E ratio is in a moderate range.")
    
    dividend_yield = data['DividendYield']
    if dividend_yield != 'N/A':
        dividend_yield = float(dividend_yield)
        if dividend_yield > 0.04:
            analysis.append("The stock has a high dividend yield, which could be attractive for income investors.")
        elif dividend_yield > 0:
            analysis.append("The stock pays a dividend, which might be of interest to income-focused investors.")
        else:
            analysis.append("The stock does not currently pay a dividend.")
    
    price_to_book = data['PriceToBook']
    if price_to_book != 'N/A':
        price_to_book = float(price_to_book)
        if price_to_book < 1:
            analysis.append("The stock is trading below its book value, which might indicate it's undervalued.")
        elif price_to_book > 3:
            analysis.append("The stock has a high price-to-book ratio, which might indicate it's overvalued.")
        else:
            analysis.append("The price-to-book ratio is in a moderate range.")
    
    if not analysis:
        analysis.append("Insufficient data to provide a meaningful analysis.")
    
    return analysis

@app.route('/', methods=['GET', 'POST'])
def index():
    selected = 'AAPL'  # Default stock selection
    data = get_stock_data(selected)
    analysis = analyze_stock(data)
    
    if request.method == 'POST':
        symbol = request.form.get('stock')
        if symbol:
            selected = symbol
            data = get_stock_data(symbol)
            analysis = analyze_stock(data)
    
    return render_template('index.html', stocks=STOCKS, selected=selected, data=data, analysis=analysis)

@app.route('/explain/<metric>')
def explain_metric(metric):
    explanations = {
        'PERatio': "The Price-to-Earnings (P/E) ratio is a valuation metric that compares a company's stock price to its earnings per share. A lower P/E may indicate an undervalued stock, while a higher P/E might suggest overvaluation or high growth expectations.",
        'ForwardPE': "The Forward P/E ratio is based on projected future earnings. It provides insight into the company's expected performance and valuation.",
        'DividendYield': "Dividend Yield represents the annual dividend payment as a percentage of the stock price. A higher yield can be attractive for income-focused investors.",
        'MarketCap': "Market Capitalization is the total value of a company's outstanding shares. It's used to classify companies into large-cap, mid-cap, or small-cap categories.",
        'EPS': "Earnings Per Share (EPS) represents the company's profit allocated to each outstanding share of common stock. It's a key indicator of a company's profitability.",
        'Beta': "Beta measures a stock's volatility in relation to the overall market. A beta greater than 1 indicates higher volatility, while less than 1 suggests lower volatility.",
        'BookValue': "Book Value per Share represents the net asset value of a company divided by the number of outstanding shares. It's used to gauge whether a stock is undervalued or overvalued.",
        'PriceToBook': "The Price-to-Book ratio compares a company's market value to its book value. A lower ratio might indicate an undervalued stock, while a higher ratio could suggest overvaluation or a company with intangible assets."
    }
    return jsonify({'explanation': explanations.get(metric, "No explanation available.")})

if __name__ == '__main__':
    app.run(debug=True)
