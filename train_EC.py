import json
from smart_dataset.evaluation.dbpedia.evaluate import load_type_hierarchy
from log_reg_categorizer import LogRegCategorizer
from elasticsearch import Elasticsearch
import string


type_hier = load_type_hierarchy('./smart_dataset/evaluation/dbpedia/dbpedia_types.tsv')
es = Elasticsearch()

INDEX_NAME = 'ec_index'


test_questions = json.load(open('./data/smarttask_dbpedia_test_questions.json'))
lrc = LogRegCategorizer('./data/smarttask_dbpedia_train.json')
baseline_output = list()

for question in test_questions:
    q_id = question['id']
    q_text = question['question']
    q_cat = lrc.predict([q_text])[0]
    if q_cat == 'boolean':
        q_type = ['boolean']
    elif q_cat == 'literal':
        q_type = lrc.predict_literal_type([q_text]).tolist()
    elif q_cat == 'resource':
        res = es.search(index=INDEX_NAME, q=q_text.translate(str.maketrans('', '', string.punctuation)), size=5)['hits']['hits']
        q_type = [hit['_source']['types'] for hit in res]
    else:
        q_type = None
    
    baseline_output.append({
        'id': q_id,
        'question': q_text,
        'category': q_cat,
        'type' : q_type
    })

with open('baseline_entity_cent_results_train.json', 'w') as outfile:
    json.dump(baseline_output, outfile)