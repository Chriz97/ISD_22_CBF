import yfinance as yf
import pandas as pd

msft = yf.Ticker("MSFT")

x = msft.get_balancesheet()

y = pd.DataFrame(data=x)

y.to_excel("dictionary.xlsx")