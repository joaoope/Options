from BlackScholes import IV
import pandas as pd
import numpy as np
from datetime import datetime
from scipy.linalg import lstsq
import scipy.stats as stats
import matplotlib.pyplot as plt

input_data = {
    'strikes': [107.00, 109.00, 111.00, 113.00, 115.00, 117.00, 107.00, 109.00, 111.00, 113.00, 115.00, 117.00],
    'prices': [7.00, 5.37, 3.85, 2.63, 1.65, 0.95, 9.00, 6.86, 6.05, 4.06, 3.06, 2.08],
    'maturities': ['2023-11-17', '2023-11-17','2023-11-17', '2023-11-17', '2023-11-17', '2023-11-17', 
                  '2023-12-15', '2023-12-15','2023-12-15', '2023-12-15', '2023-12-15', '2023-12-15'],
    'types': ['c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c']
}

underlying_price = 112.06
interest = 0.1275
dividend = 0.00
scenarios = 100
time_range = 300

def VolSurfaceDVM(input_data, underlying_price, interest, dividend, scenarios, time_range):

    #Removing outliers
    def remove_outliers_zscore(df, column, threshold=3):
        z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
        return df[z_scores < threshold]

    # Check if all lists have the same length
    if len(set(len(lst) for lst in input_data.values())) == 1:
        pass
    else:
        raise ValueError("Lists have different numbers of elements.")

    today = datetime.today().strftime('%Y-%m-%d')

    opts_data = pd.DataFrame(input_data, columns=['strikes', 'prices', 'maturities', 'types'])

    # Calculate 'T' and 'IV' values for each option in 'opts_data'
    for opt in opts_data.index:
        opts_data.loc[opt,'T'] = (len(pd.date_range(today,opts_data.loc[opt,'maturities']))-1)/365
        opts_data.loc[opt,'IV'] = IV(opts_data.loc[opt,'types'],underlying_price,opts_data.loc[opt,'strikes'],opts_data.loc[opt,'T'],interest,opts_data.loc[opt,'prices'],dividend)

    # Remove outliers in 'IV' column using the 'remove_outliers_zscore' function
    opts_data = remove_outliers_zscore(opts_data, 'IV', 3).dropna()

    # Create 'dvm_model' DataFrame with calculated features
    dvm_model = pd.DataFrame(index = opts_data.index)
    dvm_model['K'], dvm_model['Ksqr'], dvm_model['T'], dvm_model['Tsqr'], dvm_model['KT']  = opts_data.loc[:,'strikes'], (opts_data.loc[:,'strikes'])**2, opts_data.loc[:,'T'], (opts_data.loc[:,'T'])**2, opts_data.loc[:,'strikes'] * opts_data.loc[:,'T']

    # Perform least squares regression to calculate coefficients
    X_with_intercept = np.column_stack((np.ones(dvm_model.to_numpy().shape[0]), dvm_model.to_numpy()))
    coefficients, _, _, _ = lstsq(X_with_intercept, opts_data.loc[:,'IV'].to_numpy(), lapack_driver='gelsy')
    intercept = coefficients[0]
    other_coefficients = coefficients[1:]

    # Calculate mean, standard deviation, and create the strikes distribution
    mean = np.mean(input_data['strikes'])
    std_dev = np.std(input_data['strikes']) 
    std_dev *= 1.5  
    distribution = stats.norm(loc=mean, scale=std_dev)

    # Generate strike and time values for the vol_surface
    vol_surface_strikes = np.sort(distribution.rvs(size=scenarios))
    vol_surface_times = np.linspace(1, time_range, scenarios).astype(int)

    # Create an empty 'vol_surface' DataFrame
    vol_surface = pd.DataFrame(index = vol_surface_strikes, columns = vol_surface_times)

    # Calculate volatility values for the vol_surface
    for strike in vol_surface.index:
        for time in vol_surface.columns.tolist():
            time_adj = time / 365
            dvm = [strike, strike**2, time_adj, time_adj**2, strike*time_adj]
            vol_surface.loc[strike, time] = intercept + (other_coefficients * dvm).sum()
                                                     
    return(vol_surface)

surface = VolSurfaceDVM(input_data, underlying_price, interest, dividend, scenarios, time_range)
print(surface)

# Create a meshgrid of strike and time values
strike_mesh, time_mesh = np.meshgrid(surface.index, surface.columns.tolist())

# Create the 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the 3D surface
ax.plot_surface(strike_mesh, time_mesh, surface.values, cmap='viridis')

# Set labels for the axes
ax.set_xlabel('Strike')
ax.set_ylabel('Time to Maturity')
ax.set_zlabel('Volatility')

# Show the plot
plt.show()