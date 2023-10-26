from newspaper import Config, Article
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import logging


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

    def check_validity(self, article_dict):
        validity = True
        yesterday_date = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
        if len(article_dict['content']) < 1000 \
                or article_dict['publishedAt'] != yesterday_date \
                or 'Video' in article_dict['description'] \
                or 'Lecture du Monde en cours sur un autre appareil' in article_dict['content']:
            validity = False
        
        return validity
    
    def remove_text_before(self, text, substrings):
        for substring in substrings:
            index = text.find(substring)
            if index != -1:
                text = text[index + len(substring):]
        return text
    
    def remove_text_after(self, text, substrings):
        for substring in substrings:
            index = text.find(substring)
            if index != -1:
                text = text[index:]
        return text
    
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
        # finally replace double quotes by simple quotes back
        text = text.replace('"', "'")

        # remove the beginning of the article (about the main headlines/unrelated to article)
        substrings_remove_before = [
            ". Subscribers only.",
            " Le Monde with AFP. ",
            " Le Monde. "
        ]
        text = self.remove_text_before(text, substrings_remove_before)

        # remove everything that is after those substrings (about the main headlines)
        substrings_remove_after = [
            " The rest is for subscribers only",
            "Lecture du Monde en cours sur un autre appareil"
        ]
        # Already a subscriber ? Sign in


        text = self.remove_text_after(text, substrings_remove_after)

        article_dict['content'] = text

        return article_dict

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
                validity = self.check_validity(article_dict)

                if validity:
                    article_list.append(article_dict)
                    logging.info(f'**INFO: article {url} successfully scrapped')

            except Exception as e:
                logging.info(f'**INFO: An exception occurred: {str(e)}')

        return article_list