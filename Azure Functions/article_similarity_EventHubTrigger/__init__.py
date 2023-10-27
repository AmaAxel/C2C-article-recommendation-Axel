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
cosmosDB_endpoint =  #############
cosmos_database_name =  #############
graph_name = #############
cosmosDB_key = #############

eventhub_connection_string = #############
eventhub_name = #############
similarity_threshold_str = #############
############# SECTION TO BE COMPLETED BY CONSULTANT ################

consumer_group = "$Default"

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')



async def insert_article(new_article):

    ############# SECTION TO BE COMPLETED BY CONSULTANT ################

    # Create a Gremlin client and connect to the Cosmos DB graph
    gremlin_client = #########################


    # Check if article is already in DB
    #############
        
    # If article not already in database, add the new article vertex
    #############

    # Fetch the last ~200 urls and compute similarity. If similarity > 0.4 > create relationship
    #############
    #############
    #############
    #############
    #############
    #############

    # Close the Gremlin client connection
    gremlin_client.close()

    ############# SECTION TO BE COMPLETED BY CONSULTANT ################



nest_asyncio.apply()
async def main(events: func.EventHubEvent):
    try:
        for event in events:

            # read the incoming article inside each event
            ############# SECTION TO BE COMPLETED BY CONSULTANT ################
            #############
            #############            
            logging.info("New Article:")
            logging.info(new_article)
            ############# SECTION TO BE COMPLETED BY CONSULTANT ################

            # once the article extracted as a dictionary, insert this article to the graph database
            await insert_article(new_article)
    
    except Exception as e:
        logging.error(f"Error processing event: {str(e)}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Error running main: {str(e)}")
