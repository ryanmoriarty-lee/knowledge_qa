import jieba
from functools import lru_cache
from whoosh.qparser import QueryParser


def content_search(index, query_string):
    with index.searcher() as searcher:
        query_parser = QueryParser("content", index.schema)
        query = query_parser.parse(query_string)
        results = searcher.search(query)
        results_set = set()
        for result in results:
            results_set.add((result.fields()["content"], result.score))
        return list(results_set)

def extra_info_search(index, query_string):
    with index.searcher() as searcher:
        query_parser = QueryParser("extra_info", index.schema)
        query = query_parser.parse(query_string)
        results = searcher.search(query)
        results_set = set()
        for result in results:
            results_set.add((result.fields()["content"], result.score))
        return list(results_set)
    


@lru_cache(maxsize=128)
def inverted_index_search(index, query_string, k=-1):
    keywords = jieba.lcut_for_search(query_string)
    results = []
    for keyword in keywords:
        if len(keyword) >= 2:
            results += content_search(index, keyword) + extra_info_search(index, keyword)
    results = list(set(results))
    results = sorted(results, key=lambda x: x[1], reverse=True)
    if k != -1:
        results = results[:k]
    return results