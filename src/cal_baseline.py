#!/python/ENV/bin/python
# coding: utf-8
import pandas as pd
import numpy as np
import glob 
import datetime
import os


def get_log_name():
    report_names = glob.glob('baseline/*_slope_log.csv')

    return report_names

names = get_log_name()
current = pd.read_csv(names[0])
for i in names[1:]:
    tmp = pd.read_csv(i)
    current = current.append(tmp)

current.stage = current.stage.astype(np.int64)
current.to_csv("get_baseline/log.csv", index=False, encoding='utf-8')
os.system('java -jar baseline.jar')
