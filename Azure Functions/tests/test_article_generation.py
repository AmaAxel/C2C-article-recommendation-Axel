import unittest
import sys
import os

from newsapi.newsapi_client import NewsApiClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from article_generation_TimerTrigger.clean_article import clean_content
from article_generation_TimerTrigger.extract_content import extract_to_dict



class TestExtractedArticle(unittest.TestCase):

    """"
    This test checks that the data we are scrapping from the BBC is consistant with the 
    dictionary format our functions are using
    """
    def test_extracted_article_structure(self):

        newsapi_key = '6fdb9fb9f5154d1c8073d732a744fb9f'
        # Search for articles using the everything endpoint
        newsapi = NewsApiClient(api_key=newsapi_key) 

        # Search for articles using the everything endpoint
        articles = newsapi.get_everything(sources='bbc-news')

        # Retrieve the full content of each article using the urlToImage field
        for article in articles['articles']:
            article = extract_to_dict(article)

            # Check if article is a dictionary
            self.assertIsInstance(article, dict)

            # Check if article has the expected keys
            expected_keys = ['title', 'description', 'publishedAt', 'content']
            for key in expected_keys:
                self.assertIn(key, article)

            # Check if none of the values are empty strings
            for key, value in article.items():
                self.assertNotEqual(value, '', f"Value for '{key}' is an empty string.")

            break


if __name__ == '__main__':
    unittest.main()