
from sentence_transformers import SentenceTransformer, util


def compute_similarity(model, article_A, article_B):

    """"

    Information about the model : https://huggingface.co/tasks/sentence-similarity
    
    Old and new articles are dictionaries with keys title, description, publishedAt and content
    old_article is an article already in the graph database
    new_article is the incoming article that we want to compare to the old article already in the database
    Returns a float (value of similarity between the two articles)
    """

    ############# SECTION TO BE COMPLETED BY CONSULTANT ################

    content_enriched = article_A['title'] + ' ' + article_A['description'] + ' ' + article_A['content']
    new_content_enriched = article_B['title'] + ' ' + article_B['description'] + ' ' + article_B['content']

    embedding_article = model.encode(content_enriched, convert_to_tensor=True)
    embedding_new_article = model.encode(new_content_enriched, convert_to_tensor=True)
    sim = util.pytorch_cos_sim(embedding_new_article, embedding_article)[0][0].item()

    ############# SECTION TO BE COMPLETED BY CONSULTANT ################

    return sim