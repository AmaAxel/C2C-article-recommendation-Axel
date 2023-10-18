import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from article_similarity_EventHubTrigger.compute_similarity import compute_similarity

from sentence_transformers import SentenceTransformer

class TestComputeSimilarity(unittest.TestCase):


    """
    This test checks if your compute_similarity() function returns consistent similarity values
    """

    def setUp(self):
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.article_A = {
            'title': 'Ukraine war: Russia attacks Avdiivka stronghold in eastern Ukraine',
            'description': 'Russian troops have launched a major offensive on the town of Avdiivka in eastern Ukraine.',
            'publishedAt': '2023-10-16',
            'content': 'Although Russia and its proxy forces have occupied Donetsk city since 2014, they have been unable to use its resources as a key military communications hub because it is too close to the front line. By capturing Avdiivka, the occupying force could push the front line away...'
        }
        self.article_B = {
            'title': 'Ukraine war: Every family in Hroza village affected by missile attack',
            'description': "People from every family in Ukraine's north-eastern village of Hroza have been affected by a missile attack that killed 52 people on Thursday, Interior Minister Ihor Klymenko has said...",
            'publishedAt': '2023-10-16',
            'content': "Ukraine's defence ministry blamed Russia for the attack, and said there were no military targets in the area...'"
        }
        self.article_C = {
            'title': "Madonna's Celebration Tour review: The Queen of pop brings out her crown jewels",
            'description': "She's known as the Queen of Pop and, on the opening night of her Celebration World Tour, Madonna brought out her crown jewels...",
            'publishedAt': '2023-10-12',
            'content': 'Aided by vintage costumes and archive footage, she time-travelled through a career that took her from penniless wannabe to musical icon, while highlighting her impact on popular culture...'
        }

    def test_similarity_above_threshold(self):
        similarity = compute_similarity(self.model, self.article_A, self.article_B)
        self.assertGreater(similarity, 0.999)

    def test_similarity_below_threshold(self):
        similarity = compute_similarity(self.model, self.article_A, self.article_C)
        self.assertLess(similarity, 0.2)

if __name__ == '__main__':
    unittest.main()
