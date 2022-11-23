# EDA

####################################################################################################
# Environment
####################################################################################################
rm(list=ls())
gc()
setwd("~/housing_finance")
source('src/data-etl.R')

library(fGarch)
library(MASS)

# 2019
X <- hd.prices[hd.prices$date > '2018-12-31' & hd.prices$date < '2020-01-01',]
X$ret <- X$adj.close/dplyr::lag(X$adj.close) - 1
plot(X$ret, type = 'l', col='red')
plot(X$adj.close, type='l', col='blue')
plot(density(X$adj.close))

ret.mu <- mean(X$ret, na.rm = TRUE)
ret.sd <- sd(X$ret, na.rm = TRUE)
n <- nrow(X) - 1 
simulated.ret <- rnorm(1000000, ret.mu, ret.sd)
simulated.ret.ged <- rged(1000000, mean = ret.mu, sd = ret.sd)
plot(density(X$ret, na.rm = TRUE))
lines(density(simulated.ret), col='blue')
lines(density(simulated.ret.ged), col='red')

MASS::fitdistr(x = X[2:nrow(X), 'ret'], densfun = dged)

pacf(X$adj.close)
names(X)

colMeans(X[, c('adj.close.hd.up', 'adj.close.low.up')], na.rm = TRUE)
aggregate(return.hd.1day ~ adj.close.hd.up, data = X, FUN = mean, na.rm = TRUE)
aggregate(return.low.1day ~ adj.close.low.up, data = X, FUN = mean, na.rm = TRUE)


par(mfrow=c(1,1))
plot(X$adj.close.hd, type='l', col = 'red', lwd = 3)
lines(X$adj.close.low, col = 'blue', lwd = 3)


plot(X$close.hd.normalized, type='l', col = 'red', lwd = 3, ylim = c(0, 250))
lines(X$close.low.normalized, col = 'blue', lwd = 3)
lines(X$close.sp500.normalized)

par(mfrow=c(3,1))
plot(X$close.hd, type='l', col = 'red', lwd = 3, ylim = c(0, 250))
acf(X$close.hd)
pacf(X$close.hd)

par(mfrow=c(3,1))
plot(X$close.low, type='l', col = 'blue', lwd = 3, ylim = c(0, 250))
acf(X$close.low)
pacf(X$close.low)

X <- dplyr::filter(X, date < '2016-01-01')
m.hd <- lm(adj.close.hd ~ adj.close.sp500.lag1 +
             adj.close.sp500.lag2 +
             adj.close.sp500.lag3 +
             adj.close.sp500.lag4 +
             adj.close.sp500.lag5 +
             adj.close.sp500.lag6 +
             adj.close.sp500.lag7 +
             adj.close.sp500.lag8 +
             adj.close.sp500.lag9 +
             adj.close.sp500.lag10 +
             adj.close.hd.lag1 +
             adj.close.hd.lag2 +
             adj.close.hd.lag3 +
             adj.close.hd.lag4 +
             adj.close.hd.lag5 +
             adj.close.hd.lag6 +
             adj.close.hd.lag7 +
             adj.close.hd.lag8 +
             adj.close.hd.lag9 +
             adj.close.hd.lag10 +
             adj.close.low.lag1 + 
             adj.close.low.lag2 + 
             adj.close.low.lag3 + 
             adj.close.low.lag4 + 
             adj.close.low.lag5 + 
             adj.close.low.lag6 + 
             adj.close.low.lag7 + 
             adj.close.low.lag8 + 
             adj.close.low.lag9 + 
             adj.close.low.lag10, 
           data = X)

m.low <- lm(adj.close.low ~ adj.close.sp500.lag1 +
             adj.close.sp500.lag2 +
             adj.close.sp500.lag3 +
             adj.close.sp500.lag4 +
             adj.close.sp500.lag5 +
             adj.close.sp500.lag6 +
             adj.close.sp500.lag7 +
             adj.close.sp500.lag8 +
             adj.close.sp500.lag9 +
             adj.close.sp500.lag10 +
             adj.close.hd.lag1 +
             adj.close.hd.lag2 +
             adj.close.hd.lag3 +
             adj.close.hd.lag4 +
             adj.close.hd.lag5 +
             adj.close.hd.lag6 +
             adj.close.hd.lag7 +
             adj.close.hd.lag8 +
             adj.close.hd.lag9 +
             adj.close.hd.lag10 +
             adj.close.low.lag1 + 
             adj.close.low.lag2 + 
             adj.close.low.lag3 + 
             adj.close.low.lag4 + 
             adj.close.low.lag5 + 
             adj.close.low.lag6 + 
             adj.close.low.lag7 + 
             adj.close.low.lag8 + 
             adj.close.low.lag9 + 
             adj.close.low.lag10, 
           data = X)

summary(m.hd)
summary(m.low)
# Market
summary(lm(close.hd.normalized ~ close.sp500.normalized, data = X))
summary(lm(close.low.normalized ~ close.sp500.normalized, data = X))

# Macro

# Earnings

# Sentiment