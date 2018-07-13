from eventregistry import *
from .ArticleProto_pb2 import ArticleDetail, ArticleList

er = EventRegistry(apiKey='9a66d7d3-b8e3-4fc0-ab52-ed70d71fb121')

source_uri_dict = {
    "National Geographic": "news.nationalgeographic.com",
    "Nature": "nature.com",
    "The Economist": "economist.com",
    "TIME": "time.com",
    "The New York Times": "nytimes.com",
    "Bloomberg Business": "bloomberg.com",
    "CNN": "edition.cnn.com",
    "Fox News": "foxnews.com",
    "Forbes": "forbes.com",
    "Washington Post": "washingtonpost.com",
    "The Guardian": "theguardian.com",
    "The Times": "thetimes.co.uk",
    "Mail Online": "dailymail.co.uk",
    "BBC": "bbc.com",
    "PEOPLE": "people.com",
}


def get_source_uri(source_title):
    if source_title in source_uri_dict:
        return source_uri_dict[source_title]
    else:
        return None


def get_article_list(page, count, source_title, keywords):
    q = QueryArticlesIter(
        lang="eng",
        sourceUri=get_source_uri(source_title),
        dateEnd=datetime.datetime.now(),
        keywords=keywords,
        keywordsLoc="title"
    )
    q.setRequestedResult(RequestArticlesInfo
                         (page=page, count=count,
                          returnInfo=ReturnInfo(
                              articleInfo=ArticleInfoFlags
                              (body=False, categories=False, image=True, videos=False))))
    res = er.execQuery(q)
    l = ArticleList()
    article_detail_list = []
    for article in res['articles']['results']:
        a = ArticleDetail()
        a.uri = article['uri']
        a.title = article['title']
        a.source = article['source']['title']
        a.imageUrl = article['image'] if article['image'] else ''
        a.time = article['dateTime']
        article_detail_list.append(a)
    l.articles.extend(article_detail_list)
    return l


def get_article_detail(article_uri):
    q = QueryArticle(
        article_uri
    )
    q.setRequestedResult(RequestArticleInfo
                         (returnInfo=ReturnInfo(
                             articleInfo=ArticleInfoFlags
                             (body=True, categories=True, image=True, videos=False))))
    res = er.execQuery(q)
    a_proto = ArticleDetail()
    a_json = res[article_uri]["info"]
    a_proto.title = a_json["title"]
    a_proto.body = a_json["body"]
    a_proto.imageUrl = a_json["image"] if a_json["image"] else ""
    cate_str = ""
    for category in a_json["categories"]:
        cate_str += category["label"].split("/")[-1] + "; "
    a_proto.category = cate_str[:-2]
    return a_proto
