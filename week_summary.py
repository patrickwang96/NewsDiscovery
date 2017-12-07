#!/python/ENV/bin/python
# coding: utf-8

import pandas as pd
import numpy as np
import glob
from pandas import ExcelWriter

import datetime
from sklearn import linear_model

import sys

lr = linear_model.LinearRegression()

time_range = 2


def get_report_name():

    # sort in time order and returned

    report_names = glob.glob('past_report/*_report.csv')
    report_time = [datetime.datetime.strptime(i, 'past_report/%a %b %d %H:%M:%S %Y_report.csv') for i in report_names]
    report_df = pd.DataFrame([report_names, report_time]).T
    report_df.columns = ['name', 'time']
    report_df = report_df.sort_values('time', ascending=False)

    return report_df


def id2url(time_df):
    urls = 'facebook.com/' + np.array(time_df.columns.values)
    id = range(1, len(urls)+1)
    url_table = pd.DataFrame(np.array([id, urls, np.array(time_df.columns.values)])).T
    url_table.columns = ['id', 'url', 'pid']
    url_table.set_index('id', inplace=True)

    return url_table


def linreg(num, df):
    lr.fit(pd.DataFrame(np.array(list(reversed(range(len(df[num].dropna())))))+1), pd.DataFrame(df[num].dropna()))
    return lr.coef_[0][0]


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
    df['slope'] = (df['slope'] - df['avg']) / df['std']

    return df.sort_values('slope', ascending=False)


names_all = get_report_name()

def getresult(start_time):

    # get file names created within 'time_range' (2) hours.

    # names = get_report_name()
    time_bound = start_time - datetime.timedelta(hours=time_range)
    names = names_all[(names_all.time <= start_time) & (names_all.time >= time_bound)]

    assert names.shape[0] == 12, 'Tme slots number has to be 12.'

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
        tmp.time = pd.to_datetime(tmp.time, errors='coerce')
        tmp = tmp[tmp['time'] > time_bound]
        tmp.dropna(inplace=True)
        del tmp['time']
        tmp.columns = ['pid', tmp_time[i]]
        current = pd.merge(current, tmp, how='left', left_on='pid', right_on='pid')

    current.drop_duplicates(subset='pid', inplace=True)

    time_df = current.set_index('pid').T

    url_table = id2url(time_df)

    time_df.columns = range(1, len(time_df.columns.values) + 1)

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
    result['id'] = range(1, result.shape[0] + 1)
    result.set_index('id', inplace=True)

    result = result[result.popularity > 40]

    test = normalize_df(result)

    print ("Done with " + start_time.ctime())

    if sum(np.array(test['slope'] > 1.65)) > 0:
        st_result = test[test['slope'] > 1.65].sort_values('slope', ascending=False)
        # st_result.to_csv('daily_submit/standardized_hot_topics95_{}.csv'.format(start_time))
        st_result['found_time'] = start_time
        return st_result


def getdfs(query, end_point, period):
    while query < end_point:
        query = query + period
        yield getresult(query - period)


if __name__ == '__main__':

    start_str = sys.argv[1]

    start_time = datetime.datetime.strptime('%Y/%m/%d')
    # start_time = datetime.datetime(2017, 10, 2)
    one_day = datetime.timedelta(days=1)

    # end_time = start_time + one_day

    period = datetime.timedelta(minutes=10)

    writer = ExcelWriter('week_summary.xlsx')
    for i in range(1, 8):
        end_time = start_time + one_day * i

        query_point = end_time - one_day

        day_df = pd.concat(getdfs(query_point, end_time, period)).drop_duplicates(subset='pid')
        day_df.to_excel(writer, (end_time - one_day).strftime('%a'))

    writer.save()
