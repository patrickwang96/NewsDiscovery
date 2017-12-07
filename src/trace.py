#!/python/ENV/bin/python
# coding: utf-8

import pandas as pd
import numpy as np
import glob 
# import heat_topic_trend as ht
import datetime
import os
from sklearn import linear_model
lr = linear_model.LinearRegression()
# analyze latest 2 hour fb posts
time_range = 2


def get_report_name():

    # sort in time order and returned 

    report_names = glob.glob('past_report/*_report.csv')
    report_time = [datetime.datetime.strptime(i, 'past_report/%a %b %d %H:%M:%S %Y_report.csv') for i in report_names]
    report_df = pd.DataFrame([report_names, report_time]).T
    report_df.columns = ['name', 'time']
    report_df = report_df.sort_values('time', ascending=False)

    return report_df


def id2url():
    urls = 'facebook.com/' + np.array(time_df.columns.values)
    id = range(1, len(urls)+1)
    url_table = pd.DataFrame(np.array([id, urls, np.array(time_df.columns.values)])).T
    url_table.columns = ['id', 'url', 'pid']
    url_table.set_index('id', inplace=True)
    # url_table.to_csv('daily_submit/id2url.csv')
    return url_table


def linreg(num, df):
    lr.fit(pd.DataFrame(np.array(list(reversed(range(len(df[num].dropna())))))+1), pd.DataFrame(df[num].dropna()))
    return lr.coef_[0][0]


# get file names created within 'time_range' (2) hours.
names = get_report_name()
time_bound = datetime.datetime.now() - datetime.timedelta(hours=time_range)
names = names[names['time'] > time_bound]


tmp_list = np.array(names.iloc[:]['name'])
tmp_time = np.array(names.iloc[:]['time'])
current = pd.read_csv(tmp_list[0], usecols=['pid', 'popularity', 'time'])
current.time = pd.to_datetime(current.time)
current = current[current['time'] > time_bound]
del current['time']
current.columns = ['pid', tmp_time[0]]

# import 'popularity' in past 'time_range'
for i in range(1, len(tmp_list)):
    tmp = pd.read_csv(tmp_list[i], usecols=['pid', 'popularity', 'time']).drop_duplicates()
    tmp.time = pd.to_datetime(tmp.time,errors='coerce')
    tmp = tmp[tmp['time'] > time_bound]
    tmp.dropna(inplace=True)
    del tmp['time']
    tmp.columns = ['pid', tmp_time[i]]
    current = pd.merge(current, tmp, how='left', left_on='pid', right_on='pid')

current.drop_duplicates(subset='pid',inplace=True)


time_df = current.set_index('pid').T

url_table = id2url()

time_df.columns = range(1, len(time_df.columns.values)+1)


# get the regression result

reg_result = list()
stage_list = list()
for i in time_df.columns.values:
    reg_result.append(linreg(i, time_df))
    stage_list.append(len(time_df[i].dropna()))

result = pd.DataFrame([time_df.columns.values, reg_result, stage_list]).T
result.columns = ['id', 'slope', 'stage']
result.id = result.id.astype(int)
result.set_index('id', inplace=True)


result = pd.merge(url_table, result, right_index=True, left_index=True)
result = pd.merge(result,
                  pd.read_csv(tmp_list[0],
                              usecols=['pid', 'popularity', 'time', 'source', 'content']).drop_duplicates(),
                  how='left', right_on='pid', left_on='pid')

result.stage = result.stage.astype(np.int64)
result['id'] = range(1, result.shape[0]+1)
result.set_index('id', inplace=True)

result = result[result.popularity > 40]


def normalize_df(source):
    df = source.copy()
    df.stage = df.stage.astype(int)

    avg_baseline = pd.read_csv('get_baseline/avg_baseline.csv', index_col=False)
    std_baseline = pd.read_csv('get_baseline/std_baseline.csv', index_col=False)

    avg_baseline_map = pd.melt(avg_baseline, id_vars=['source'], value_vars=[str(i) for i in range(1, 13)])
    std_baseline_map = pd.melt(std_baseline, id_vars=['source'], value_vars=[str(i) for i in range(1, 13)])

    avg_baseline_map.columns = ['source', 'stage', 'avg']
    std_baseline_map.columns = ['source', 'stage', 'std']
    avg_baseline_map.stage = avg_baseline_map.stage.astype(int)
    std_baseline_map.stage = std_baseline_map.stage.astype(int)
    
    df = pd.merge(df, avg_baseline_map, on=['source', 'stage'], how='left')
    df = pd.merge(df, std_baseline_map, on=['source', 'stage'], how='left')
    
    df['std'].replace(to_replace=0.0, value=1.0, inplace=True)

  # standardize
    df['slope'] = (df['slope'] - df['avg'])/df['std']

    return df.sort_values('slope', ascending=False)


