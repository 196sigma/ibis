rm(list=ls())
gc()
setwd("~/housing_finance/")
hd.prices <- read.csv("data/HD.csv")
low.prices <- read.csv("data/LOW.csv")
names(hd.prices) <- tolower(names(hd.prices))
names(low.prices) <- tolower(names(low.prices))
X <- merge(hd.prices, low.prices, by = c('date'), suffixes = c('.hd', '.low'))
X <- X[2000:nrow(X), ]

plot(X$adj.close.hd, col='orange', type='l')
lines(X$adj.close.low, col = 'blue')

# Normalized prices
X$adj.close.hd.normalized <- X$adj.close.hd/X[1,'adj.close.hd']
X$adj.close.low.normalized <- X$adj.close.low/X[1,'adj.close.low']

plot(X$adj.close.hd.normalized, col='orange', type='l', ylim=c(0,30))
lines(X$adj.close.low.normalized, col = 'blue')
X$spread <- X$adj.close.hd.normalized - X$adj.close.low.normalized
plot(X$spread, type='l', col='blue', lwd=3)
s <- 2*sd(X$spread)
abline(h = mean(X$spread), col='red')
abline(h = mean(X$spread) + s, col = 'red')
abline(h = mean(X$spread) - s, col='red')
pacf(X$spread)
acf(X$spread)
forecast::auto.arima(X$spread)
forecast::auto.arima(X$adj.close.hd)
forecast::auto.arima(X$adj.close.low)

# Log adjusted closing prices
plot(log(X$adj.close.hd), col='orange', type='l')
lines(log(X$adj.close.low), col = 'blue')
m <- lm(log(adj.close.hd) ~  log(adj.close.low), data = X); summary(m)
res <- m$residuals
var(res)
sd(res)
par(mfrow=c(2,1))
plot(res, type='l', col='red')
acf(res)

# Ratios
X$adj.close.hd.to.low <- X$adj.close.hd/X$adj.close.low
par(mfrow=c(3,1))
plot(X$adj.close.hd.to.low, col='red', type='l', lwd=3)
abline(h = median(X$adj.close.hd.to.low), col='grey50')
acf(X$adj.close.hd.to.low)
pacf(X$adj.close.hd.to.low)
X$adj.close.hd.to.low.rollmean <- zoo::rollmean(X$adj.close.hd.to.low, k = 100,na.pad = TRUE)
plot(X$adj.close.hd.to.low.rollmean, col='red', type='l')

X$volume.hd.to.low <- X$volume.hd/X$volume.low
X$volume.hd.to.low <- zoo::rollmean(X$volume.hd.to.low, k = 100,na.pad = TRUE)
plot(X$volume.hd.to.low, col='red', type='l', lwd=3)
abline(h=median(X$volume.hd.to.low, na.rm = TRUE), col='grey50')
hist(X$volume.hd.to.low)
hist(log(X$volume.hd.to.low))
