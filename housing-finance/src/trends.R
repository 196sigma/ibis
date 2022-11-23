rm(list=ls())
gc()

library(wikipediatrend)
# Wikipedia
wiki.trends <- wikipediatrend::wp_trend(page = c("The_Home_Depot"), 
                                        lang = c("en"), 
                                        from = "2016-01-01",
                                        to   = Sys.Date()
)
wiki.trends$date <- as.Date(wiki.trends$date)
# calc weekly average views
ma <- function(x, n = 7){filter(x, rep(1 / n, n), sides = 1)}
wiki.trends$views.ma7 <- ma(wiki.trends$views)

trends <- read.csv('housing_finance/data/google-trends-long.csv')
names(trends)
# adjust trend date to last friday
trends$date2 <- as.Date(trends$date) + 1
trends$isPartial <- NULL

# Load stock and index data
X <- read.csv('data/data.csv')

X1 <- X[, c('date', 'adj.close.hd', 'adj.close.hd.lag1', 'adj.close.sp500', 'adj.close.sp500.lag1')]
X1$date <- as.Date(X1$date)
X1 <- merge(X1, trends, by.x = 'date', by.y = 'date2')
X1$date.y <- NULL
X1 <- merge(X1, wiki.trends, by = 'date')
X1$views.ma7.lag1 <- dplyr::lag(X1$views.ma7)

n <- nrow(X1)
n.train <- floor(.9*n)
X1.train <- X1[1:n.train, ]
X1.test <- X1[n.train:n, ]

x1 <- X1$home.depot/X1$home.depot[1]
x2 <- X1$adj.close.hd/X1$adj.close.hd[1]
x3 <- X1$views.ma7.lag1/X1$views.ma7.lag1[2]
plot(x1, type = 'l')
lines(x2, type='l', col='red')
lines(x3, type='l', col='blue')

m1 <- lm(adj.close.hd ~ home.depot + views.ma7.lag1 + adj.close.hd.lag1 + adj.close.sp500.lag1, data = X1.train)
summary(m1)
plot(m1$residuals)
hist(m1$residuals)

m1.pred <- predict(m1, X1.test)
X1.test$m1.pred <- m1.pred
X1.test$error.dir <- ifelse(X1.test$m1.pred > X1.test$adj.close.hd, 1, -1)
barplot(X1.test$error.dir)
table(X1.test$error.dir)


X2 <- X
X2$adj.close.hd <- ifelse(X2$adj.close.hd > X2$adj.close.hd.lag1, 1, 0)
X2$adj.close.hd.lag1 <- ifelse(X2$adj.close.hd.lag1 > X2$adj.close.hd.lag2, 1, 0)
X2$adj.close.low <- ifelse(X2$adj.close.low > X2$adj.close.low.lag1, 1, 0)
X2$adj.close.low.lag1 <- ifelse(X2$adj.close.low.lag1 > X2$adj.close.low.lag2, 1, 0)

mi.baseline <- infotheo::multiinformation(X = X2[,c('adj.close.hd', 'adj.close.hd')])
infotheo::mutinformation(X = X2[,c('adj.close.hd', 'adj.close.hd.lag1')])
infotheo::mutinformation(X = X2[,c('adj.close.hd', 'adj.close.hd.lag1','adj.close.low')])

