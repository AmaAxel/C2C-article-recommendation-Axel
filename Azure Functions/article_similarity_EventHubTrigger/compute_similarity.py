
from sentence_transformers import SentenceTransformer, util


def compute_similarity(model, old_article, new_article):

    """"
    Old and new articles are dictionaries with keys title, description, publishedAt and content
    old_article is an article already in the graph database
    new_article is the incoming article that we want to compare to the old article already in the database
    Returns a float (value of similarity between the two articles)
    """

    ############# SECTION TO BE COMPLETED BY CONSULTANT ################

    content_enriched = old_article['title'] + ' ' + old_article['description'] + ' ' + old_article['content']
    new_content_enriched = new_article['title'] + ' ' + new_article['description'] + ' ' + new_article['content']

    embedding_article = model.encode(content_enriched, convert_to_tensor=True)
    embedding_new_article = model.encode(new_content_enriched, convert_to_tensor=True)
    sim = util.pytorch_cos_sim(embedding_new_article, embedding_article)[0][0].item()

    ############# SECTION TO BE COMPLETED BY CONSULTANT ################

    return sim