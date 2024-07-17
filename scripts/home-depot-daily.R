# Home Depot
rm(list=ls())
gc()

getwd()
#install.packages("forecast")
#install.packages("tseries")
#install.packages("lubridate")



# Load necessary libraries
library(forecast)
library(tseries)
library(lubridate)
hd_daily <- read.csv("data/HD.csv")
# Assuming 'Date' column is character, convert it to Date type
hd_daily$Date <- as.Date(hd_daily$Date, "%Y-%m-%d")

# Make sure data is in ascending date order
hd_daily <- hd_daily[order(hd_daily$Date),]

# Set Date as rownames (necessary for time series objects)
rownames(hd_daily) <- hd_daily$Date

# Create a time series object from the 'Adj Close' column
adj_close_ts <- ts(hd_daily$Adj.Close, start=c(year(hd_daily$Date[1]), yday(hd_daily$Date[1])), frequency=365)

# Check if the time series is stationary using the Augmented Dickey-Fuller Test
adf_test <- adf.test(adj_close_ts)

# If p-value > 0.05, data is non-stationary and needs differencing
if (adf_test$p.value > 0.05) {
  print("Not stationary")
  # Difference the data and store it back in adj_close_ts
  adj_close_ts <- diff(adj_close_ts)
}

# Use auto.arima() function to find best ARIMA model according to AIC
fit <- auto.arima(adj_close_ts)

# Forecast the next day's adjusted close
forecasted_data <- forecast(fit, h=1)

# Print forecasted data
print(forecasted_data)
