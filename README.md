# Volitility-Surface-Model
Creating volatility surface using model specified in 2020 paper "Option-implied information: What’s the vol surface got to do with it?".

## Overview
Creates estimated implied volatility using 1D kernel regression model. Uses data freely accessible from LSE (London Strategic Edge) with built in access and functions for creating data sets of differing type and size depending on use. 

The project is currently in active development, with new features, improvements and extensions being implemented soon.

## Features
- flexible and free dataset creation for model from LSE intra-day options flow data
- 1D kernel regression model for estimating implied volatility over range of moneyness
- data and visual output for volatility surface
- data summary

## Development Progress
The project is currently under active development. The following outlines completed work, ongoing tasks and planned improvements.
### Completed
- [X] 1D kernel regression model
- [X] large data collection (LSE)
### In Progress
- [ ] Logging and error management
- [ ] Full range DTE data collection
### Upcoming
- [ ] Full back-testing
- [ ] Implied information based on vol surface estimates
