---
editor: 
  markdown: 
    wrap: sentence
---

# Philadelphia Eviction Early Warning System

**Authors:** Angel Rutherford, Ixchel Ramirez, Tess Vu

**Affiliation:** University of Pennsylvania | MUSA 5080: Public Policy Analytics

**Date:** December 8, 2025

## Executive Summary

Eviction is both a cause and consequence of poverty that destabilizes entire neighborhoods. Currently, city responses to eviction are reactive, with resources like legal aid and rental assistance deployed *after* filing volumes become a crisis. This project develops a Real-Time Operational Tool for the Philadelphia Office of Homeless Services and the Fair Housing Commission. By shifting from reactive to predictive analysis, we enable the city to allocate limited staff to specific census tracts predicted to experience elevated eviction filings in the coming month.

Our Negative Binomial regression model leverages temporal momentum, spatial spillover effects, policy intervention effects, property tax delinquency stress, and American Community Survey socioeconomic indicators to forecast monthly eviction filing counts at the census tract level.

The model demonstrates strong performance with meaningful improvement, and sets the foundation for building up to a practical and usable tool down the line. Using a robust temporal validation strategy (training through 2023, testing on 2024-2025), the model generalizes well to future periods without overfitting. Also stark racial disparities in eviction burden was identified, with Black-majority tracts accounting for disproportionate shares of filings. These findings emphasize the need for equity-centered implementation safeguards to prevent perpetuating existing disparities through algorithmic resource allocation.

## Predictive Question

**"Where should renter's assistance programs be targeted in Philadelphia?"**

**Target Variable:** Monthly Count of Eviction Filings per Census Tract.

## Data Sources & Integration

[Eviction Lab Main Data](https://evictionlab.org/eviction-tracking/get-the-data/)

[Eviction Lab Claims Data](https://evictionlab.org/eviction-tracking/philadelphia-pa/)

[Real Estate Tax Balances](https://opendataphilly.org/datasets/real-estate-tax-balances/)

[Neighborhood Boundaries](https://opendataphilly.org/datasets/philadelphia-neighborhoods/)

[Tract Boundaries](https://opendataphilly.org/datasets/census-tracts/)

ACS 2023 Data via `tidycensus` API