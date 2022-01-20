
import os
import pathlib
import time
import json
import random
import nltk
import xml.etree.ElementTree as ET
import pandas as pd
from tabulate import tabulate
import PosTagger
import preprocessing
import inverted_index

"""
Before running this script, go to codeA/crawlers run the following commands:
scrapy crawl foxnews
scrapy crawl aljazeera
scrapy crawl bcc
in order to populate the database.
"""

def get_all_lemmas():

    """
    Use existing lemmas to create queries.
    """

    all_lemmas = []
    articles_dfs = inverted_index.get_all_articles()  # Get all articles from the database

    for df in articles_dfs:
        for _, row in df.iterrows():
            lemmas = json.loads(row['lemmas_count'])

            for lemma in lemmas:
                if lemma not in all_lemmas:
                    all_lemmas.append(lemma)
    return all_lemmas

def create_queries(params):

    """
    Create queries based on the params and the lemmas onb the database
    """
    length_of_query, number_of_queries = params
    all_lemmas = get_all_lemmas()
    queries = []

    for i in range(number_of_queries):
        queries.append(random.sample(all_lemmas, k=length_of_query))
    return queries

def read_xml():

    """
    Read the inverted index xml file.
    """

    xml_path = os.path.join(os.path.dirname(pathlib.Path(__file__).parent.resolve()) , "dataA", "inverted_index.xml")
    tree = ET.parse(xml_path)  # Create element tree object
    root = tree.getroot()  # Get root element
    inverted_index_dict = {}

    for item in root:
        inverted_index_dict[item.attrib['name']] = {}  # Empy dictionary for each lemma

        for child in item:
            inverted_index_dict[item.attrib['name']][child.attrib['id']] = float(child.attrib['weight'])  # Add urls and weights to dictionary
    return inverted_index_dict

def answer_query(query, inverted_index_dict):

    """
    Given a query of lemmas, look up the urls that contain those words in the inverted index.
    If there are more than one word, the weight of a document which contains 2 or more words will be the sum of the two.
    The ansewer will be returned in descending order.
    """

    query = [lemma.lower() for lemma in query]
    answer = {}  # Dictionary of urls and their weights
    for lemma in query:
        if lemma in inverted_index_dict:
            for url in inverted_index_dict[lemma]:
                if url in answer:
                    answer[url] += inverted_index_dict[lemma][url]
                else:
                    answer[url] = inverted_index_dict[lemma][url]
    
    # Return a dataframe of (url, weight of lemma ..., total weight)
    final_answer = []  # List of lists [url, weight of lemma ..., total weight]
    for url in answer:
        temp_list = [url]
        for lemma in query:
            if lemma in inverted_index_dict and url in inverted_index_dict[lemma]:
                temp_list.append(inverted_index_dict[lemma][url])
            else:
                temp_list.append(0)
        temp_list.append(answer[url])
        final_answer.append(temp_list)
    
    pd.set_option('display.max_colwidth', None)
    df = pd.DataFrame(final_answer, columns=['url'] + query + ['total_weight'])
    df = df.sort_values(by=['total_weight'], ascending=False)
    return df

def create_inverted_index():

    """
    Run all scripts needed after crawling.
    """

    # ------------- Preprocessing and creating the inverted index. Inverted index is saved in the data folder as an xml file. -------------
    inverted_index_build_start = time.time()
    PosTagger.PoSTagger()
    preprocessing.preprocessing()
    preprocessing.lemmas_count()
    inverted_index.inverted_to_xml()
    inverted_index_build_end = time.time()
    print("Inverted index build time: " + str(inverted_index_build_end - inverted_index_build_start) + " seconds")

def preprocess_query(query):

    """
    Preprocess_query:
    PoSTagging, remove stopwords and lemmatization
    """

    # Download needed NLTK packages for removing stop words
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('omw-1.4')
    lemmatizer = nltk.stem.WordNetLemmatizer()
    stop_words = nltk.corpus.stopwords.words('english')

    to_return = []
    query = query.split(",")  # Split the query by comma
    query = [lemma.lower() for lemma in query]  # Convert to lowercase

    pos_tags = nltk.pos_tag(query)  # Get the part of speech tags
    query = [item for item in pos_tags if item[0] not in stop_words and item[1] in preprocessing.OPEN_CLASS_CATEGORIES]  # Remove stop words and close categories

    for item in query:
        to_return.append(lemmatizer.lemmatize(item[0], pos=preprocessing.POS_TAGS[item[1][0:2]]))  # Lemmatize the words
    return to_return

if __name__ == "__main__":

    create_inverted_index()  # Create the inverted index and print the time it took to build it
    inverted_index_dict = read_xml()  # Read the inverted index xml file

    # -------------------------------------------------- Create queries and print timings --------------------------------------------------
    user_input = input("Timings or custom input? (t/c): ")

    if user_input == "c":
        query = input("Enter query (english words separated by comma): ")
        preprocessed_query = preprocess_query(query)  # Preprocess the query to remove stop words and lemmatize
        answer = answer_query(preprocessed_query, inverted_index_dict)
        print(tabulate(answer, showindex=False, headers=answer.columns))
    elif user_input == "t":
        queries_list = [(1, 20), (2, 20), (3, 30), (4, 30)]  # Tuples of (query length, number of queries)

        for params in queries_list:
            queries = create_queries(params)  # Create queries of the given length and number of queries

            start_time = time.time()
            for query in queries:
                answer = answer_query(query, inverted_index_dict)
                # print("\n")
                # print(tabulate(answer, showindex=False, headers=answer.columns))
                # print("\n")
            end_time = time.time()
            print("Query length: " + str(params[0]) + " | Number of queries: " + str(params[1]) + " | Time: " + str((end_time - start_time) / params[1]) + " seconds")
    else:
        print("Invalid input")
