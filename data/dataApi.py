# -*-coding: utf-8 -*-
# Python 3.6
# Author:Zhang Haitao
# Email:13163385579@163.com
# TIME:2018-04-24  21:19
# NAME:assetPricing2-dataApi.py
import os
import pickle

from config import PKL_PATH
from data.dataTools import load_data, save, save_to_filtered
import pandas as pd
from data.sampleControl import apply_condition
from indicators_new.indicators_filter import refine


def combine_all_indicators():
    fns=['size','beta','value','momentum','reversal','liquidity','skewness','idio']

    xs=[]
    info={}
    for fn in fns:
        x=load_data(fn)
        # stack those panel with only one indicators such as reversal
        if not isinstance(x.index,pd.MultiIndex):
            if x.columns.name=='sid':
                x = x.stack().to_frame()
                x.columns = [fn]

        x.columns = pd.Index(['{}__{}'.format(fn, col) for col in x.columns], x.columns.name)
        xs.append(x)
        info[fn]=x.columns.tolist()

    indicators=pd.concat(xs,axis=1)
    return indicators,info

def combine_all_benchmarks():
    models=['capmM', 'ff3M', 'ffcM', 'ff5M', 'hxz4M']
    xs=[]
    info={}
    for model in models:
        x=load_data(model)
        if x.ndim==1:# such as capmM
            x.name='{}__{}'.format(model,x.name)
        else:
            x.columns=pd.Index(['{}__{}'.format(model,col) for col in x.columns],name=x.columns.name)
        xs.append(x)

        if x.ndim==1: # model with only one column such as capmM
            info[model]=[x.name]
        else:
            info[model]=x.columns.tolist()
    benchmark=pd.concat(xs,axis=1)
    return benchmark,info

def join_all():
    # --------------------time T---------------------------------
    weight=load_data('size')['mktCap']
    weight.name='weight'

    indicators,info_indicators=combine_all_indicators()
    indicators=indicators.groupby('sid').shift(1)
    '''
        all the indicators are shift forward one month except for eret,rf and other base data,
    so the index denotes time t+1,and all the indicators are from time t,the base data are from 
    time t+1.We adjust the indicators rather than the base data for these reasons:
    1. we will sort the indicators in time t to construct portfolios and analyse the eret in time
        t+1
    2. We need to make sure that the index for eret and benchmark is corresponding to the time when 
    it was calcualted. If we shift back the base data in this place (rather than shift forward the
    indicators),we would have to shift forward eret again when we regress the portfolio eret on 
    benckmark model in the function _alpha in template.py

    For simply,we use the information at t to predict the eret of time t+1.In our DATA.data,the index
    denotes time t,and the values for eretM,benchmark model and so on is from time t+1.

    Notice:
        To calculate value-weighted result,we use the market capitalization of the time t (portfolio
        formation period) as weight.So,in this place,we should shift the capM forward for one step
        as well.For more details,refer to page 40 of Bali.

    '''
    # -----------------------------time T+1--------------------------------------
    stockEretM=load_data('stockEretM')
    stockEretM=stockEretM.stack()
    stockEretM.name='stockEretM'

    rfM=load_data('rfM')
    mktRetM=load_data('mktRetM')
    rpM=load_data('rpM')
    benchmark,info_benchmark=combine_all_benchmarks()

    #combine singleIndexed
    single=pd.concat([rfM,mktRetM,rpM,benchmark],axis=1)

    #combine multiIndexed
    multi=pd.concat([weight,indicators,stockEretM],axis=1)
    data=multi.join(single,how='outer')
    data.index.name=['t','sid']
    data.columns.name='type'


    info={**info_benchmark,**info_indicators}
    pickle.dump(info,open(os.path.join(PKL_PATH,'info.pkl'),'wb'))

    # save info as df
    infoDf=pd.concat([pd.Series(v,name=k) for k,v in info.items()],axis=1)
    infoDf.to_csv('info.csv')

    save(data,'data')

def refine_data():
    data=load_data('data')
    data=refine(data)
    save_to_filtered(data,'data')

    data_controlled=apply_condition(data)
    save_to_filtered(data_controlled,'data_controlled')

class Database:
    def __init__(self,sample_control=True):
        if sample_control:
            self.data=load_data('data_controlled')
        else:
            self.data=load_data('data')
        self.info=load_data('info')

    def by_factor(self,factorname):
        return self.data[self.info[factorname]].copy(deep=True).dropna(how='all')

    def by_indicators(self,indicators):
        '''
        no mather indicators is just a string represent one indicators
        or list (tuple),the function will return a DataFrame
        :param indicators:
        :return: DataFrame
        '''
        if isinstance(indicators,(list,tuple)):
            return self.data[list(indicators)].copy(deep=True).dropna(how='all')
        else:
            return self.data[[indicators]].copy(deep=True).dropna(how='all')


if __name__ == '__main__':
    join_all()
    refine_data()




#TODO:deal with sample control and detect outliers

