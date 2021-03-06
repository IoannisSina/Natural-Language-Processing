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

    return ' '.join(html_file.css("div.wysiwyg--all-content p ::text").getall())

def create_folder(path):

    """
    Create a folder if it doesn't exist.
    """

    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

class AljazeeraSpider(scrapy.Spider):

    """
    Spider for scraping Al Jazeera.
    """

    name = "aljazeera"
    cleaned_articles = []  # Tuples of (article_title, article_url, article_text) to save them in database
    start_urls = [
        'https://www.aljazeera.com/',
    ]

    def parse(self, response):

        """
        WEB SCRAPING SYSTEM.
        Get all articles from https://www.aljazeera.com/ homepage and parse them.
        """

        article_counter = 1
        articles_links = response.css("a.u-clickable-card__link")

        for article_link in articles_links:
            article_title = article_link.css('span::text').get()
            article_url = article_link.css('::attr(href)').get()

            # If the article is not a gallery, scrape it
            if "gallery" not in article_url:
                yield response.follow(article_url, callback=self.parse_article, meta={'article_title': article_title, 'article_counter': article_counter})
                article_counter += 1
    
    def parse_article(self, respone):

        """
        Save the article's html and append tuple of (article_title, article_url, article_text) to self.cleaned_articles.
        """
        
        title = respone.meta.get('article_title')  # Title of the article
        url = respone.url  # Url of the article
        count = respone.meta.get('article_counter')  # Count to keep track of the number of articles scraped

        # Create folder if it doesn't exist and save the html file. Works for both Windows and Linux
        filename = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "dataA", "html", "aljazeera", "")
        create_folder(filename)  # Create folder if it doesn't exist

        # Save the html file
        with open(os.path.join(filename, f"{count}.html"), "wb") as f:
            f.write(respone.body)
       
        # Append tuple of (article_title, article_url, article_text) to list of cleaned articles only if title and content are not empty
        content = clean_html(respone)
        if title and content:
            self.cleaned_articles.append((title, url, content))

    def closed(self, reason):

        """
        Save tuples of (article_title, article_url, article_text) to database.
        """

        # Create folder if it doesn't exist and save the html file. Works for both Windows and Linux
        filename = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "dataA", "")
        create_folder(filename)

        db = sqlite3.connect(os.path.join(filename, "db.sqlite3"))  # Establish connection to database

        df = pd.DataFrame(self.cleaned_articles, columns=['title', 'url', 'content'])  # Create dataframe of cleaned articles
        df.to_sql('aljazeera', db, if_exists='replace', index=False)  # Insert dataframe to database. Replace table if it exists
