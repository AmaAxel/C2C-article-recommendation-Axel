
from sentence_transformers import SentenceTransformer, util


def compute_similarity(model, article_A, article_B):

    """"

    Information about the model : https://huggingface.co/tasks/sentence-similarity
    
    Both article_A and article_B are dictionaries with keys 'title', 'publishedAt', 'section', 'URL', 'description' and 'content'
    The model should use the concatenation of title, description and content of both articles to compute the similarity
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