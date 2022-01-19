import os
import pathlib
import sqlite3
import nltk
import json
import pandas as pd

DATABASE_TABLES = ["foxnews", "aljazeera", "bcc"]

def get_all_articles():
    
    """
    Run spiders first in order for the database to be populated.
    Get all articles from the database.
    """

    db = sqlite3.connect(os.path.join(os.path.dirname(pathlib.Path(__file__).parent.resolve()) , "data", "db.sqlite3"))  # Establish connection to database
    
    fox_news_df = pd.read_sql("SELECT * FROM " + DATABASE_TABLES[0], db)  # Get all articles from the table fox_news
    aljazeera_df = pd.read_sql("SELECT * FROM " + DATABASE_TABLES[1], db)  # Get all articles from the table aljazeera
    bcc_df = pd.read_sql("SELECT * FROM " + DATABASE_TABLES[2], db)  # Get all articles from the table bcc

    return [fox_news_df, aljazeera_df, bcc_df]

def PoSTagger():

    """
    SYNTACTIC ANALYSIS.
    Run spiders first in order for the database to be populated.
    For every article in the database, get the article's text and tag it with PoS tags.
    Save the tagged text in the database.
    """

    # Download needed NLTK packages for PoS tagging
    nltk.download('averaged_perceptron_tagger')
    nltk.download('punkt')

    article_dfs = get_all_articles()  # Get all articles from the database

    for df in article_dfs:
        current_df_tags = []  # Each element is a json object containing a list of tagged words
        for _, row in df.iterrows():
            current_article_tags = []  # List to store the tagged words of the current article
            text = row['content']  # Get the article's text
            text_sentences = nltk.sent_tokenize(text)  # Split the text into sentences

            for sentence in text_sentences:
                tokenized_sentence = nltk.word_tokenize(sentence)  # Split the sentence into words
                current_article_tags.extend(nltk.pos_tag(tokenized_sentence))  # Append tagged text to list as a tuple of (word, tag)
            current_df_tags.append(json.dumps(current_article_tags))  # Append list of tagged words to the current_df_list
        
        assert len(current_df_tags) == len(df.index), "PoSTagger Error"  # Check that the list's length of tagged words is equal to the number of articles
        df['PoSTags'] = current_df_tags  # Add the list of tagged words to the dataframe
        # print(df)  # Print the dataframe to see the progress
    
    # Save the new dataframe to the database
    db = sqlite3.connect(os.path.join(os.path.dirname(pathlib.Path(__file__).parent.resolve()) , "data", "db.sqlite3"))  # Establish connection to database

    for df, table in zip(article_dfs, DATABASE_TABLES):
        df.to_sql(table, db, if_exists='replace', index=False)  # Insert dataframe to database. Replace table if it exists

if __name__ == '__main__':

    PoSTagger()
    print("PoS Tagging finished successfully!")
