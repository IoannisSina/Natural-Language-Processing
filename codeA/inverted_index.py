import os
import pathlib
import sqlite3
import json
import math
from xml.dom import minidom
import pandas as pd

DATABASE_TABLES = ["foxnews", "aljazeera", "bcc"]

def get_all_articles():
    
    """
    Run spiders first in order for the database to be populated.
    Then run PoSTagger and Then run preprocessing.
    Get all articles from the database.
    """

    db = sqlite3.connect(os.path.join(os.path.dirname(pathlib.Path(__file__).parent.resolve()) , "dataA", "db.sqlite3"))  # Establish connection to database
    
    fox_news_df = pd.read_sql("SELECT * FROM " + DATABASE_TABLES[0], db)  # Get all articles from the table fox_news
    aljazeera_df = pd.read_sql("SELECT * FROM " + DATABASE_TABLES[1], db)  # Get all articles from the table aljazeera
    bcc_df = pd.read_sql("SELECT * FROM " + DATABASE_TABLES[2], db)  # Get all articles from the table bcc

    return [fox_news_df, aljazeera_df, bcc_df]

def count_docs_containing_lemmas():

    """
    Return a dictionary {lemma: Number of documents containing lemma}
    """

    articles_dfs = get_all_articles()  # Get all articles from the database
    to_return = {}

    for df in articles_dfs:
        for _, row in df.iterrows():
            lemmas = json.loads(row['lemmas_count'])

            for lemma in lemmas:
                if lemma in to_return:
                    to_return[lemma] += 1
                else:
                    to_return[lemma] = 1
    return to_return

def test_lemmas_count():

    """
    Ensure that tf_idf_dict has as many lemmas as the database
    """

    df = lemmas_tf_idf()
    lemmas_count_1 = len(df.index)
    lemmas_count_2 = len(count_docs_containing_lemmas())
    assert lemmas_count_1 == lemmas_count_2, "Lemmas count are not equal"

def lemmas_tf_idf():

    """
    INVERTED INDEX SYSTEM.
    Run spiders first in order for the database to be populated.
    Then run PoSTagger and Then run preprocessing.
    For every lemma, calculate the tf-idf score and save the infomration to the database.
    Create new table lemmas. Save tuples (lemma, {doc_id: tf-idf, ...}) to the table.
    TF = (Number of times the word appears in the document) / (Total number of words in the document)
    IDF = log(Total number of documents / Number of documents containing the word)
    We already know the number of documents, the number of times the word appears in each document and the total number of words in each document.
    The total number of words in each document is equal to the length of PoSTags_cleaned list.
    We have only to calculate the Number of documents containing each lemma.
    """
    
    articles_dfs = get_all_articles()  # Get all articles from the database

    # Data needed for tf-idf
    articles_count = len(articles_dfs[0].index) + len(articles_dfs[1].index) + len(articles_dfs[2].index)  # Total number of articles
    lemma_in_docs_counter = count_docs_containing_lemmas()  # Dictionary {lemma: Number of documents containing lemma}

    tf_idf = {}  # Dictionary {lemma: {doc_id: tf-idf, ...}}

    for df in articles_dfs:
        for _, row in df.iterrows():
            lemmas = json.loads(row['lemmas_count'])

            for lemma in lemmas:
                if lemma not in tf_idf:
                    tf_idf[lemma] = {}  # Create new dictionary for lemma if lemma is not in tf_idf yet
                
                # Add tf-idf score to the dictionary for the specific document
                tf_idf[lemma][row['url']] = (lemmas[lemma] / len(json.loads(row['PoSTags_cleaned']))) * (math.log(articles_count / (1 + lemma_in_docs_counter[lemma])))
    
    # Convert tf_idf dictionary to a list of tuples [(lemma, {doc_id: tf-idf, ...}), ...] in order to save it to the database
    dict_items = tf_idf.items()
    tf_idf_list = list(dict_items)
    tf_idf_list = [(lemma, json.dumps(tf_idf)) for lemma, tf_idf in tf_idf_list]

    db = sqlite3.connect(os.path.join(os.path.dirname(pathlib.Path(__file__).parent.resolve()) , "dataA", "db.sqlite3"))  # Establish connection to database

    df = pd.DataFrame(tf_idf_list, columns=['lemma', 'tf_idf'])  # Create dataframe of cleaned articles
    df.to_sql('lemmas', db, if_exists='replace', index=False)  # Insert dataframe to database. Replace table if it exists

    return tf_idf  # Return list of tuples [(lemma, {doc_id: tf-idf, ...}), ...] to save it as xml file

def inverted_to_xml():

    """
    Saves the inverted index to an xml file.
    """

    xml_path = os.path.join(os.path.dirname(pathlib.Path(__file__).parent.resolve()) , "dataA", "inverted_index.xml")
    lemmas_tf_idf_dict = lemmas_tf_idf()  # Get the list of tuples [(lemma, {doc_id: tf-idf, ...}), ...] from the database

    root = minidom.Document()  # Create file
    xml = root.createElement('inverted_index')  # Create root element
    root.appendChild(xml) 

    for lemma in lemmas_tf_idf_dict:
        lemma_child = root.createElement('lemma')  # Create child element
        lemma_child.setAttribute('name', lemma)  # Set name attribute

        # Add all documents containing the lemma
        for doc in lemmas_tf_idf_dict[lemma]:
            doc_child = root.createElement('document')  # create child element
            doc_child.setAttribute('id', doc)  # Set id attribute (url)
            doc_child.setAttribute('weight', str(lemmas_tf_idf_dict[lemma][doc]))  # Set weight (tf-idf) attribute
            xml.appendChild(lemma_child)  # append child to parent
            lemma_child.appendChild(doc_child)  # append child to parent
        xml.appendChild(lemma_child)  # append child to parent

    xml_str = root.toprettyxml(indent ="\t")
    
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_str)

if __name__ == "__main__":
    # test_lemmas_count()  # Test lemmas_tf_idf()
    inverted_to_xml()
    print("Inverted index saved to xml file and to the database!")