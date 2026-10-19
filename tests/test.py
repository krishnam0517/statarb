import yfinance as yf
df = yf.download('AAPL', start='2025-01-01', end='2026-01-01')
print("AAPL Data Sample:")
print(df.head())