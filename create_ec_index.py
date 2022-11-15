import json
import re
from elasticsearch import Elasticsearch

es = Elasticsearch()
INDEX_NAME = 'ec_index'

INDEX_SETTINGS = {  
    "settings" : {
        "index" : {
            "number_of_shards" : 1,
            "number_of_replicas" : 1
        }
    }
}

if es.indices.exists(INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)

es.indices.create(index=INDEX_NAME, body=INDEX_SETTINGS)

with open("data/entity_type.json", "r") as f:
    entity_type = json.load(f)

with open('data\short_abstracts_en.ttl', encoding='utf-8') as f:
    next(f)
    for i, line in enumerate(f):
        comment = re.findall(r'"([^"]*)"', line[2:])[0]
        line = line.split(' ')
        name = line[0].split("/")[-1].replace('>', '').strip()
        types = entity_type.get(name)
        if types != None:
            types = ' '.join(types)
        else: 
            types = ''
        name = name.replace('_', ' ')
        print(i, name)
        elem = {'name': name, 'type': types, 'comment': comment}
        es.index(index=INDEX_NAME, id=name, body=elem)        