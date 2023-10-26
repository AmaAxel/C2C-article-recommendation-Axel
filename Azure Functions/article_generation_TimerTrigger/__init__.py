import datetime
import requests
from bs4 import BeautifulSoup
import traceback

import json 
import logging 
import sys

import pandas as pd
from azure.eventhub import EventHubProducerClient, EventData
import datetime 
import re
import azure.functions as func
import os
# from .lemonde_scraper import LeMondeArticleScraper
from .bbc_scraper import BBCArticleScraper


def main(timer: func.TimerRequest, outputMessage: func.Out[str]):
            
    ############# SECTION TO BE COMPLETED BY CONSULTANT ################
    event_hub_connection_string = os.environ.get("eventhub_connection_string_sender")
    eventhub_name = os.environ.get("eventhub_article_generation")
    ############# SECTION TO BE COMPLETED BY CONSULTANT ################
    
    # use the bbc_scrapper to extract the BBC articles currently on the website
    scraper = BBCArticleScraper()
    articles = scraper.scrape_articles()

    # iterate through the articles and send the content to Azure Event Hub
    for article in articles:

        producer = EventHubProducerClient.from_connection_string(event_hub_connection_string, eventhub_name=eventhub_name)

        ############ SECTION TO BE COMPLETED BY CONSULTANT ################
        with producer:
            event_data_batch = producer.create_batch()
            event_data_batch.add(EventData(json.dumps(article).encode("utf-8")))
            producer.send_batch(event_data_batch)
            url = article['URL']
            logging.info(f'**INFO - article {url} sent to : {eventhub_name}')
        ####################################################################
        
if __name__ == "__main__":
    main()