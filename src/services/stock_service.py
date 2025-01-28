from src.utils.data_loader import get_stock_data, clean_stock_data
from src.utils.indicators import is_near_high

class StockService:
    def __init__(self):
        self.period_options = {
            "1mo": "1 Month",
            "3mo": "3 Months",
            "6mo": "6 Months",
            "1y": "1 Year"
        }

    def get_stock_info(self, symbol, period):
        try:
            data = get_stock_data(symbol, period=period)
            if data.empty:
                return None
                
            data = clean_stock_data(data)
            if data.empty:
                return None
            
            _, diff_percent, period_high = is_near_high(data)
                
            return {
                'symbol': symbol,
                'data': data,
                'current_price': data['Close'].iloc[-1],
                'period_high': period_high,
                'period_low': data['Low'].min(),
                'average_volume': data['Volume'].mean(),
                'diff_percent': diff_percent
            }
        except Exception:
            return None

    def get_filtered_stocks(self, symbols, period, threshold):
        filtered_results = []
        for symbol in symbols:
            try:
                data = get_stock_data(symbol, period=period)
                if not data.empty:
                    data = clean_stock_data(data)
                    if not data.empty:
                        is_near, diff_percent, period_high = is_near_high(data, threshold)
                        if is_near:
                            filtered_results.append({
                                'symbol': symbol,
                                'data': data,
                                'current_price': data['Close'].iloc[-1],
                                'period_high': period_high,
                                'period_low': data['Low'].min(),
                                'average_volume': data['Volume'].mean(),
                                'diff_percent': diff_percent
                            })
            except Exception:
                continue
        return filtered_results

    def calculate_technical_indicators(self, data, rsi_period=14, ema_period=20):
        # Calculate RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Calculate EMA
        ema = data['Close'].ewm(span=ema_period, adjust=False).mean()
        
        return rsi.iloc[-1], ema.iloc[-1]

    def get_period_data(self, symbol, periods=None):
        if periods is None:
            periods = ['1mo', '3mo', '6mo', '1y']
            
        period_data = {}
        for period in periods:
            try:
                data = get_stock_data(symbol, period=period)
                if not data.empty:
                    data = clean_stock_data(data)
                    period_data[period] = {
                        'high': data['High'].max(),
                        'low': data['Low'].min()
                    }
            except Exception:
                period_data[period] = None
        return period_data 