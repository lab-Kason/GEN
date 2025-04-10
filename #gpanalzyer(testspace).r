# ----------------------------
# Aging in Hong Kong: Text Classification
# STAT 2610SEF Course Project
# ----------------------------

# Load libraries
library(tm)        # Text mining
library(dplyr)     # Data manipulation
library(ggplot2)   # Visualization
library(wordcloud) # Word cloud
library(RColorBrewer) # Color palettes for word clouds

# ----------------------------
# STEP 1: Load & Preprocess Data
# ----------------------------

# Set working directory to folder containing your .txt files
setwd("C:/Users/admin/Desktop/ConvertedFiles")

# Read all .txt files
file_list <- list.files(pattern = "\\.txt$")
articles <- lapply(file_list, function(file) {
  paste(readLines(file, warn = FALSE, encoding = "UTF-8"), collapse = " ")
})

# Create a dataframe
docs <- data.frame(
  doc_id = sub("\\.txt$", "", file_list),  # Remove .txt extension
  text = unlist(articles),
  stringsAsFactors = FALSE
)

# Clean text: lowercase, remove punctuation/numbers/stopwords
corpus <- VCorpus(VectorSource(docs$text)) %>%
  tm_map(content_transformer(tolower)) %>%
  tm_map(removePunctuation) %>%
  tm_map(removeNumbers) %>%
  tm_map(removeWords, c(stopwords("en"), "hong kong", "said", "of", "the", "in", "and", "to", "is")) %>%
  tm_map(stripWhitespace)

# Remove empty documents
corpus <- corpus[!sapply(corpus, function(doc) length(content(doc)) == 0)]
   
# Update the cleaned text back to the `docs` dataframe
docs$text <- sapply(corpus, as.character)

# ----------------------------
# STEP 2: Define Hong Kong Aging Keywords
# ----------------------------

categories <- list(
  Healthcare = c(
    "care", "health", "geriatric services", "health institutions", 
    "community nursing", "subvented care", "residential care",
    "health management", "elderly health", "medical support", "institutions"
  ),
  
  Policy = c(
    "population", "ageing", "government", "economic policy", 
    "labour policies", "social security", "savings schemes", 
    "retirement protection", "elderly poverty alleviation", 
    "projected demographics", "aging", "initiatives"
  ),
  
  Housing = c(
    "housing", "residential", "mobility", "elderly housing", 
    "senior residential", "housing mobility", "age-friendly architecture", 
    "Hong Kong Housing Authority", "subsidized flats", "elderly hostels", 
    "multi-generational housing", "residents' needs", "barrier-free design"
  ),
  
  Technology = c(
    "telemedicine", "AI-powered eldercare", "wearable health tracker",
    "Jockey Club Gerontechnology", "smart elderly homes", 
    "fall detection systems", "robotic care assistants"
  )
)

# ----------------------------
# STEP 3: Classify Articles
# ----------------------------

# Create Document-Term Matrix (DTM)
dtm <- DocumentTermMatrix(corpus)
dtm_matrix <- as.matrix(dtm)

# Calculate category scores
category_scores <- sapply(categories, function(keys) {
  matched_terms <- intersect(colnames(dtm_matrix), keys)
  if (length(matched_terms) > 0) {
    rowSums(dtm_matrix[, matched_terms, drop = FALSE])
  } else {
    rep(0, nrow(dtm_matrix))  # Handle no matches
  }
})

# Assign dominant category to each article
docs$category <- colnames(category_scores)[max.col(category_scores, ties.method = "first")]

# Label unclassified articles (no keywords matched)
docs$category[rowSums(category_scores) == 0] <- "Unclassified"

# ----------------------------
# STEP 4: Analyze & Visualize
# ----------------------------

# 1. Category Distribution (Bar Chart)
category_summary <- docs %>%
  group_by(category) %>%
  summarise(count = n()) %>%
  mutate(percentage = round(count / sum(count) * 100, 1))

ggplot(category_summary, aes(x = reorder(category, -count), y = count, fill = category)) +
  geom_bar(stat = "identity") +
  geom_text(aes(label = paste0(count, " (", percentage, "%)"), vjust = -0.5)) +
  labs(title = "Aging-Related Topics in Hong Kong Articles",
       x = "Category", y = "Number of Articles") +
  theme_minimal(base_size = 14) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

# Ensure the output directory exists
output_dir <- "C:/Users/admin/Desktop/analysis result"
if (!dir.exists(output_dir)) {
  dir.create(output_dir)
}

# Save plot
ggsave(file.path(output_dir, "category_distribution.png"), width = 10, height = 6)

# Generate a word cloud for each .txt file
for (i in seq_along(docs$text)) {
  # Extract the text of the current document
  doc_text <- docs$text[i]
  
  # Skip if the document text is empty
  if (nchar(doc_text) == 0) next
  
  # Generate the word cloud
  words <- unlist(strsplit(doc_text, "\\s+"))  # Split text into words
  word_freq <- table(words)  # Calculate word frequencies
  
  # Skip if there are no valid words
  if (length(word_freq) == 0) next
  
  # Save the word cloud as an image
  output_file <- file.path(output_dir, paste0("wordcloud_doc_", docs$doc_id[i], ".png"))
  png(output_file, width = 800, height = 600)
  wordcloud(
    words = names(word_freq),          # Words to display
    freq = as.numeric(word_freq),      # Frequencies of the words
    max.words = 100,                   # Display up to 100 words
    colors = brewer.pal(8, "Dark2"),   # Use a colorful palette
    scale = c(4, 0.8),                 # Adjust font size range
    random.order = FALSE               # Order words by frequency
  )
  dev.off()
}

# ----------------------------
# STEP 5: Save Outputs
# ----------------------------

# Save classified articles
write.csv(docs, file.path(output_dir, "hk_aging_classified_articles.csv"), row.names = FALSE)

# Save   info for reproducibility
sink(file.path(output_dir, "session_info.txt"))
sessionInfo()
sink()

# Print out the most common words in each file as a table
sink(file.path(output_dir, "common_words_per_file.txt"))
for (i in seq_along(docs$text)) {
  # Extract the text of the current document
  doc_text <- docs$text[i]
  
  # Skip if the document text is empty
  if (nchar(doc_text) == 0) next
  
  # Calculate word frequencies
  words <- unlist(strsplit(doc_text, "\\s+"))  # Split text into words
  word_freq <- sort(table(words), decreasing = TRUE)  # Sort by frequency
  
  # Print the document ID and the top words
  cat("Document ID:", docs$doc_id[i], "\n")
  print(head(word_freq, 10))  # Show the top 10 most common words
  cat("\n")
}
sink()