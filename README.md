# C2C Article Recommendation

Version : 2.0


# **Hands-on : C2C recommendation**

This hands-on tackles content similarity in Azure. In this project, you will :

* Extract news articles from a website (scrapers currently available : BBC and Le Monde). Those articles will be sent to an Azure Event Hub using a first time-triggered Azure Function. 
* Using another event-hub-triggered Azure Function, you will read those incoming news articles to the Azure Event Hub and insert those articles in the graph CosmosDB database. When inserting a new article in the graph database, you will also compute the similarity of this article with the other articles already in the graph database and create properties based on the results. 
* Finally, you will implement simple CI/CD pipelines to industrailize this project using Azure DevOps.


## **Services used in this Hands-On:**
* Azure Functions
* Azure Event Hub
* Azure CosmosDB
* Azure DevOps

