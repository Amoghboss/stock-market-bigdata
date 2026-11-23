# MapReduce Job 7: Volatility Analysis

## Objective
Quantifies the market risk profile of each stock by computing the historical dispersion of daily logarithmic returns and annualizing the resulting standard deviation across 252 standard trading sessions per calendar year.

## Mathematical Formulation
1. **Daily Log Return**:
   $$r_t = \ln\left(\frac{P_t}{P_{t-1}}\right)$$

2. **Sample Standard Deviation**:
   $$\sigma_{\text{daily}} = \sqrt{\frac{1}{N-1}\sum_{t=1}^N (r_t - \bar{r})^2}$$

3. **Annualized Historical Volatility**:
   $$\sigma_{\text{annualized}} = \sigma_{\text{daily}} \times \sqrt{252} \times 100\%$$

## Mapper Implementation (`mapper.py`)
- Emits `symbol\tdate\tclose_price` for valid CSV lines.

## Reducer Implementation (`reducer.py`)
- Receives keys partitioned and sorted by Hadoop.
- Orders records chronologically, calculates returns, applies the variance formula, and emits risk metrics.

## Sample Output
```
Symbol	Annualized_Vol_Pct	Mean_Daily_Return_Pct	Daily_Std_Pct	Days_Analyzed
BAJFINANCE	38.14%	+0.0412%	2.4025%	1305
RELIANCE	25.42%	+0.0385%	1.6012%	1305
HINDUNILVR	19.10%	+0.0192%	1.2031%	1305
```
