from scipy.stats import ks_2samp
import numpy as np

# Generate two samples
sample1 = np.random.normal(loc=0, scale=1, size=2)
sample2 = np.random.normal(loc=0.5, scale=1, size=100)
print(sample1)
print(sample2)

# Perform the Kolmogorov-Smirnov test
stat, p = ks_2samp(sample1, sample2)

# Print the p-value
print('p-value:', p)