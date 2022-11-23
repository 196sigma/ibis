rm(list=ls())
gc()
library(caret)
x <- read.csv("data/monthly_sp500_modeling.csv", stringsAsFactors = FALSE)
n.train <- round(nrow(x)*.7)
n.test <- nrow(x)-n.train
x.train <- x[1:n.train, ]
x.test <- x[(n.train+1):nrow(x),]
x$date <- NULL
m <- lm(sp500_lead1 ~ ., data=x); summary(m)
preds <- predict(m, x.test)
mae <- mean(abs(x.test$sp500_lead1 - preds), na.rm = TRUE); mae
x.test$sp500_pred <- preds

ifelse(x.test$sp500_lead1 > x.test$sp500_pred,1,0)
plot(x.test$sp500_lead1, type='l', col='blue')
points(x.test$sp500_pred, type='l', col='red')
