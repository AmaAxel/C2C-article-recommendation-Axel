import logging
import asyncio
import requests


async def get_best_labels(properties):
    labels = ['sport', 'tech', 'politics', 'entertainment', 'business']
    best_labels = []
    for label in labels:
        if properties.get(label) and properties[label] <= 2:
            best_labels.append(label)
    return best_labels


async def get_labels(text):

    headers = {
        'Authorization': 'Bearer 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',
        'Content-Type': 'application/json'
    }

    data = '{"inputs": "%s"}' % text[:512].replace('"', '\\"').replace("'", "\\'").encode('utf-8', 'replace')
    url = 'https://api-inference.huggingface.co/models/abhishek/autonlp-bbc-news-classification-37229289'

    response = requests.post(url, headers=headers, data=data)

    logging.info('**RESPONSE: %s', response.text)

    t = 0
    while True and t < 10:

        response = requests.post(url, headers=headers, data=data)
        
        if response.ok:
            # Extract the list of labels and scores from the predictions
            label_scores = response.json()[0]
            
            # Sort the labels based on the scores
            sorted_labels = sorted(label_scores, key=lambda x: x['score'], reverse=True)
            
            # Create a dictionary with the ranking of each label
            rankings = {}
            for i, label in enumerate(sorted_labels):
                rankings[label['label']] = i + 1

            return rankings
        
        elif "currently loading" in response.text:
            estimated_time = response.json()["estimated_time"]
            logging.info("Model is currently loading, waiting for %.2f seconds before retrying", 8)
            await asyncio.sleep(8)            
            t = t + 1
        else:
            raise ValueError(f"Failed to get response from Hugging Face API: {response.text}")

    logging.info('**Error in model-tagging API call: %s', response.text)
    raise ValueError('Could not get answer model-tagging API: %s', response.text)
