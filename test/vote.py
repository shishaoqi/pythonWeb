# -*- coding: utf-8 -*-
# @Author: shishao
# @Date:   2017-03-22 00:50:06
# @Last Modified by:   shishao
# @Last Modified time: 2017-03-22 01:10:07
# <start id="upvote-code"/>
import time
import unittest

ONE_WEEK_IN_SECONDS = 7 * 86400                     #A
VOTE_SCORE = 432                                    #A

def article_vote(conn, user, article):
    cutoff = time.time() - ONE_WEEK_IN_SECONDS      #B
    if conn.zscore('time:', article) < cutoff:      #C
        return

    article_id = article.partition(':')[-1]         #D
    if conn.sadd('voted:' + article_id, user):      #E
        conn.zincrby('score:', article, VOTE_SCORE) #E
        conn.hincrby(article, 'votes', 1)           #E
# <end id="upvote-code"/>
#A Prepare our constants
#B Calculate the cutoff time for voting
#C Check to see if the article can still be voted on (we could use the article HASH here, but scores are returned as floats so we don't have to cast it)
#D Get the id portion from the article:id identifier
#E If the user hasn't voted for this article before, increment the article score and vote count (note that our HINCRBY and ZINCRBY calls should be in a Redis transaction, but we don't introduce them until chapter 3 and 4, so ignore that for now)
#END

# <start id="post-article-code"/>
def post_article(conn, user, title, link):
    article_id = str(conn.incr('article:'))     #A

    voted = 'voted:' + article_id
    conn.sadd(voted, user)                      #B
    conn.expire(voted, ONE_WEEK_IN_SECONDS)     #B

    now = time.time()
    article = 'article:' + article_id
    conn.hmset(article, {                       #C
        'title': title,                         #C
        'link': link,                           #C
        'poster': user,                         #C
        'time': now,                            #C
        'votes': 1,                             #C
    })                                          #C

    conn.zadd('score:', article, now + VOTE_SCORE)  #D
    conn.zadd('time:', article, now)                #D

    return article_id
# <end id="post-article-code"/>
#A Generate a new article id
#B Start with the posting user having voted for the article, and set the article voting information to automatically expire in a week (we discuss expiration in chapter 3)
#C Create the article hash
#D Add the article to the time and score ordered zsets
#END

# <start id="fetch-articles-code"/>
ARTICLES_PER_PAGE = 25

def get_articles(conn, page, order='score:'):
    start = (page-1) * ARTICLES_PER_PAGE            #A
    end = start + ARTICLES_PER_PAGE - 1             #A

    ids = conn.zrevrange(order, start, end)         #B
    articles = []
    for id in ids:                                  #C
        article_data = conn.hgetall(id)             #C
        article_data['id'] = id                     #C
        articles.append(article_data)               #C

    return articles
# <end id="fetch-articles-code"/>
#A Set up the start and end indexes for fetching the articles
#B Fetch the article ids
#C Get the article information from the list of article ids
#END

# <start id="add-remove-groups"/>
def add_remove_groups(conn, article_id, to_add=[], to_remove=[]):
    article = 'article:' + article_id           #A
    for group in to_add:
        conn.sadd('group:' + group, article)    #B
    for group in to_remove:
        conn.srem('group:' + group, article)    #C
# <end id="add-remove-groups"/>
#A Construct the article information like we did in post_article
#B Add the article to groups that it should be a part of
#C Remove the article from groups that it should be removed from
#END

# <start id="fetch-articles-group"/>
def get_group_articles(conn, group, page, order='score:'):
    key = order + group                                     #A
    if not conn.exists(key):                                #B
        conn.zinterstore(key,                               #C
            ['group:' + group, order],                      #C
            aggregate='max',                                #C
        )
        conn.expire(key, 60)                                #D
    return get_articles(conn, page, key)                    #E
# <end id="fetch-articles-group"/>
#A Create a key for each group and each sort order
#B If we haven't sorted these articles recently, we should sort them
#C Actually sort the articles in the group based on score or recency
#D Tell Redis to automatically expire the ZSET in 60 seconds
#E Call our earlier get_articles() function to handle pagination and article data fetching
#END

#--------------- Below this line are helpers to test the code ----------------

class TestCh01():
    def setUp(self):
        import redis
        self.conn = redis.Redis(db=15)

    def tearDown(self):
        del self.conn
        print
        print

    def test_article_functionality(self):
        conn = self.conn
        import pprint

        article_id = str(post_article(conn, 'username', 'A title', 'http://www.google.com'))
        print "We posted a new article with id:", article_id
        print
        self.assertTrue(article_id)

        print "Its HASH looks like:"
        r = conn.hgetall('article:' + article_id)
        print r
        print
        self.assertTrue(r)

        article_vote(conn, 'other_user', 'article:' + article_id)
        print "We voted for the article, it now has votes:",
        v = int(conn.hget('article:' + article_id, 'votes'))
        print v
        print
        self.assertTrue(v > 1)

        print "The currently highest-scoring articles are:"
        articles = get_articles(conn, 1)
        pprint.pprint(articles)
        print

        self.assertTrue(len(articles) >= 1)

        add_remove_groups(conn, article_id, ['new-group'])
        print "We added the article to a new group, other articles include:"
        articles = get_group_articles(conn, 'new-group', 1)
        pprint.pprint(articles)
        print
        self.assertTrue(len(articles) >= 1)

        to_del = (
            conn.keys('time:*') + conn.keys('voted:*') + conn.keys('score:*') + 
            conn.keys('article:*') + conn.keys('group:*')
        )
        if to_del:
            conn.delete(*to_del)

if __name__ == '__main__':
    Obj = TestCh01()
    Obj.setUp()
    Obj.test_article_functionality()
    Obj.tearDown()