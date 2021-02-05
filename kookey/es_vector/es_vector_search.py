
import json
import time
from datetime import date
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

today = date.today()
es = Elasticsearch("[localhost]:9301")

index = "duo2"
#body =  '{"query":{"match" :{"id":"50001"}}}'
search_body = '{ "size" : 1, "query" : { "multi_match" : {"query" :"tip_level", "fields": ["title.n","contents.n"]} }  }'

print(today)
#print(body)
res = es.search(index=index, body=search_body)

print("start")

query = input("Enter VOC제목 : ")
print("입력질문 :", query)
    
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
        "query" : { "match_all" : {}},
        "script" : {
            "source":"cosineSimilarity(params.query_vector, doc[\"title_vector\"])+1.0"
            ,"params":{"query_vector":query_vector}         
        }
    }
}

search_body = script_query 
print("script_query:\n",script_query)

search_start = time.time()

#query_body =script_query

response = es.search (
    index = "duo2",
    size= 5,
    body=search_body
#    body = { "query" : script_query }
#    {       
#                "query" = script_query
#       ,        "_source": {"includes":["title","body"]}   
#     }
)

search_time = time.time() - search_start

#print("body:\n",body)
print("{} total hits.".format(response["hits"]["total"]["value"]))
#print("embedding time : {:.2f} ms".format(embedding_time * 1000))
#print("search time: {.2f} ms".format(search_time * 1000))
for hit in response["hits"]["hits"]:
    print("id:{}, score: {}".format(hit["_id"], hit["_score"]))
    print(hit["_source"])
    print()
