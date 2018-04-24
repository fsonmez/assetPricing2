
'''
1. Li and Galvani, “Market States, Sentiment, and Momentum in the Corporate Bond Market.”
    page 254
2. Cooper Michael J., Gutierrez Roberto C., and Hameed Allaudeen, “Market States and Momentum.”
'''

import pandas as pd
import numpy as np
from functools import partial


from data.dataTools import load_data, save_to_filtered
import statsmodels.formula.api as sm
from collections import OrderedDict
from tool import groupby_rolling


def get_upDown():
    '''
    2. Cooper Michael J., Gutierrez Roberto C., and Hameed Allaudeen, “Market States and Momentum.”

    :return:
    '''
    mktRetM=load_data('mktRetM')
    windows=[12,24,36]
    series=[]
    for window in windows:
        s=mktRetM.rolling(window=window).sum()
        s=s.shift(1)
        s[s>0]=1
        s[s<0]=-1
        series.append(s)

    upDown=pd.concat(series,axis=1,keys=windows)
    save_to_filtered(upDown, 'upDown')

def cal_market_states():
    '''
    market states:
        search for 'market state' in zoter
    1. Cheema and Nartea, “Momentum Returns, Market States, and Market Dynamics.”  chapter 3.1:
    Following Chui et al. (2010), we set stocks with monthly returns greater (lower) than 100 (−95) percent equal to 100
(−95) percent to avoid the influence of extreme returns and any possible data recording errors.

    :return:
    '''
    upDown=load_data('upDown')
    pass

if __name__ == '__main__':
    get_upDown()