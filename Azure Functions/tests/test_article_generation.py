import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from article_generation_TimerTrigger.bbc_scraper import BBCArticleScraper



class TestExtractedArticle(unittest.TestCase):

    """"
    This test checks that the data we are scrapping from the BBC is consistant with the 
    dictionary format our functions are using
    """
    def test_extracted_article_structure(self):

        bbc_scraper = BBCArticleScraper()
        articles = bbc_scraper.scrape_bbc_articles()

        # Retrieve the full content of each article using the urlToImage field
        for article in articles:

            # Check if article is a dictionary
            self.assertIsInstance(article, dict)

            # Check if article has the expected keys
            expected_keys = ['title', 'publishedAt', 'section', 'URL', 'description', 'content']
            for key in expected_keys:
                self.assertIn(key, article)

            # Check if none of the values are empty strings
            for key, value in article.items():
                self.assertNotEqual(value, '', f"Value for '{key}' is an empty string.")

if __name__ == '__main__':
    unittest.main()