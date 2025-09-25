import pandas as pd
file_path = '/Users/ravicorrie/Downloads/stock_data.csv'

df = pd.read_csv(file_path)

df = df[df["ticker"] != "NAN"]
df.to_csv('/Users/ravicorrie/Downloads/final_stock_data.csv')
