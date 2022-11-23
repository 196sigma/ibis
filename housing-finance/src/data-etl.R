# Data ETL
setwd("~/Dropbox/ibis/housing_finance/")


hd.prices <- read.csv("data/HD.csv")
low.prices <- read.csv("data/LOW.csv")
names(hd.prices) <- tolower(names(hd.prices))
names(low.prices) <- tolower(names(low.prices))
X <- merge(hd.prices, low.prices, by = c('date'), suffixes = c('.hd', '.low'))
X <- X[order(X$date, decreasing = FALSE), ]

sp500 <- read.csv('data/sp500.csv')
names(sp500) <- tolower(names(sp500))
a <- c()
for(v in names(sp500)){
  if(v == 'date'){
    a <- c(a, v)  
  }else{
    a <- c(a, paste0(v,'.sp500'))
  }
}
names(sp500) <- a

X <- merge(X, sp500, by = 'date', suffixes = c('', '.sp500'))
X <- X[order(X$date, decreasing = FALSE), ]


X$adj.close.hd.normalized <- X$adj.close.hd/X$adj.close.hd[1]
X$adj.close.low.normalized <- X$adj.close.low/X$adj.close.low[1]
X$adj.close.sp500.normalized <- X$adj.close.sp500/X$adj.close.sp500[1]


#i <- 1; v <- 'adj.close.hd'
X <- X[order(X$date, decreasing = FALSE), ]
for(v in c('adj.close.hd', 
           'adj.close.low', 
           'adj.close.sp500',
           'volume.low', 
           'volume.hd', 
           'volume.sp500')){
  for(i in 1:10){
    v.lag <- paste0(v, '.lag', i)
    X[, v.lag] <- dplyr::lag(X[, v], n = i)
  }  
}

X$adj.close.hd.up <- ifelse(X$adj.close.hd > X$adj.close.hd.lag1, 1, 0)
X$adj.close.low.up <- ifelse(X$adj.close.low > X$adj.close.low.lag1, 1, 0)
X$return.hd.1day <- log(X$adj.close.hd) - log(X$adj.close.hd.lag1)
X$return.low.1day <- log(X$adj.close.low) - log(X$adj.close.low.lag1)

write.csv(x = X, file = 'data/data.csv', row.names = FALSE, quote = FALSE)

