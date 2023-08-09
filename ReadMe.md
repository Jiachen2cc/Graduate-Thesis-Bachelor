# World City Graph

The whole project is composed of three parts: information collection, graph construction, and latent information inference

## Part 1 Collect city information from Wikipedia

Firstly, we collect a country-city list from Wikipedia and then further obtain information about each city

Secondly, we parse the raw web content to get text content that describes different aspects of cities 

## Part 2 Graph construct

Firstly, we use a pre-trained Bert model to get the embedding of each city

Secondly, we further analyze the "friend city" section on the web page of each city and link friendly cities

Finally, we build a city graph composed of city nodes and friendly relations.


## Part 3 Mine latent city relationship

we train a GNN model based on the graph built in Part 2 And use it to infer the latent friend-city relationship



