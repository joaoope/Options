from BlackScholes import BlackScholes
from BlackScholes import IV
from Holidays import GetBrazilianHolidays
import pandas as pd
import numpy as np
from datetime import datetime
import datetime as dt

def ScenarioAnalysis(callput, output, underlying_price, strike, maturity, interest, dividend_yield, opt_price, scenarios=4, underlying_stress=0.2, iv_stress=0.1, exposure=None):
    # Error handling:
    strVariables = [callput, output]
    floatVariables = [underlying_price, strike, interest, opt_price, dividend_yield]
    
    strResult = all(isinstance(var, str) for var in strVariables)
    floatResult = all(isinstance(var, float) for var in floatVariables)
    
    if (strResult) == True:
        pass
    else:
        raise ValueError('The "callput" variable must be "c" or "p", and the "output" variable must be "p", "d", "g", "t", "v", "r"')
    
    if (floatResult) == True:
        pass
    else:
        raise ValueError('The variables "underlying_price", "strike", "interest", "opt_price", and "dividend_yield" must be floats')

    if (callput == 'c' or callput == 'p'):
        pass
    else:
        raise ValueError('The "callput" variable must be "c" or "p"')

    if (output == 'p' or output == 'd' or output == 'g' or output == 't' or output == 'v' or output == 'l'):
        pass
    else:
        raise ValueError('The "output" variable must be "p", "d", "g", "t", "v", "l"')
    
    if isinstance(maturity, str):
        maturity = dt.datetime.strptime(maturity, '%Y-%m-%d').strftime('%d/%m/%Y')
    elif isinstance(maturity, dt.date):
        maturity = maturity.strftime('%d/%m/%Y')
    else:
        raise ValueError('The date must follow the type str yyyy-mm-dd or the type dt.date')
    
    #Calculations:
    today = datetime.today().strftime('%Y-%m-%d')
    holidays = GetBrazilianHolidays(today, maturity)
    time = (len(pd.bdate_range(today,maturity,freq='C',holidays=holidays)) - 1) / 252

    opt_iv = IV(callput, underlying_price, strike, time, interest, opt_price, dividend_yield)

    df_index = np.linspace(underlying_price * (1 - underlying_stress), underlying_price * (1 + underlying_stress), 2*scenarios + 1)
    df_columns = np.linspace(opt_iv * (1 - iv_stress), opt_iv * (1 + iv_stress), 2*scenarios + 1)

    df = pd.DataFrame(index=df_index, columns=df_columns)
    df.index.name = 'UnderlyingStress'
    df.columns.name = 'VolStress'

    for price in df_index:
        for volatility in df_columns:
            if output == 'l':
                starting_option = BlackScholes(callput, 'p', underlying_price, strike, time, interest, opt_iv, dividend_yield)
                option = BlackScholes(callput, 'p', price, strike, time, interest, volatility, dividend_yield)
                df.at[price, volatility] = ((option / starting_option) - 1) * exposure
            else:
                option = BlackScholes(callput, output, price, strike, time, interest, volatility, dividend_yield)
                df.at[price, volatility] = option 
        
    return(df)

print(ScenarioAnalysis('c', 'l', 35.21, 34.45, '2023-11-17', 0.1275, 0.00, 2.09, 4, 0.2, 0.1, 10**6))