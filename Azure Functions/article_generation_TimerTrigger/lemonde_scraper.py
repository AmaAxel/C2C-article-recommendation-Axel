from newspaper import Config, Article
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

class LeMondeArticleScraper:

    """
    The scrapper has to a list of dictionaries 
    with keys 'title', 'publishedAt', 'section', 'URL', 'description' and 'content'
    """

    def __init__(self):
        self.config = Config()
        self.config.memoize_articles = False
        self.config.language = 'en'
        self.main_url = 'https://www.lemonde.fr/en/'

    def clean_LeMonde_articles(self, article_dict):
        # remove special characters
        text = article_dict['content'].replace('\n', '. ').replace("'", '"')
        # remove all the spaces before a dots
        text = re.sub(r'\s+\.', '.', text)
        # remove all the spaces before a dots
        text = re.sub(r'\.\s+', '.', text)
        # remove multiple dots
        text = re.sub(r'\.{2,}', '.', text)
        # add a space after each dot
        text = re.sub(r'\.(?=\S)', '. ', text)

        # remove the end of the article (about subscribing and other non-relevant text)
        index = text.find("Already a subscriber ?")
        # Check if the substring is found
        if index != -1:
            # Extract the portion of the string before the target substring
            text = text[:index]
        else:
            # If the substring is not found, keep the original string
            text = text

        article_dict['content'] = text

    def get_LeMonde_article_content(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            content_elements = soup.find_all(['p'])
            article_content = '\n'.join([element.get_text() for element in content_elements])
            return article_content

    def scrape_LeMonde_articles(self):
        response = requests.get(self.main_url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        yesterday_date = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')

        article_list = []

        sub_urls = []

        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href.startswith(self.main_url):
                sub_urls.append(href)

        for url in sub_urls:
            try:
                article = Article(url, config=self.config)
                article.download()
                article.parse()

                description = article.meta_data['og']['description']
                content = self.get_LeMonde_article_content(url)
                title = article.title
                publishedAt = article.meta_data['og']['article']['published_time']
                publishedAt = datetime.fromisoformat(publishedAt).strftime('%Y-%m-%d')
                section = article.meta_data['og']['article']['section']

                article_dict = {
                    'title': title,
                    'publishedAt': publishedAt,
                    'section': section,
                    'URL': url,
                    'description': description,
                    'content': content
                }

                article_dict = self.clean_LeMonde_articles(article_dict)

                if len(content) > 1000 and publishedAt == yesterday_date:
                    article_list.append(article_dict)
                    print(f'**INFO: article {url} successfully scrapped')

            except Exception as e:
                print(f'**INFO: An exception occurred: {str(e)}')

        return article_list