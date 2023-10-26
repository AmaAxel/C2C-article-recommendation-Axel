import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from article_generation_TimerTrigger.bbc_scraper import BBCArticleScraper
from article_generation_TimerTrigger.lemonde_scraper import LeMondeArticleScraper

class TestExtractedArticle(unittest.TestCase):
    """
    This test checks that the data we are scraping from different sources is consistent with the
    dictionary format our functions are using.
    """

    def setUp(self):
        # Initialize the scrapers here, which can be accessed by test methods
        self.bbc_scraper = BBCArticleScraper()
        self.lemonde_scraper = LeMondeArticleScraper()

    def test_extracted_bbc_article_structure(self):
        articles = self.bbc_scraper.scrape_articles()

        for article in articles:
            self.assertIsInstance(article, dict)

            expected_keys = ['title', 'publishedAt', 'section', 'URL', 'description', 'content']
            for key in expected_keys:
                self.assertIn(key, article)

            for key, value in article.items():
                self.assertNotEqual(value, '', f"Value for '{key}' is an empty string.")

    def test_extracted_lemonde_article_structure(self):
        articles = self.lemonde_scraper.scrape_articles()

        for article in articles:
            self.assertIsInstance(article, dict)

            expected_keys = ['title', 'publishedAt', 'section', 'URL', 'description', 'content']
            for key in expected_keys:
                self.assertIn(key, article)

            for key, value in article.items():
                self.assertNotEqual(value, '', f"Value for '{key}' is an empty string.")

if __name__ == '__main__':
    unittest.main()
