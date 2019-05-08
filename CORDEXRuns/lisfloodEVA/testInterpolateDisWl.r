# example of interpolation
set.seed(20)
q <- seq(from=0, to=20, by=0.1)
y <- 500 + 0.4 * (q-10)^3

noise <- rnorm(length(q), mean=10, sd=80)
noisy.y <- y + noise
plot(q,noisy.y,col='deepskyblue4',xlab='q',main='Observed data');

model <- lm(noisy.y ~ poly(q,3))
#model <- lm(noisy.y ~ q + I(q^2) + I(q^3))

par(new=T)
plot(q, fitted(model));