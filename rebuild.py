
# coding: utf-8

import urllib2
import json
import datetime
import pandas as pd

import logging
logging.basicConfig(filename='log/hot_topic.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

import numpy as np
import glob
import os
from sklearn import linear_model


# Define some variables
app_id = '447967258885033'
app_secret = '2c17aac0ec2b4ee668ee8ec84fe931e4'
access_token = app_id + "|" + app_secret
query_num = 50
recent = 5
baseline_post_num = 500

time_range = 2

# send request by url
def request_until_succeed(url):
    req = urllib2.Request(url)
    count = 0
    success = False

    response = None
    while not success:
        try:
            if count > 1:
                # try 2 times for request. else break
                break
            response = urllib2.urlopen(req)
            if response.getcode() == 200:
                success = True
                break
        except Exception, e:
            logging.error(e)
            count = count + 1

    # if not success, return a empty json string
    if not success:
        return '{"post":""}'

    return response.read()


# request data by fb page id, limited by _num_
def crawl_facebook_page_by_id(page_id, num):

    base = 'https://graph.facebook.com'
    node = '/v2.9/' + str(page_id)
    parameters = '?fields=posts.limit(%s){message,created_time,shares,likes.limit(0).' \
                 'summary(true),comments.limit(0).summary(true)}&access_token=%s' % (num, access_token)
    url = base + node + parameters

    result = request_until_succeed(url)

    data = json.loads(result)['posts']

    return data


def parse_time(raw):
    published = datetime.datetime.strptime(raw, '%Y-%m-%dT%H:%M:%S+0000')
    published = published + datetime.timedelta(hours=+8)  # Chinese time zone
    published = published.strftime('%Y-%m-%d %H:%M:%S')

    return published


def parse_posts(post):

    result = dict()
    result['pid'] = post.get('id', '')
    result['created_time'] = parse_time(post['created_time'])
    result['content'] = post.get('message', '')
    result['share'] = post.get('shares', dict()).get('count', 0)
    result['comment'] = post.get('comments', dict()).get('summary', dict()).get('total_count', 0)
    result['like'] = post.get('likes', dict()).get('summary', dict()).get('total_count', 0)

    return result


# parse facebook posts data
def parse_facebook_data(posts):

    parsed_posts = map(parse_posts, posts)

    return pd.DataFrame(parsed_posts)


def crawl(num=query_num):

    source = pd.read_csv('source.csv')

    total = pd.DataFrame()

    for pid in source.id:
        posts = crawl_facebook_page_by_id(pid, num)
        parsed_posts = parse_facebook_data(posts)
        parsed_posts['source'] = source[source.id == pid].name[0]

        total = pd.concat([total, parsed_posts])

    return total


def preprocess_data(df, time_delta=recent):

    result = df.copy()

    result.fillna(0, inplace=True)
    result['time'] = [datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S") for i in result['created_time']]

    del result['created_time']

    time_bound = datetime.datetime.now() - datetime.timedelta(days=time_delta)

    result = result[result['time'] > time_bound]
    result['postid'] = range(1, result.shape[0] + 1)
    result.set_index('postid', inplace=True)

    return result


def past_report_names():
    report_names = glob.glob('past_report/*_report.csv')
    report_time = map(lambda x: datetime.datetime.strptime(x,
                                                           'past_report/%a %b %d %H:%M:%S %Y_report.csv'), report_names)

    report_df = pd.DataFrame([report_names, report_time]).T

    report_df.columns = ['name', 'time']
    report_df = report_df.sort_values('time', ascending=False)

    return report_df


def id2url():
    urls = 'facebook.com/' + np.array(time_df.columns.values)




if __name__ == '__main__':

    logging.info('Periodic crawl mission started.')

    raw_data = crawl()
    logging.info('Crawl mission finished.')

    processed_data = preprocess_data(raw_data)

    processed_data['popularity'] = \
        processed_data['like'] + processed_data['comment'] * 1.5 + processed_data['share'] * 2.

    processed_data.sort_values('popularity', ascending=False).to_csv('past_report/' + datetime.datetime.now().ctime()
                                                                     + '_report.csv', index=False, encoding='utf-8')

    logging.info('Data stored in past_report directory.')

    