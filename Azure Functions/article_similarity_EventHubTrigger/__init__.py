import os
import logging
import sys
import asyncio
import nest_asyncio
import requests
import azure.functions as func
import json
from gremlin_python.driver import client, serializer
from gremlin_python.driver.protocol import GremlinServerError
from gremlin_python.process.traversal import T
from collections.abc import MutableMapping

from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from sentence_transformers import SentenceTransformer, util

#from .label_article import get_labels, get_best_labels
from .compute_similarity import compute_similarity


############# SECTION TO BE COMPLETED BY CONSULTANT ################
cosmosDB_endpoint =  os.environ.get("cosmosDB_endpoint")
cosmos_database_name =  os.environ.get("cosmos_database_name")
graph_name = os.environ.get("graph_name")
cosmosDB_key = os.environ.get("cosmosDB_key")

eventhub_connection_string = os.environ.get("eventhub_connection_string_listener")
eventhub_name = os.environ.get("eventhub_article_generation")
similarity_threshold_str = os.environ.get("similarity_threshold")
if similarity_threshold_str is not None:
    sim_threshold = float(similarity_threshold_str)
else:
    # Handle the case when the environment variable is not set or is None
    sim_threshold = 0.4  # Set a default value or handle it as needed

############# SECTION TO BE COMPLETED BY CONSULTANT ################
consumer_group = "$Default"

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')



async def insert_article(new_article):


    ############# SECTION TO BE COMPLETED BY CONSULTANT ################

    # Create a Gremlin client and connect to the Cosmos DB graph
    gremlin_client = client.Client(cosmosDB_endpoint, 'g',
                                        username=f"/dbs/%s/colls/%s" % (cosmos_database_name, graph_name),
                                        message_serializer=serializer.GraphSONSerializersV2d0(),
                                        password=cosmosDB_key)


    # Check if article is already in DB
    check_query_already_exist = """
        g.V().has('article', 'URL', URL)
    """
    result_set = gremlin_client.submit(check_query_already_exist, {
        'URL': new_article['URL']
    })
        
    # If there are no existing articles, add the new article vertex
    if not result_set.all().result():

        # Define the Gremlin query to insert the article vertex
        # Create a dictionary of properties for the new article
        properties = {
                    'title': new_article['title'],
                    'publishedAt': new_article['publishedAt'],
                    'section': new_article['section'],
                    'URL': new_article['URL'],
                    'description': new_article['description'],
                    'content': new_article['content']
        }

        logging.info('**INFO: PROPERTIES')
        logging.info(properties)
            
        # Construct the Gremlin query with the properties
        insert_query = """
                    g.addV('article')
                        .property('title', title)
                        .property('publishedAt', publishedAt)
                        .property('section', section)
                        .property('URL', URL)
                        .property('description', description)
                        .property('content', content)
                        .property('partitionKey', partitionKey)
                    """

        # Execute the Gremlin query with the given article properties
        gremlin_client.submitAsync(insert_query, properties)
        logging.info('**INFO: Article successfully inserted')

        # Delete latest article (replacing the oldest article with the newest)
        # query_delete_last_article = "g.V().hasLabel('article').order().by('publishedAt').limit(1).sideEffect(drop())"
        # result_set = gremlin_client.submit(query_delete_last_article)

        # Fetch the last 250 urls
        query_recent_urls = "g.V().hasLabel('article').order().by('publishedAt', decr).limit(250).values('URL').fold()"

        # Get the same-category articles
        recent_urls = gremlin_client.submit(query_recent_urls)
        recent_urls = recent_urls.all().result()
        recent_urls = list(recent_urls[0])

        # Loop over all recent urls in the list, fetch content and compute similarity
        for url in recent_urls:

            # Query the content property of the article with the matching url
            query_recent_article = "g.V().hasLabel('article').has('URL', URL).project('title', 'description', 'content').by('title').by('content').by('description').fold()"
            result = gremlin_client.submit(query_recent_article, {'URL': url}).all().result()
            # Extract the nested dictionary
            recent_article = result[0][0]

            # compute similarity
            sim = compute_similarity(model, recent_article, new_article)

            # If the similarity score is above the threshold, create a relationship between the articles
            if sim >= sim_threshold:

                # prepare relationship query to used in between similar articles
                query_create_relationship = """
                        g.V().has('article', 'URL', url1).as('a')
                            .V().has('article', 'URL', url2).as('b')
                            .coalesce(
                                select('a').outE('similarity').where(inV().as('b')),
                                addE('similarity').from('a').to('b').property('value', sim)
                            )
                                        """
            
                # Create a relationship between the new article and the current article
                result_set = gremlin_client.submitAsync(query_create_relationship, {
                                'url1': new_article['URL'],
                                'url2': url,
                                'sim': sim
                        })

                logging.info('**INFO: Similarity found %s', round(sim, 2))

    else:
        logging.info('**INFO: Article is already in Database')

    # Close the Gremlin client connection
    gremlin_client.close()

    ############# SECTION TO BE COMPLETED BY CONSULTANT ################



nest_asyncio.apply()
async def main(events: func.EventHubEvent):

    try:
        for event in events:

            # read the incoming article inside each event
            ############# SECTION TO BE COMPLETED BY CONSULTANT ################
            message_body = event.get_body().decode('utf-8')
            new_article = json.loads(message_body)
            logging.info("New Article:")
            logging.info(new_article)
            ############# SECTION TO BE COMPLETED BY CONSULTANT ################

            # once the article extracted as a dictionary, insert this article to the graph database
            await insert_article(new_article)
    
    except Exception as e:
        logging.error(f"Error processing event: {str(e)}")


