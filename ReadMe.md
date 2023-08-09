# World City Graph

The whole project is composed of three parts: information collection, graph construction, and latent information inference

## Part 1 Collect city information from Wikipedia

Firstly, we collect a country-city list from Wikipedia and then further obtain information about each city

Secondly, we parse the raw web content to get text content that describes different aspects of cities 

file contents:

getcitylist.py  get the city list of each country from Wikipedia <br/>

due to the different forms of the city list of each country, we collect the city list information with *different parameters combination(even different function design)*, you can refer to city_record.py for further information

get_content.py get the web content of each city



## Part 2 Graph construct

Firstly, we use a pre-trained Bert model to get the embedding of each city

Secondly, we further analyze the "friend city" section on the web page of each city and link friendly cities

Finally, we build a city graph composed of city nodes and friendly relations.

file contents:

content_analyze.py basically parse the web content of each city to get mixed information of a city(txt file with contents from all the sections)
super_ana.py       further analyze the mixed information, and split it into several files according to the number of sections
fieldmatch.py      many cities contained sections with different names but have similar contents(both in-city and inter-city), this step aims at 
                   recognizing the similarity and classifying these sections
cons_dataset.py    get the embedding of each city (concatenate the embedding of different section classes) and parse the relationship between cities 
                  mentioned in "friendly cities"


## Part 3 Mine latent city relationship

we train a GNN model based on the graph built in Part 2 And use it to infer the latent friend-city relationship



