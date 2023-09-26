import math
from scipy.stats import norm
import numpy as np

def dOne(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend):
    # Calculate d1 for the Black-Scholes formula
    dOne = (math.log(UnderlyingPrice / ExercisePrice) + (Interest - Dividend + 0.5 * Volatility ** 2) * Time) / (Volatility * (np.sqrt(Time)))
    return(dOne)

def NdOne(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend):
    # Calculate the cumulative distribution function of d1
    NdOne = math.exp(-(dOne(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend) ** 2) / 2) / (np.sqrt(2 * 3.14159265358979))
    return(NdOne)

def dTwo(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend):
    # Calculate d2 for the Black-Scholes formula
    dTwo = dOne(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend) - Volatility * np.sqrt(Time)
    return(dTwo)

def NdTwo(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend):
    # Calculate the cumulative distribution function of d2
    NdTwo = norm.cdf(dTwo(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend))
    return(NdTwo)

def BlackScholes(callput, Output, UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend):
    # Error handling:
    strVariables = [callput, Output]
    floatVariables = [UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend]
    
    strResult = all(isinstance(var, str) for var in strVariables)
    floatResult = all(isinstance(var, float) for var in floatVariables)
    
    if (strResult) == True:
        pass
    else:
        raise ValueError('The "callput" variable must be "c" or "p", and the "output" variable must be "p", "d", "g", "t", "v", "r"')
    
    if (floatResult) == True:
        pass
    else:
        raise ValueError('The variables "UnderlyingPrice", "ExercisePrice", "Time", "Interest", "Volatility", and "Dividend" must be floats')

    if (callput == 'c' or callput == 'p'):
        pass
    else:
        raise ValueError('The "callput" variable must be "c" or "p"')

    if (Output == 'p' or Output == 'd' or Output == 'g' or Output == 't' or Output == 'v' or Output == 'r'):
        pass
    else:
        raise ValueError('The "output" variable must be "p", "d", "g", "t", "v", "r"')
    
    # Calculate for Call option:
    if callput == 'c':
        if Output == 'p':  # Return price:
            BlackScholes = math.exp(-Dividend*Time) * UnderlyingPrice * norm.cdf(dOne(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend)) - ExercisePrice * math.exp(-Interest * Time) * norm.cdf(dOne(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend) - Volatility * np.sqrt(Time))
        elif Output == 'd': # Return delta:
            BlackScholes = norm.cdf(dOne(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend))
        elif Output == 'g': # Return gamma:
            BlackScholes = NdOne(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend) / (UnderlyingPrice * (Volatility * np.sqrt(Time)))
        elif Output == 't': # Return theta:
            CT = -(UnderlyingPrice * Volatility * NdOne(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend)) / (2 * np.sqrt(Time)) - Interest * ExercisePrice * math.exp(-Interest * (Time)) * NdTwo(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend)
            BlackScholes = CT / 365
        elif Output == 'v': # Return vega:
            BlackScholes = 0.01 * UnderlyingPrice * np.sqrt(Time) * NdOne(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend)
        elif Output == 'r': # Return rho:
            BlackScholes = 0.01 * ExercisePrice * Time * math.exp(-Interest * Time) * norm.cdf(dTwo(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend))
        else:
            pass
        
     # Calculate for Put option:
    elif callput == 'p':
        if Output == 'p': # Return price:
            BlackScholes = ExercisePrice * math.exp(-Interest * Time) * norm.cdf(-dTwo(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend)) - math.exp(-Dividend * Time) * UnderlyingPrice * norm.cdf(-dOne(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend))
        elif Output == 'd': # Return delta:
            BlackScholes = norm.cdf(dOne(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend)) - 1
        elif Output == 'g': #Retornando gamma:
            BlackScholes = NdOne(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend) / (UnderlyingPrice * (Volatility * np.sqrt(Time)))
        elif Output == 't': # Return theta:
            PT = -(UnderlyingPrice * Volatility * NdOne(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend)) / (2 * np.sqrt(Time)) + Interest * ExercisePrice * math.exp(-Interest * (Time)) * (1 - NdTwo(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend))
            BlackScholes = PT / 365
        elif Output == 'v': # Return vega:
            BlackScholes = 0.01 * UnderlyingPrice * np.sqrt(Time) * NdOne(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend)
        elif Output == 'r': # Return rho:
            BlackScholes = -0.01 * ExercisePrice * Time * math.exp(-Interest * Time) * (1 - norm.cdf(dTwo(UnderlyingPrice, ExercisePrice, Time, Interest, Volatility, Dividend)))
            
    else:
        pass
    
    
    return(BlackScholes)

def IV(callput,UnderlyingPrice,ExercisePrice,Time,Interest,Target,Dividend):
    if callput == 'c':
        High = 5
        Low = 0
        while (High - Low) > 0.0001:
            # Binary search to find implied volatility for a call option
            if BlackScholes("c", "p", UnderlyingPrice, ExercisePrice, Time, Interest, (High + Low) / 2, Dividend) > Target:
                High = (High + Low) / 2
            else:
                Low = (High + Low) / 2
        
        Vol = (High + Low) / 2
        
    elif callput == 'p':
        High = 5
        Low = 0
        while (High - Low) > 0.0001:
            # Binary search to find implied volatility for a put option
            if BlackScholes("p", "p", UnderlyingPrice, ExercisePrice, Time, Interest, (High + Low) / 2, Dividend) > Target:
                High = (High + Low) / 2
            else:
                Low = (High + Low) / 2
        
        Vol = (High + Low) / 2
        
    return(Vol)

info = BlackScholes('p','p',11.5,12.0,0.087671233,0.1288,0.25,0.0)
vol =  IV('p',11.5,12.0,0.087671233,0.1288,0.5578,0.0)
print(info, vol)