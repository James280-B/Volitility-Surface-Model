# Volitility-Surface-Model

Creating volatility surface using model specified in 2020 paper "Option-implied information: What’s the vol surface got
to do with it?".

## Overview

Creates estimated implied volatility using 1D kernel regression model. Uses data freely accessible from LSE (London
Strategic Edge) with built in access and functions for creating data sets of differing type and size depending on use.

The project is currently in active development, with new features, improvements and extensions being implemented soon.

### Data Overview

Uses the freely accessible data from LSE. Chosen for both its free access and its deep availability of historical
options data on large range of different underlyings. Data is selected via 5000 row chunks due to the limit imposed by
LSE, per day. Data is then cleaned (dropping any row with missing data) and filtered via an put-call parity arbitrage
filtering system where options are paired in put-call pairs based on having the same strike and TTM, on the same day.
Impose the same constraints as in Ulrich and Walther (2020) where only those pairs where the percentage change of the
underlying price is below 0.01% and also impose a secondary constriction where only those pairs that are within a
minutes time frame of each other are kept.

For the risk free rate used in computing continuous dividends used in put-call parity calculation uses data sourced from
CheckMySwap.

The input data is then put in the model in put-call pairs.

### Model Overview

Use best performning model as found in Lrich and Walther (2020), which is their 1D kernel regression model as specified
below:

Moneyness for each strike $K_i$ with forward $F_i$:

$$
m_i = \frac{K_i}{F_i}
$$

Strike spacing for expiry $\tau$, using $N^*(\tau)$ strikes:

$$
\Delta K(\tau) = \frac{1}{N^*(\tau) - 1}\left(K_{\max}(\tau) - K_{\min}(\tau)\right)
$$

Kernel bandwidth for expiry $\tau$:

$$
h(\tau) = 0.75 \Delta K(\tau)
$$

Kernel-weighted (Nadaraya–Watson) estimate of implied volatility at moneyness $m_j$ for expiry $\tau$:

$$
\sigma(m_j, \tau) =
\frac{
\sum_{i=1}^{N^{\ast}}
k\left(m_j - m_i\right)\sigma(m_i, \tau)
}{
\sum_{i=1}^{N^{\ast}}
k\left(m_j - m_i\right)
}
$$

The kernel used is:

$$
k(x)=\frac{1}{\sqrt{2\pi}}
\exp\left(-\frac{x^2}{2h_x}\right)
$$

## Features

- Flexible and free dataset creation for model from LSE intra-day options flow data via DataBuilder class
- 1D kernel regression model for estimating implied volatility over range of moneyness via OneDKernelRegressionModel
  class
- Data and visual output for volatility surface
- Output data summary of input data

## Development Progress

The project is currently under active development. The following outlines completed work, ongoing tasks and planned
improvements.

### Completed

- [X] 1D kernel regression model
- [X] large data collection (LSE)
- [X] Logging and error management

### In Progress

- [ ] Full range DTE data collection
- [ ] Improving model computational performance

### Upcoming

- [ ] Full back-testing
- [ ] Implied information based on vol surface estimates
