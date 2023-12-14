import numpy as np
import statsmodels.api as sm 

def fit_regression(rbi_values: np.array, perf_values: np.array):
    print(rbi_values)
    print(perf_values)
    rbi_values = sm.add_constant(rbi_values)
    model = sm.OLS(perf_values, rbi_values)
    results = model.fit()

    # Extract the required statistics
    intercept, slope = results.params
    r_squared = results.rsquared
    _, rpi_p_value = results.pvalues
    _, rpi_t_stat = results.tvalues

    return intercept, slope, r_squared, rpi_p_value, rpi_t_stat