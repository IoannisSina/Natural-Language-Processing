## Description - Part A :zap:

1. Use scrapy libary to crawl recent articles from three famous news websites. HTML files are cleaned and only text is kept and saved.
2. Use PoSTagger to tag every word in all tokenized articles.
3. Represent texts as articles.
4. Create an inverted index and save it.
5. Use the inverted index to answer given queries (strings). TF-IDF metric was used to return relevan articles from the inverted index.

## Steps to run part A :runner:

Clone repository and cd to the folder:
~~~
git clone https://github.com/IoannisSina/Natural-Language-Processing
cd Natural-Language-Processing
~~~

Create virtual enviroment and activate it:
~~~
python3 -m venv env
source env/bin/activate  # Activate on Linux
env\Scripts\activate  # Activate on Windows
~~~

Install requirements and cd to code/crawlers:
~~~
pip install -r requirements.txt
cd codeA/crawlers
~~~

Run spiders:
~~~
scrapy crawl foxnews
scrapy crawl aljazeera
scrapy crawl bcc
~~~

Cd to code and run main.py:
~~~
cd ..
python3 main.py
~~~
