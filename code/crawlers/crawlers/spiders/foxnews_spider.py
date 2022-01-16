import os
import errno
import sqlite3
import scrapy
import pandas as pd

def clean_html(html_file):

    """
    DATA PREPROCESSING SYSTEM.
    Keep only the text from the html file. Keep all tex in <p> tags.
    """

    return ''.join(html_file.css('div.article-body p ::text').getall())

def create_folder(path):

    """
    Create a folder if it doesn't exist.
    """

    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

class FoxNewsSpider(scrapy.Spider):

    """
    Spider for scraping Fox News.
    """

    name = "foxnews"
    cleaned_articles = []  # Tuples of (article_title, article_url, article_text) to save them in database
    start_urls = [
        'https://www.foxnews.com/',
    ]

    def parse(self, response):

        """
        WEB SCRAPING SYSTEM.
        Get all articles from the homepage and parse them.
        """

        article_counter = 1
        articles_links = response.css('h2.title-color-default a')

        for article_link in articles_links:
            article_title = article_link.css('::text').get()
            article_url = article_link.css('::attr(href)').get()
            

            if "video" not in article_url:
                yield scrapy.Request(article_url, callback=self.parse_article, meta={'article_title': article_title, 'article_url': article_url, 'article_counter': article_counter})
                article_counter += 1
    
    def parse_article(self, respone):

        """
        Save the article's html and append tuple of (article_title, article_url, article_text) to self.cleaned_articles.
        """
        
        title = respone.meta.get('article_title') #  Title of the article
        url = respone.meta.get('article_url')  # Url of the article
        count = respone.meta.get('article_counter')  # Count to keep track of the number of articles scraped

        # Create folder if it doesn't exist and save the html file
        filename = os.getcwd() + f'../../../data/html/foxnews/{count}.html'
        create_folder(filename)

        # Save the html file
        with open(filename, "wb") as f:
            f.write(respone.body)
       
        # Append tuple of (article_title, article_url, article_text) to list of cleaned articles
        self.cleaned_articles.append((title, url, clean_html(respone)))

    def closed(self, reason):

        """
        Save tuples of (article_title, article_url, article_text) to database.
        """

        # Establish connection to database
        filename = os.getcwd() + f'../../../data/db.sqlite3'
        create_folder(filename)
        db = sqlite3.connect(filename)

        df = pd.DataFrame(self.cleaned_articles, columns=['title', 'url', 'content'])  # Create dataframe of cleaned articles
        df.to_sql('foxnews', db, if_exists='replace', index=False)  # Insert dataframe to database
