rm(list=ls())
gc()

company_name <- "Google"
ticker <- "goog"

daily_data <- read.csv(sprintf("~/Dropbox/ibis/data/us_equities_daily/stocks/%s.us.txt", ticker))
names(daily_data) <- tolower(names(daily_data))
daily_data <- daily_data[order(daily_data$date, decreasing = FALSE), ]
dim(daily_data)

train <- daily_data[which(daily_data$date < "2016-01-01"), ]
val <- daily_data[which((daily_data$date >= "2016-01-01") & (daily_data$date < "2017-01-01")), ]
plot(daily_data$close, type='l', col='darkgreen')
points(c(train$close, val$close), type='l', col='yellow')
points(train$close, type='l', col='red')
date_list <- val$date

n_val = nrow(val)
prediction_results <- data.frame(date=val$date,
                                 close_actual = rep(NA, n_val),
                                 close_pred = rep(NA, n_val))
for(i in 1:n_val){
  #i <- 1
  target_date <- val[i, "date"]; target_date
  current_train_set <- daily_data[which(daily_data$date < target_date), ]; tail(current_train_set)
  print(c(target_date, nrow(current_train_set)))
  next_day_set <- val[which(val$date == target_date), ]; next_day_set
  next_day_date <- next_day_set$date; next_day_date
  next_day_actual <- next_day_set$close; next_day_actual
  arima_1_0_0_fit <- arima(x = current_train_set$close, 
                                order = c(1,0,0),
                                include.mean = TRUE)
  arima_1_0_0_pred <- predict(arima_1_0_0_fit, 
                                   n.ahead = 1)
  next_day_pred <- arima_1_0_0_pred$pred[[1]]; next_day_pred
  c(next_day_date, next_day_actual, next_day_pred)
  
  prediction_results[i, "date"] <- target_date
  prediction_results[i, "close_actual"] <- next_day_actual
  prediction_results[i, "close_pred"] <- next_day_pred 
}
plot(prediction_results$close_actual, type='l', col='darkgreen')
points(prediction_results$close_pred, type='l', col='green')

prediction_results$error <- prediction_results$close_pred - prediction_results$close_actual
plot(prediction_results$error, type='l')
pred_error <- prediction_results$error
mean(pred_error**2)
sqrt(mean(pred_error**2))
prediction_results$percent_error <- round(prediction_results$error/prediction_results$close_actual, 3)
plot(prediction_results$percent_error, type='l')

