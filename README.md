# Natural-Language-Processing

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
