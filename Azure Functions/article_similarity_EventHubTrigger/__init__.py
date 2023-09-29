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

from src.label_article import *

############# SECTION TO BE COMPLETED BY CONSULTANT ################
cosmosDB_endpoint =  os.environ.get("cosmosDB_endpoint")
cosmos_database_name =  os.environ.get("cosmos_database_name")
graph_name = os.environ.get("graph_name")
cosmosDB_key = os.environ.get("cosmosDB_key")

eventhub_connection_string = os.environ.get("eventhub_connection_string_listener")
eventhub_name = os.environ.get("eventhub_article_generation")
sim_threshold = float(os.environ.get("similarity_threshold"))
############# SECTION TO BE COMPLETED BY CONSULTANT ################
consumer_group = "$Default"

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


async def insert_article(new_article):

    # Create a Gremlin client and connect to the Cosmos DB graph
    gremlin_client = client.Client(cosmosDB_endpoint, 'g',
                                        username=f"/dbs/%s/colls/%s" % (cosmos_database_name, graph_name),
                                        message_serializer=serializer.GraphSONSerializersV2d0(),
                                        password=cosmosDB_key)


    # Check if article is already in DB
    # Define the Gremlin query to check if there is an existing article with similar title and property
    check_query_already_exist = """
        g.V().has('article', 'title', title)
                                """

    # Execute the Gremlin query with the given article properties to check if an article already exists
    result_set = gremlin_client.submit(check_query_already_exist, {
            'title': new_article['title'],
            })
    
    # If there are no existing articles, add the new article vertex
    if not result_set.all().result():

        # Define the Gremlin query to insert the article vertex

        # Create a dictionary of properties for the new article
        properties = {
                    'title': new_article['title'],
                    'description': new_article['description'],
                    'content': new_article['content'],
                    'publishedAt': new_article['publishedAt'],
                    'partitionKey': new_article['publishedAt']
        }

        # Add properties for each labels and its corresponding score
        label_scores = await get_labels(new_article['title'])
        for label, score in label_scores.items():
            properties[label] = score

        # get the best labels of the new article
        best_labels = await get_best_labels(properties)

        # Construct the query to select articles with the specified properties and label
        query = "g.V().hasLabel('article')"
        for label in best_labels:
            query += ".has('{}', lte(2))".format(label)
        query += ".limit(200).values('title').fold()"

        # Get the same-category articles
        all_titles = gremlin_client.submit(query)
        all_titles = all_titles.all().result()
        all_titles = list(all_titles[0])
            
        # Construct the Gremlin query with the properties
        add_query = """
                    g.addV('article')
                        .property('title', title)
                        .property('description', description)
                        .property('content', content)
                        .property('publishedAt', publishedAt)
                        .property('partitionKey', partitionKey)
                    """

        # Add properties for each label and its corresponding score to the query
        for label, score in label_scores.items():
            add_query += f"\n.property('{label}', {score})"

        # Execute the Gremlin query with the given article properties
        gremlin_client.submitAsync(add_query, properties)
        logging.info('**INFO: Article successfully inserted')

        # Delete latest article (replacing the oldest article with the newest)
        # query = "g.V().hasLabel('article').order().by('publishedAt').limit(1).sideEffect(drop())"
        # result_set = gremlin_client.submit(query)

        # Loop over all titles in the list and compute similarity
        for title in all_titles:

            ############# SECTION TO BE COMPLETED BY CONSULTANT ################

            # Query the content property of the article with the matching title
            query = "g.V().hasLabel('article').has('title', title).project('title', 'description', 'content').by('title').by('content').by('description').fold()"
            result = gremlin_client.submit(query, {'title': title}).all().result()
            # Extract the nested dictionary
            nested_dict = result[0][0]

            # Concatenate 'title', 'description', and 'content'
            content_enriched = nested_dict['title'] + ' ' + nested_dict['description'] + ' ' + nested_dict['content']
            new_content_enriched = new_article['title'] + ' ' + new_article['description'] + ' ' + new_article['content']

            embedding_article = model.encode(content_enriched, convert_to_tensor=True)
            embedding_new_article = model.encode(new_content_enriched, convert_to_tensor=True)
            sim = util.pytorch_cos_sim(embedding_new_article, embedding_article)[0][0].item()

            # prepare relationship query to used in between similar articles
            relationship_query = """
                        g.V().has('article', 'title', title1).as('a')
                            .V().has('article', 'title', title2).as('b')
                            .coalesce(
                                select('a').outE('similarity').where(inV().as('b')),
                                addE('similarity').from('a').to('b').property('value', sim)
                            )
                                        """
            # If the similarity score is above the threshold, create a relationship between the articles
            if sim >= sim_threshold:
                # Create a relationship between the new article and the current article
                result_set = gremlin_client.submitAsync(relationship_query, {
                                'title1': new_article['title'],
                                'title2': title,
                                'sim': sim
                        })

                logging.info('**INFO: Similarity found %s', round(sim, 2))

            ############# SECTION TO BE COMPLETED BY CONSULTANT ################

    else:
        logging.info('**INFO: Article is already in Database')

    # Close the Gremlin client connection
    gremlin_client.close()


nest_asyncio.apply()
async def main(events: func.EventHubEvent):

    try:
        for event in events:

            ############# SECTION TO BE COMPLETED BY CONSULTANT ################
            message_body = event.get_body().decode('utf-8')
            new_article = json.loads(message_body)
            logging.info("New Article:")
            logging.info(new_article)
            ############# SECTION TO BE COMPLETED BY CONSULTANT ################

            await insert_article(new_article)
    
    except Exception as e:
        logging.error(f"Error processing event: {str(e)}")


