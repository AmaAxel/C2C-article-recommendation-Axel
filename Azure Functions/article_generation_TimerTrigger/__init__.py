import datetime
import requests
from bs4 import BeautifulSoup
import traceback

import json 
import logging 
import sys

import pandas as pd
#from newsapi import NewsApiClient
from azure.eventhub import EventHubProducerClient, EventData
import datetime 
import re
from newsapi.newsapi_client import NewsApiClient
import azure.functions as func
import os


from .clean_article import clean_content
from .extract_content import extract_to_dict


def main(timer: func.TimerRequest, outputMessage: func.Out[str]):
            
    ############# SECTION TO BE COMPLETED BY CONSULTANT ################
    event_hub_connection_string = os.environ.get("eventhub_connection_string_sender")
    eventhub_name = os.environ.get("eventhub_article_generation")
    newsapi_key = os.environ.get("newsapi_key")
    ############# SECTION TO BE COMPLETED BY CONSULTANT ################
    
    newsapi = NewsApiClient(api_key=newsapi_key) 

    # Search for articles using the everything endpoint
    articles = newsapi.get_everything(sources='bbc-news')

    # Retrieve the full content of each article using the urlToImage field
    for article in articles['articles']:

        article = extract_to_dict(article)

        if article:
            article['content'] = clean_content(article['content'])

            logging.info('**INFO - Article generated %s :', article)

            if len(article['content']) > 500:
                producer = EventHubProducerClient.from_connection_string(event_hub_connection_string, eventhub_name=eventhub_name)

                ############# SECTION TO BE COMPLETED BY CONSULTANT ################
                with producer:
                    event_data_batch = producer.create_batch()
                    event_data_batch.add(EventData(json.dumps(article).encode("utf-8")))
                    producer.send_batch(event_data_batch)
                    logging.info('**INFO - article sent to %s :', eventhub_name)
                ####################################################################

        
if __name__ == "__main__":
    main()