#!/usr/bin/env python
# coding: utf-8

# In[96]:


import json
import time
from datetime import date
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

today = date.today()
es = Elasticsearch("[localhost]:9301")

index = "duo2"
#body =  '{"query":{"match" :{"id":"50001"}}}'
body = '{ "query" : { "multi_match" : {"query" :"tip_level", "fields": ["title.n","contents.n"]} }  }'

print(today)
#print(body)
res = es.search(index=index, body=body)

print("start")

query = input("Enter Query : ")
print("query:",query)
    
# vector 값 읽기

with open('C:\\100.삼성전자DUO프로젝트\\300. 개발_검색\\Vector_Data_0105\\example_json\\es_vector_value1.txt','r',encoding='utf-8') as f:
    json_data = json.load(f)
    query_vector = json_data['title_vector']

    #print(title_vector)

#print("query_vector:\n",query_vector)
print("query_vector:\n")

embedding_start = time.time()
#
#    vectors = session.run(embeddings, feed_dict={text_ph: text})
#    return [vector.tolist() for vector in vectors]
#    query_vector = session.run([query], feed_dict={text_ph: text})[0].tolist() 

embedeing_time = time.time() - embedding_start

script_query = {
    "script_score":{
        "query" : { "match_all" : {}}#,
        # "script" : {
        #     "source":"cosineSimilarity(params.query_vector, doc['title_vector']) "
        #     ,"params":{"query_vector":query_vector}         
        # }
    }
}

# script_query = {
#     "script_score":{
#         "query" : { "match_all" : {}},
#         "script" : {
#             "source":"cosineSimilarity(params.query_vector, doc['title_vector']) "
#             ,"params":{"query_vector":query_vector}         
#         }
#     }
# }

script_query = body
print("script_query:\n",script_query)

search_start = time.time()

#query_body =script_query

response = es.search (
    index = "duo2",
    size= 5,
    body=body
#    body = { "query" : script_query }
#    {       
#                "query" = script_query
#       ,        "_source": {"includes":["title","body"]}   
#     }
)

search_time = time.time() - search_start

print("body:\n",body)
print("{} total hits.".format(response["hits"]["total"]["value"]))
#print("embedding time : {:.2f} ms".format(embedding_time * 1000))
#print("search time: {.2f} ms".format(search_time * 1000))
for hit in response["hits"]["hits"]:
    print("id:{}, score: {}".format(hit["_id"], hit["_score"]))
    print(hit["_source"])
    print()


# In[46]:


with open('C:\\Users\\minsoo20.kim\\workspace\\Data\\vector_data1.json','r',encoding='utf-8') as f:
    json_data = json.load(f)
    title = json_data['title']
    title_vector = json_data['title_vector']
    doc_id=json_data['doc_id']
    #print(json.dumps(title))
    print(title)
    #print(title_vector)
    
    doc = {
        "src" : "BERT",
        "id" : doc_id,
        "title": title,
        "title_vector":title_vector,
        "contents" : "벡터등록일:"+str(today)
        
    }
    #print (doc)
    
    res = es.index(index=index, id=5100001, body=doc)
    
    


# In[86]:


def run_query():
    while True :
        try:
                handle_query()
        except KeyboardInterrupt:
            return
        
def handle_query():
    query = input("Enter Query : ")
    
    embedding_start = time.time()
    query_vector = embeded_text([query])[0]
    embedeing_time = tme.time() - embedding_start
    
    script_query = {
        "script_score":{
            "query" : { "match_all" : {}},
            "script" : {
                "source":"cosineSimilarity(params.query_vector, doc['title_vector']) + 1.0",
                "params":{"query_vector":query_vector}         
            }
        }
    }
    
    search_start = time.time()
    response = es.search (
        index = "duo2",
        body = {
            "size" = 5,
            "query" = script_query,
            "_source": {"includes":["title","body"]}
        }
    )
        
    print()
    print("{} total hits.".format(response["hits"]["total"]["value"]))
    print("embedding time : {:.2f} ms".format(embedding_time * 1000))
    print("search time: {.2f} ms".format(search_time * 1000))
    for hit in response["hits"]["hits"]:
        print("id:{}, score: {}".format(hit["_id"], hit["_score"]))
        print(hit["_source"])
        print()
        


# In[87]:





# In[ ]:


es = Elasticsearch(['localhost'],port=9301)
doc = { 'title' : 'tip_level'}
#res = es.index(index="duo2", id=1, body=doc)

res = es.get(index="duo2")

print(res['_source'])


# In[76]:


json_data = []
count = 0

with open('C:\\100.삼성전자DUO프로젝트\\300. 개발_검색\\Vector_Data_0105\\example_json\\es_sample_1000.json','r',encoding='UTF8') as data_file:
    json_data = json.load(data_file)
    
    for i, vectorlist in enumerate(json_data["vector_data"]):
        print( str(i+1) +" "+ vectorlist['title'])
        #vector_data = json_data['vector_data']
        #print("vector_data count : ", len(vectorlist))
    
        title = vectorlist['title']
        title_vector = vectorlist['title_vector']
        doc_id = vectorlist['doc_id']
    
        doc = {
            "src" : "BERT",
            "id" : doc_id,
            "title": "[" + str(i+1) + "] " +title ,
            "title_vector":title_vector,
            "contents" : "벡터등록일:"+str(today),
            "txtfl_txt-hashtag_usrTag" : ["BERT","VECTOR","SVOC"]
        }
        #print (doc)
    
        res = es.index(index=index, id=(51000001+i), body=doc)
        #print ("index end")
        
        


# %%
