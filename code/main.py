
import time
import PosTagger
import preprocessing
import inverted_index

"""
Before running this script, go to code/crawlers run the following commands:
scrapy crawl foxnews
scrapy crawl aljazeera
scrapy crawl bcc
in order to populate the database.
"""

# ------------- Preprocessing and creating the inverted index. Inverted index is saved in the data folder as an xml file. -------------
inverted_index_build_start = time.time()
PosTagger.PoSTagger()  # SYNTACTIC ANALYSIS SYSTEM
preprocessing.preprocessing()  # PREPROCESSING SYSTEM
preprocessing.lemmas_count()  # PREPROCESSING SYSTEM
inverted_index.inverted_to_xml()  # INVERTED INDEX SYSTEM. INVERTED INDEX IS SAVED IN THE DATA FOLDER AS AN XML FILE
inverted_index_build_end = time.time()
print("Inverted index build time: " + str(inverted_index_build_end - inverted_index_build_start) + " seconds")
# -------------------------------------------------------------------------------------------------------------------------------------