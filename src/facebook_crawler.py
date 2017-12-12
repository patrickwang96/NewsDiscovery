#!/user/bin/env python
# coding: utf-8

__author__ = 'WANG Ruochen'
__copyright__ = 'Copyright 2017, NewsDiscovery'
__credits__ = ['WANG Ruoche']

__license__ = 'GPL 3.0'
__version__ = '0.1'
__maintainer__ = 'WANG Ruochen'
__email__ = 'ruochwang@gmail.com'

from . import setting

import urllib2
import json
import datetime
import pandas as pd
# import numpy as np
# import glob
import logging

logging.basicConfig(filename='log/web_crawler.log', level=logging.DEBUG)

# Define some variables
app_id, app_secret = setting.load_facebook_account()

access_token = app_id + "|" + app_secret
query_num = 10
recent = 5
baseline_post_num = 500


# Error class
class PidError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class NoMessageError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def request_until_succeed(url):
    req = urllib2.Request(url)
    count = 0
    success = False
    while success is False:
        try:
            # try http request for two times.
            if count > 1:
                break
            response = urllib2.urlopen(req)
            if response.getcode() == 200:
                success = True
                break
        except NoMessageError:
            logging.error(NoMessageError)
            count = count + 1

    if success is False:
        # If failed to may connection, just pass an empty dict
        return '{"posts":""}'
        # logging.error("Error for URL %s: %s" % (url, datetime.datetime.now()))

    return response.read()


def get_facebook_page_id_data(page_id, num_statuses):
    """This method will crawl 'num_statuses' number of posts from 'page_id'"""
    base = 'https://graph.facebook.com'
    node = '/v2.9/' + str(page_id)
    parameters = '?fields=posts.limit(%s){message,created_time,shares,likes.limit(0).' \
                 'summary(true),comments.limit(0).summary(true)}&access_token=%s' % (num_statuses, access_token)
    url = base + node + parameters

    response = request_until_succeed(url)
    if response != '':
        data = json.loads(response).get('posts', '')
    else:
        return ''

    return data


def parse_time(raw):
    # just for parsing string into proper time format

    published = datetime.datetime.strptime(raw, '%Y-%m-%dT%H:%M:%S+0000')
    published = published + datetime.timedelta(hours=+8)  # Hong Kong time
    published = published.strftime('%Y-%m-%d %H:%M:%S')  # best time format for spreadsheet programs

    return published


def parse_posts(post):
    # The structure of jsons facebook returned to us
    # was a mass, change them into proper structure.

    result = dict()

    result['pid'] = post.get('id', '')
    result['created_time'] = parse_time(post['created_time'])
    result['content'] = post.get('message', '')
    result['share'] = post.get('shares', dict()).get('count', 0)
    result['comment'] = post.get('comments', dict()).get('summary', dict()).get('total_count', 0)
    result['like'] = post.get('likes', dict()).get('summary', dict()).get('total_count', 0)

    return result


def process_facebook_data(posts):
    response_data = []
    if posts == '':
        return pd.DataFrame()
        # for those connection failure, we just use an empty df

    for post in posts['data']:
        response_data.append(parse_posts(post))

    return pd.DataFrame(response_data)


def get_result_df(num=query_num):
    # first load ids from our 'source.csv'
    ids = pd.read_csv('source.csv')
    total = pd.DataFrame()

    # iterate id lists and request posts from every id in 'source.csv'
    for i in range(ids.shape[0]):
        posts = get_facebook_page_id_data(ids['id'][i], num_statuses=num)
        result = process_facebook_data(posts)
        # denote the source of posts
        result['source'] = ids['name'][i]
        # attach each fb page's posts to total df
        total = pd.concat([total, result])

    return total


def parse_news_df(df, time_delta=recent):
    result = df.copy()
    result.fillna(0, inplace=True)
    result['time'] = [datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S") for i in result['created_time']]
    del result['created_time']

    time_bound = datetime.datetime.now() - datetime.timedelta(days=time_delta)

    result = result[result['time'] > time_bound]
    result['postid'] = range(1, result.shape[0] + 1)
    result.set_index('postid', inplace=True)

    return result


if __name__ == "__main__":
    now = datetime.datetime.now()
    logging.info(now.ctime() + ' A new crawling mission started.')
    posts = get_result_df()
    now = datetime.datetime.now()
    logging.info(now.ctime() + ' Crawling mission finished.')

    result = parse_news_df(posts)

    result['popularity'] = result['like'] + result['comment'] * 1.5 + result['share'] * 2

    now = datetime.datetime.now()
    result.sort_values('popularity', ascending=False).to_csv('past_report/' + now.ctime() + '_report.csv',
                                                             index=False, encoding='utf-8')
    result['record_time'] = now
    result.sort_values('popularity', ascending=False).to_csv('/hdd/import/data/fb_threads/raw/' + now.ctime()
                                                             + '_report.csv', index=False, encoding='utf-8')
    logging.info(now.ctime() + '_report.csv(all posts) has been stored in past_report folder.')
