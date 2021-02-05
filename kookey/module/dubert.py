
import json
from collections import OrderedDict
import time
from datetime import date
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


class DubertSearch():
    def __init__(self):
        self.title_vector = list()
        self.today = date.today()
        self.indexName = "duo3"
        self.response = {}
        self.es = Elasticsearch([{'host':'localhost','port':9301}])
        
    #초기화
    def search_vector(self, queryString):

        print("DUO BERT 검색[{}] : {}".format(self.indexName, self.today))

        #"g-tne 문의"
        #queryString = input("검색할 VOC제목을 입력하세요 : ")
        print("검색할 문장 :", queryString)

        search_script = '{"size":1, "query" : { "multi_match" : {"query" :"'+queryString+'", "fields": ["id","title.n","title.s","contents.n","contents.s"]} }  }'
            
        search_body = search_script 
        print("search script:\n",search_body)

        search_start = time.time()

        response = self.es.search (
            index = self.indexName,
            body= search_body
        )

        search_time = time.time() - search_start
        

        #print("body:\n",body)
        #print("타이틀 검색결과")
        #hit_count = response["hits"]["total"]["value"]
        print("{} total hits.".format(response["hits"]["total"]["value"]))
        print("search time: {:.2f} ms".format(search_time * 1000))
        for hit in response["hits"]["hits"]:
            # print("1. id:{}, score: {}".format(hit["_id"], hit["_score"]))
            # print("2. title :", hit["_source"]["title"])
            self.title_vector = hit["_source"]["title_vector"]

        #벡터값으로 조회하기
        print("*************** 벡터값 조회 종료 ********************\n")

        return self.title_vector


    # elasticSearch Query    
    def search_list(self, inQuiry_vector, size):
        #inQuiry_vector = list(title_vector)
        #print("inQuiry_vector:",inQuiry_vector)

        search_script = {
            "size" : size,
            "query": {
                "script_score": {
                    "query" : { 
                        "bool" : {
                            "filter" : {
                                "term" : {
                                "src" : "BERT" 
                                }
                            }
                        }
                    },
                    "script": {
                        "source": "cosineSimilarity(params.inQuiry_vector, 'title_vector') + 1.0",
                        "params": { 
                            "inQuiry_vector": inQuiry_vector
                            }
                        }
                    }
            } 
        }     

        print("vector script:\n", search_script)
        print("--------------------------------")
        search_start = time.time()

        response = self.es.search ( 
            index = self.indexName,
            body = search_script
        )

        search_time = time.time() - search_start
        print("Title Vector 유사도 검색결과")
        print("{} total hits.".format(response["hits"]["total"]["value"]))
        #print("embedding time : {:.2f} ms".format(embedding_time * 1000))
        print("search time: {:.2f} ms".format(search_time * 1000))
        print("--------------------------------", end="\n")

        search_result = []
        es_data = OrderedDict()
        #print("[Rank:{:2d}] id:{}, score: {:10f} ==> 유사제목 : {}".format(i+1, hit["_id"], hit["_score"], hit["_source"]["title"]) )
        #print("[Rank:{:2d}] score:{:10f} ==> {}".format(i+1,  hit["_score"], hit["_source"]["title"]) ) #hit["_source"]["title_vector"]

        for i, hit in enumerate(response["hits"]["hits"]):
            print("[Rank:{:2d}] id:{}, score: {:10f} ==> 유사제목 : {}".format(i+1, hit["_id"], hit["_score"], hit["_source"]["title"]) )
            # search_result.append(i+1, hit["_score"], hit["_source"]["title"])
            # es_data["rank"] = i+1
            # es_data["score"] = hit["_score"]
            # es_data["title"] = hit["_source"]["title"]
            # es_data["id"] = hit["_id"]

            search_result.append(
                {
                    'rank':i+1, 'score':hit["_score"], 'title':hit["_source"]["title"], 'id': hit["_id"]
                }
            )
                        
        print("--------------------------------")

        return search_result
