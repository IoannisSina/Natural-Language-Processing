import os
import pathlib
import sqlite3
import string
import nltk
import json
import pandas as pd

DATABASE_TABLES = ["foxnews", "aljazeera", "bcc"]
OPEN_CLASS_CATEGORIES = ["JJ", "JJR", "JJS", "RB", "RBR", "RBS", "NN", "NNS", "NNP", "NNPS", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "FW"]
POS_TAGS = {'NN': nltk.corpus.wordnet.NOUN, 'JJ': nltk.corpus.wordnet.ADJ, 'VB': nltk.corpus.wordnet.VERB, 'RB': nltk.corpus.wordnet.ADV, 'FW': nltk.corpus.wordnet.NOUN}
PANCTUATION = string.punctuation

def get_all_articles():
    
    """
    Run spiders first in order for the database to be populated.
    Then run PoSTagger.
    Get all articles from the database.
    """

    db = sqlite3.connect(os.path.join(os.path.dirname(pathlib.Path(__file__).parent.resolve()) , "dataA", "db.sqlite3"))  # Establish connection to database
    
    fox_news_df = pd.read_sql("SELECT * FROM " + DATABASE_TABLES[0], db)  # Get all articles from the table fox_news
    aljazeera_df = pd.read_sql("SELECT * FROM " + DATABASE_TABLES[1], db)  # Get all articles from the table aljazeera
    bcc_df = pd.read_sql("SELECT * FROM " + DATABASE_TABLES[2], db)  # Get all articles from the table bcc

    return [fox_news_df, aljazeera_df, bcc_df]

def preprocessing():

    """
    PREPROCESSING SYSTEM.
    Run spiders first in order for the database to be populated.
    Then run PoSTagger.
    Remove stop words, closed tag category words and punctuation and save the infomration to the database.
    """

    # Download needed NLTK packages for removing stop words
    nltk.download('stopwords')
    stop_words = nltk.corpus.stopwords.words('english')

    article_dfs = get_all_articles()  # Get all articles from the database

    for df in article_dfs:
        current_df_cleaned_tags = []  # Each element is a json object containing a list of tagged words

        for _, row in df.iterrows():
            postags = json.loads(row['PoSTags'])  # Get the list of tagged words in list format
            cleaned_tags = [item for item in postags if item[0] not in stop_words and item[1] in OPEN_CLASS_CATEGORIES]  # Remove stop words and closed tag category words
            panc_cleaned_tags = [item for item in cleaned_tags if not any(symbol in item[0] for symbol in PANCTUATION)]  # Remove punctuation
            panc_cleaned_tags = [item for item in panc_cleaned_tags if item[0].encode("ascii", "ignore").decode() != ""]  # Remove unicode characters
            lower_cleaned_tags = [(item[0].lower(), item[1]) for item in panc_cleaned_tags]  # Convert all words to lower case
            current_df_cleaned_tags.append(json.dumps(lower_cleaned_tags))  # Convert list to json object and append it
        
        assert len(current_df_cleaned_tags) == len(df.index), "Pre-processing Error"  # Check that the list's length of cleaned tagged words is equal to the number of articles
        df['PoSTags_cleaned'] = current_df_cleaned_tags  # Add the list of cleaned tagged words to the dataframe
    
    # Save the new dataframe to the database
    db = sqlite3.connect(os.path.join(os.path.dirname(pathlib.Path(__file__).parent.resolve()) , "dataA", "db.sqlite3"))  # Establish connection to database

    for df, table in zip(article_dfs, DATABASE_TABLES):
        df.to_sql(table, db, if_exists='replace', index=False)  # Insert dataframe to database. Replace table if it exists

    return article_dfs

def lemmas_count():

    """
    LEMMATIZATION SYSTEM.
    Count lemmas and save the infomration to the database.
    Run spiders first in order for the database to be populated.
    Then run PoSTagger.
    """

    # Download needed NLTK packages for lemmatization
    nltk.download('wordnet')
    nltk.download('omw-1.4')
    lemmatizer = nltk.stem.WordNetLemmatizer()

    cleaned_dfs = get_all_articles() # Get the new dfs after preprocessing

    for df in cleaned_dfs:
        current_df_lemmas_count = []  # A list containing dictionaries of lemmas and their counts for each article

        for _, row in df.iterrows():
            current_article_cleaned_postags = json.loads(row['PoSTags_cleaned'])  # Get the list of cleaned tagged words in list format
            current_article_lemmas_count = {}  # A dictionary containing lemmas and their counts for each article

            for postag_word in current_article_cleaned_postags:
                word = postag_word[0]
                tag = postag_word[1]
                lemmatized_word = lemmatizer.lemmatize(word, pos=POS_TAGS[tag[0:2]])  # Lemmatize the word
                if word == "needs":
                    print("tag: " + tag)

                if lemmatized_word in current_article_lemmas_count:
                    current_article_lemmas_count[lemmatized_word] += 1
                else:
                    current_article_lemmas_count[lemmatized_word] = 1
            current_df_lemmas_count.append(json.dumps(current_article_lemmas_count))  # Convert dictionary to json object and append it

        assert len(current_df_lemmas_count) == len(df.index), "Lemmatizer Error"  # Check that the list's length of lemmas count is equal to the number of articles
        df['lemmas_count'] = current_df_lemmas_count  # Add the list of dictionaries to the dataframe
    
    # Save the new dataframe to the database
    db = sqlite3.connect(os.path.join(os.path.dirname(pathlib.Path(__file__).parent.resolve()) , "dataA", "db.sqlite3"))  # Establish connection to database

    for df, table in zip(cleaned_dfs, DATABASE_TABLES):
        df.to_sql(table, db, if_exists='replace', index=False)  # Insert dataframe to database. Replace table if it exists

if __name__ == "__main__":
    preprocessing()
    lemmas_count()
    print("Preprocessing anf Lemmatization finished successfully!")