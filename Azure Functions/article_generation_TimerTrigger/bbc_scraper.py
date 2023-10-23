from newspaper import Config, Article
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re


class BBCArticleScraper:

    """
    The scrapper has to a list of dictionaries 
    with keys 'title', 'publishedAt', 'section', 'URL', 'description' and 'content'
    """

    def __init__(self):
        self.config = Config()
        self.config.memoize_articles = False  # Disable article caching
        self.config.language = 'en'  # Set the language to English
        self.main_url = 'https://www.bbc.com/news'
        
    def clean_bbc_articles(self, article_dict):
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
        # truncate the end of the article as it contains all of of rubbish not related to the article
        shortened_str = text[:-1300]
        # Find the last occurrence of ". "
        last_dot_index = shortened_str.rfind(". ")
        
        if last_dot_index != -1:
            # Remove everything following the last ". "
            text = shortened_str[:last_dot_index + 2]
        else:
            # If no ". " is found, keep the shortened string as is
            text = shortened_str
        
        article_dict['content'] = text
        
        return article_dict


    def get_bbc_article_content(self, url):
        # Send an HTTP GET request to the URL
        response = requests.get(url)

        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Identify the HTML elements that contain the article content
            content_elements = soup.find_all(['p'])  # Adjust as needed

            # Extract and clean the article content
            article_content = '\n'.join([element.get_text() for element in content_elements])

            # Remove everything after "Related Topics" (including "Related Topics" itself)
            article_content = article_content.split("Related Topics", 1)[0]

            # Use regular expression to add a period and space after lowercase-uppercase patterns
            article_content = re.sub(r'([a-z])([A-Z])', r'\1. \2', article_content)

            return article_content


    def scrape_bbc_articles(self):
        # Fetch the BBC website
        response = requests.get(self.main_url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # Get the current date
        yesterday_date = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')

        # Extract and parse articles
        article_list = []
        article_links = []

        # Find and extract article links from the BBC homepage
        for link in soup.find_all('a', class_='gs-c-promo-heading'):
            href = link.get('href')
            if href:
                article_links.append(f'https://www.bbc.com{href}')

        # Iterate through the article links and scrape the content
        for article_link in article_links:
            try:
                article = Article(article_link, config=self.config)
                article.download()
                article.parse()

                description = article.meta_data['description']
                section = article.meta_data['article']['section']
                title = article.meta_data['og']['title']
                url = article.meta_data['og']['url']
                publishedAt = article.publish_date

                # article.text does not contain the whole article for the bbc
                content = self.get_bbc_article_content(url)

                # Check if publishedAt is None and set it to the current date if so
                if publishedAt is None:
                    publishedAt = yesterday_date

                article_dict = {
                    'title': title,
                    'publishedAt': publishedAt,
                    'section': section,
                    'URL': url,
                    'description': description,
                    'content': content
                }
                
                article_dict = self.clean_bbc_articles(article_dict)

                # Save if the article is long enough
                if len(article_dict['content']) > 1000:
                    article_list.append(article_dict)
                    print(f'**INFO: article {url} successfully scrapped')

            except Exception as e:
                print(f'**INFO: An exception occurred: {str(e)}')

        return article_list