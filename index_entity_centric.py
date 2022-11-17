from rdflib import Graph
import re
import json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk

with open('data\ontology_1.json') as f:
    ontology = json.load(f)

g = Graph()
instance_types = dict()
short_abstracts = dict()

g.parse('./data/instance_types.ttl', format='n3')
for subj, pred, obj in g:
    if str(pred) == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
        uri = str(subj)
        type = str(obj)
        if type == 'http://www.w3.org/2002/07/owl#Thing':
            types = ['owl:Thing']
        elif type.startswith('http://dbpedia.org/ontology/'):
            type = type.split(' ')
            type = type[0].split("/")[-1].strip()
            type = 'dbo:' + type
            types = [type] + ontology[type]['parent']
        instance_types[uri] = types

g = Graph()
g.parse('./data/short_abstracts.ttl', format='n3')
for subj, pred, obj in g:
    if str(pred) == 'http://www.w3.org/2000/01/rdf-schema#comment':
        uri = str(subj)
        if uri in instance_types.keys():
            types = instance_types[uri]
            types = ' '.join([type for type in types])
            name = uri.split(' ')
            name = name[0].split("/")[-1].strip()
            name = re.sub(r'__\d+', '', name)
            name = name.replace('_', ' ')
            elem = {'name': name, 'types': types, 'comment': str(obj)}
            short_abstracts[uri] = elem
            
es = Elasticsearch()
INDEX_NAME = 'ec_index2'

INDEX_SETTINGS = {    
    'settings' : {
        'index' : {
            "number_of_shards" : 1,
            "number_of_replicas" : 1
        },
        'analysis': {
            'analyzer': {
                'my_english_analyzer': {
                    'type': "custom",
                    'tokenizer': "standard",
                    'stopwords': "_english_",
                    'filter': [
                        "lowercase",
                        "english_stop",
                        "filter_english_minimal"
                    ]                
                }
            },
            'filter' : {
                'filter_english_minimal' : {
                    'type': "stemmer",
                    'name': "minimal_english"
                },
                'english_stop': {
                    'type': "stop",
                    'stopwords': "_english_"
                }
            },
        }
    },
    'mappings': {
        'properties': {
            'name': {
                'type': "text",
                'term_vector': "with_positions",
                'analyzer': "my_english_analyzer"
            },
            'types': {
                'type': "text",
                'term_vector': "with_positions",
                'analyzer': "my_english_analyzer"
            },
            'comment': {
                'type': "text",
                'term_vector': "with_positions",
                'analyzer': "my_english_analyzer"
            },

        }
    }
}


if es.indices.exists(index=INDEX_NAME):
    es.indices.delete(index=INDEX_NAME)

es.indices.create(index=INDEX_NAME, body=INDEX_SETTINGS)


def insert_data(index_name, data):
    for key, val in data.items():
        yield {
                '_index': index_name,
                '_type': '_doc',
                '_id': key,
                '_source': val,
            }

for success, info in parallel_bulk(es, insert_data(INDEX_NAME, short_abstracts), 
                                        chunk_size=1000, thread_count=16, queue_size=16):  
    if not success:
        print('A document failed:', info)
            
res = es.search(index=INDEX_NAME, q = 'Name famous russian director', size = 5)['hits']['hits']

print(res[0]['_source']['types'].split(' '))