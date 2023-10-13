import requests
from bs4 import BeautifulSoup


def extract_to_dict(article):
    # Make sure the article has a URL
    if 'urlToImage' in article:
        # Use the URL to fetch the full article content
        response = requests.get(article['url'])
        soup = BeautifulSoup(response.content, 'html.parser')
        try:
            # get content
            article['content'] = soup.find('article').get_text()

            article = {
                'title': article['title'],
                'description': article['description'],
                'publishedAt': article['publishedAt'],
                'content': article['content']
                    }
            
            return article
            
        except:
            return