test = normalize_df(result)

cmd = 'echo "hot topics submit(standarded with baseline:-)" | /bin/mail -s "Hot Topics" '
should_send = False

# ====================
# newly added lastest 20 mins slope df

recent_time_df = time_df.iloc[:3, :]
recent_reg_result = []
for i in recent_time_df.columns.values:
    recent_reg_result.append(linreg(i, recent_time_df))
recent_result = pd.DataFrame([recent_time_df.columns.values, recent_reg_result, stage_list]).T
recent_result.columns = ['id', 'slope', 'stage']
recent_result.id = recent_result.id.astype(int)
recent_result.set_index('id', inplace=True)
recent_result = pd.merge(url_table, recent_result, right_index=True, left_index=True)
recent_result = pd.merge(recent_result, pd.read_csv(tmp_list[0],
                                                    usecols=['pid', 'popularity', 'time', 'source', 'content']),
                         how='left', right_on='pid', left_on='pid')

recent_result['id'] = range(1, recent_result.shape[0]+1)
recent_result.set_index('id', inplace=True)
recent_standardize_df = normalize_df(recent_result)
recent_standardize_df.sort_values('slope', ascending=False)

recent_standardize_df.drop_duplicates(inplace=True)

if sum(np.array(recent_standardize_df['slope'] > 1.65)) > 0:
    should_send = True
    cmd = cmd + ' -a daily_submit/20min_standardized_hot_topics95.csv '
    st_result = recent_standardize_df[recent_standardize_df['slope'] > 1.65].sort_values('slope', ascending=False)
    st_result.to_csv('daily_submit/20min_standardized_hot_topics95.csv')
if sum(np.array(recent_standardize_df['slope'] > 0.85)) > 0:
    should_send = True
    cmd = cmd + ' -a daily_submit/20min_standardized_hot_topics80.csv '
    st_result = recent_standardize_df[recent_standardize_df['slope'] > 0.85].sort_values('slope', ascending=False)
    st_result.to_csv('daily_submit/20min_standardized_hot_topics80.csv')

# ====================

# result.sort_values('slope',ascending=False).head(n=10).to_csv('daily_submit/current_hot_topics.csv')
if sum(np.array(test['slope'] > 1.65)) > 0:
    should_send = True
    cmd = cmd + ' -a daily_submit/standardized_hot_topics95.csv '
    st_result = test[test['slope'] > 1.65].sort_values('slope', ascending=False)
    st_result.to_csv('daily_submit/standardized_hot_topics95.csv')
if sum(np.array(test['slope'] > 0.85)) > 0:
    should_send = True
    cmd = cmd + ' -a daily_submit/standardized_hot_topics80.csv '
    st_result = test[test['slope'] > 0.85].sort_values('slope', ascending=False)
    st_result.to_csv('daily_submit/standardized_hot_topics80.csv')

cmd = cmd + '  patrick.wang@networld.hk, jason.tsang@networld.hk'
if should_send:
    os.system(cmd)
#else: print "nothing send"

# ====================
# create baseline log

# the two df's shape may not be the same\
# baseline_trace = time_df.copy()
# baseline_result = result.copy()

# # assert baseline_trace.shape == baseline_result.shape
# baseline_trace.columns = np.array(url_table.pid)
# stage_list = []
# for i in baseline_trace.columns.values:
# #     baseline_reg_result.append(linreg(i,baseline_trace))
#     stage_list.append(len(baseline_trace[i].dropna()))
# baseline_result['stage'] = stage_list
del result['url']
del result['content']
del result['time']
del result['popularity']
result.to_csv('baseline/' + datetime.datetime.now().ctime() + '_slope_log.csv', index=False, encoding='utf-8')

# ===================
