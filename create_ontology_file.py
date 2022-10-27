type_set = set()

with open('data\dbpedia_2016-10.nt', encoding='latin-1') as f:
    for line in f:
        line = line.split(' ')
        if len(line[0]) > len('<http://dbpedia.org/ontology/>'):
            type_set.add(line[0])


ontology = {key :{'resources': [], 'subClassOf': []} for key in type_set}

from xml.dom.minidom import Attr
from owlready2 import *

onto = get_ontology("file://data\dbpedia_2016-10.owl").load()

for t in type_set:
    index = t.rfind('/')
    t1 = t[index+1:]
    val = t1[:-1]

    with onto:
        cls_list = onto.search(iri = '*{}'.format(val))
        print(cls_list)
        if len(cls_list) != 0:
            cls = cls_list[0]
            try:
                supclasses = cls.ancestors()
            except AttributeError:
                continue
            for supclass in supclasses: 
                supclass = str(supclass)
                if supclass.startswith('data\dbpedia_2016-10'):
                    index = supclass.rfind('.')
                    supclass = supclass[index+1:]
                    if supclass != val:
                        ontology[t]['subClassOf'].append(supclass)

with open('data\instance_types_en.ttl', encoding='latin-1') as f:
    for line in f:
        line = line.split(' ')
        if line[2].startswith('<http://dbpedia.org/ontology'):
            if line[2] in ontology.keys():
                ontology[line[2]]['resources'].append(line[0])


import json
with open('ontology.json', 'w') as fp:
    json.dump(ontology, fp)





