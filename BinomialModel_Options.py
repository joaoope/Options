import math
import numpy as np
import pandas as pd

Vol = 0.23438        # Stock volatility
StockPrice = 100     # Initial stock price
Periods = 10         # Number of time periods
r = 0.1194           # Risk-free interest rate
T = 0.25             # Time to expiration (in years)
Div = 0              # Dividend yield
Strike = 100         # Option strike price
callput = 'c'        # 'c' for call option, 'p' for put option
type = 'American'    # Type of option (American or European)

# Define a function for the Binomial Option Pricing Model
def BinomialModel(S, T, Vol, Periods, r, d, strike, callput, type='European'):

    # Calculate up and down factors for the binomial model
    u = math.exp(Vol * np.sqrt(T / Periods))
    d = 1 / u
    q = (math.exp((r - Div) * T / Periods) - d) / (u - d)

    # Create empty DataFrames to store stock and option prices
    indexlist = list(range(Periods + 1))
    share_df = pd.DataFrame(index=indexlist[::-1], columns=indexlist)
    share_df.loc[0, 0] = S

    # Calculate stock prices at each node in the binomial tree
    for i in share_df.index[::-1]:
        for j in share_df.columns.tolist()[1:]:
            if i < j:
                share_df.loc[i, j] = d * share_df.loc[i, j - 1]
            elif i == j:
                share_df.loc[i, j] = u * share_df.loc[i - 1, j - 1]
            else:
                share_df.loc[i, j] = 0

    share_df = share_df.fillna(0)

    # Create a DataFrame to store option prices
    option_df = pd.DataFrame(index=indexlist[::-1], columns=indexlist)

    # Calculate option prices at expiration
    for i in option_df.index:
        if callput == 'c':
            option_df.loc[i, Periods] = max(1 * (share_df.loc[i, Periods] - Strike), 0)
        elif callput == 'p':
            option_df.loc[i, Periods] = max(-1 * (share_df.loc[i, Periods] - Strike), 0)
        else:
            raise ValueError('The variable callput must be either c or p')

    # Calculate option prices at earlier time steps using the binomial model
    for i in option_df.index:
        for j in option_df.columns.tolist()[:-1][::-1]:
            if (i <= j and type == 'European'):
                option_df.loc[i, j] = (q * (option_df.loc[i + 1, j + 1]) + ((1 - q) * (option_df.loc[i, j + 1]))) / (
                            math.exp(r * T / Periods))
            elif (i <= j and type == 'American'):
                option_df.loc[i, j] = max(max(strike - share_df.loc[i, j], 0),
                                          (q * (option_df.loc[i + 1, j + 1]) + ((1 - q) * (
                                                      option_df.loc[i, j + 1]))) / (math.exp(r * T / Periods)))
            else:
                option_df.loc[i, j] = 0

    return option_df

print(BinomialModel(StockPrice, T, Vol, Periods, r, Div, Strike, callput, 'European'))