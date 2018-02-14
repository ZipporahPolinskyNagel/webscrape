library(ggplot2)
library(dplyr)
library(data.table)
library(tidyr)
library(wordcloud)
library(zoo)
library(googleVis)


beers <- read.csv("beer_reviews_v1.csv",stringsAsFactors = FALSE)
beers.df <- as.data.frame(beers)

#data cleanup

#title	judges_rating	aroma	appearance	flavor	mouthfeel	overall	date	brewery	brew_style	availability	state	country	reviewer	body
#extract year
beers.df$date = zoo::as.yearmon(beers.df$date, "%b, %Y")
beers.df$year = as.numeric(year(beers.df$date))

#appearance and mouthfeel come through as dates- change them to numbers- month becomes the rating
beers.df$appearance = as.Date(beers.df$appearance, "%e-%b")
beers.df$appearance = as.numeric(month(beers.df$appearance))
beers.df$mouthfeel = as.Date(beers.df$mouthfeel, "%e-%b")
beers.df$mouthfeel = as.numeric(month(beers.df$mouthfeel))

#aroma, flavor, overall have the slash which needs to be removed
beers.df$aroma = as.numeric(sapply(strsplit(beers.df$aroma, "/"), "[", 1))
beers.df$flavor = as.numeric(sapply(strsplit(beers.df$flavor, "/"), "[", 1))
beers.df$overall = as.numeric(sapply(strsplit(beers.df$overall, "/"), "[", 1))

#only going to look at the brew styles who have appeared at least 20 times
top_brewstyle <- 
  group_by(beers.df, brew_style) %>% 
  summarize( count = n() ) %>%
  filter(count > 10)

beers.df.filtered = semi_join(beers.df, top_brewstyle, by = 'brew_style')

# use this data to make charts

#scores by reviewer
avg_reviewer <-
  group_by( beers.df.filtered, reviewer) %>%
  filter( overall <= 20) %>%
  filter( appearance <= 6) %>%
  filter( mouthfeel <= 10) %>%
  filter( overall <=20) %>%
  filter( judges_rating <= 100) %>%
  select( reviewer, judges_rating) %>%
  summarize( sd = sd(judges_rating))

reviewer_chart <- gvisCandlestickChart(avg_reviewer, options=list(gvis.editor="Pick one",
                                                                  title="Scores by Reviewer"))

plot( reviewer_chart)



#scores by state
avg_state <-
  group_by( beers.df.filtered, state) %>%
  filter( country == "United States" ) %>%
  filter( state != "") %>%
  filter( overall <= 20) %>%
  filter( appearance <= 6) %>%
  filter( mouthfeel <= 10) %>%
  filter( overall <=20) %>%
  filter( judges_rating <= 100) %>%
  summarize( count = n(), average = mean(judges_rating), min = min(judges_rating), max= max(judges_rating)) %>%
  arrange( desc(count )) %>%
  top_n(10)

state_chart <-  gvisLineChart(avg_state, "state", c("average","min", "max"), options=list(gvis.editor="Pick one",
                                                                                          title="Scores by State"))

plot(state_chart)

#scores by brew_style
avg_brewstyle <-
  group_by( beers.df.filtered, brew_style) %>%
  filter( overall <= 20) %>%
  filter( appearance <= 6) %>%
  filter( mouthfeel <= 10) %>%
  filter( overall <=20) %>%
  filter( judges_rating <= 100) %>%
  summarize( count = n(), average = mean(judges_rating), min = min(judges_rating), max= max(judges_rating)) %>%
  arrange( desc(count ))

brew_style_chart <-  gvisLineChart(avg_brewstyle, "brew_style", c("average","min", "max"), options=list(gvis.editor="Pick one",
                                                                                                        title ="Scores by Brew Style"))

plot(brew_style_chart)

scatter <- gvisScatterChart(beers.df.filtered[,c("overall", "appearance")])
plot(scatter,"chart")

bar <- gvisBarChart(beers.df.filtered[, ""])

plot(bar)


# word cloud
library(wordcloud) # this requires the tm and NLP packages
library(devtools)
library(SnowballC)


all_desc_vector <- as.vector(head(unlist(strsplit(beers.df.filtered$body, split = "\\s+")),10))
docs <- Corpus(VectorSource(entire_desc_text))
toSpace <- content_transformer(function (x , pattern ) gsub(pattern, " ", x))
docs <- tm_map(docs, toSpace, "/")
docs <- tm_map(docs, toSpace, "@")
docs <- tm_map(docs, toSpace, "\\|")

# Remove punctuations
docs <- tm_map(docs, removePunctuation)
# Convert the text to lower case
docs <- tm_map(docs, content_transformer(tolower))
# Remove numbers
docs <- tm_map(docs, removeNumbers)

# Eliminate extra white spaces
docs <- tm_map(docs, stripWhitespace)
# Remove english common stopwords
docs <- tm_map(docs, removeWords, stopwords("english"))
# Remove your own stop word
# specify your stopwords as a character vector
docs <- tm_map(docs, removeWords, c("near", "required", "upon", "use", "with", "the",
                                    "that", "and")) 
docs <- tm_map(docs, stemDocument)
#docs <- tm_map(docs, stemDocument)
dtm <- TermDocumentMatrix(docs)
m <- as.matrix(dtm)
v <- sort(rowSums(m),decreasing=TRUE)
d <- data.frame(word = names(v),freq=v)
head(d, 10)

set.seed(1234)
wordcloud(words = d$word, freq = d$freq, min.freq = 50, scale=c(1.5,.5),
          max.words=500, random.order=FALSE, rot.per=0.15, 
          colors=brewer.pal(8, "Dark2"))

wordcloud(words = entire_desc_text, min.freq = 50)



