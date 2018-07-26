#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pandas as pd
import numpy as np
from pymongo import MongoClient
import configparser

class GenerateNewPTs:

    def __init__(self):
        self.n_differs = 2
        self.old_pt = dict()
        self.old_pt_dict = dict()
        self.df_com_features = pd.DataFrame()

    ''' 读取配置文件中的db数据并将需要连接 '''
    def read_config(self):
        cf = configparser.ConfigParser()
        cf.read('config.ini')
        db_config = dict()
        db_config['db_host'] = cf.get('db', 'db_host')
        db_config['db_port'] = cf.get('db', 'db_port')
        db_config['db_user'] = cf.get('db', 'db_user')
        db_config['db_pwd'] = cf.get('db', 'db_pwd')
        return db_config

    ''' mongodb的连接 '''
    def mongodb_conn(self):
        db_config = self.read_config()
        # host=None,port=None,document_class=dict,tz_aware=None,connect=None
        client = MongoClient(host=db_config['db_host'], port=int(db_config['db_port']))
        db = client.ai_explore
        db.authenticate(db_config['db_user'], db_config['db_pwd'])
        return db, client

    ''' 将获取的属性的概率值由dict{behaviors:{},interests:{}}转化为dataframe[id,rate,sign]'''
    def transformate_to_df(self, values_prob):
        self.df_com_features = pd.DataFrame()
        behaviors_prob = values_prob['behaviors']
        for k, v in behaviors_prob.items():
            self.df_com_features = self.df_com_features.append(pd.DataFrame({'id': k, 'rate': v, 'sign': 1}, index=[0]))

        interests_prob = values_prob['interests']
        for k, v in interests_prob.items():
            self.df_com_features = self.df_com_features.append(pd.DataFrame({'id': k, 'rate': v, 'sign': 2}, index=[0]))
        self.df_com_features.reset_index(drop=True, inplace=True)
        self.df_com_features.sort_values(by=['rate'], ascending=False, inplace=True)

    ''' 将获得的pt转化为dict dict[name]=id'''
    def get_value_dict(self):
        behaviors = self.old_pt['pt']['adset_spec']['targeting']['behaviors']
        if isinstance(behaviors, list):
            for index in range(len(behaviors)):
                behavior = behaviors[index]
                self.old_pt_dict[behavior['id']] = behavior['name']
        elif isinstance(behaviors, dict):
            for k, v in behaviors.items():
                self.old_pt_dict[v['id']] = v['name']

        interests = self.old_pt['pt']['adset_spec']['targeting']['interests']
        if isinstance(interests, list):
            for index in range(len(interests)):
                interest = interests[index]
                self.old_pt_dict[interest['id']] = interest['name']
        elif isinstance(interests, dict):
            for k, v in interests.items():
                self.old_pt_dict[v['id']] = v['name']

    ''' 产生新pt的主进入口 '''
    def get_new_pt(self):
        pt_behaviors_ads = [[] for _ in range(self.n_differs)]
        pt_behaviors_tmp = [0 for _ in range(self.n_differs)]
        pt_interests_ads = [[] for _ in range(self.n_differs)]
        pt_interests_tmp = pt_behaviors_tmp.copy()
        self.df_com_features.apply(lambda df: self.judge_give(df, pt_behaviors_ads, pt_behaviors_tmp,
                                                              pt_interests_ads, pt_interests_tmp), axis=1)
        npts = self.reverse_generate_new_pt(pt_behaviors_ads, pt_interests_ads)
        return npts

    ''' 将排好序的概率值进行划分并进行判断 '''
    def judge_give(self, df, pt_behaviors_ads, pt_behaviors_tmp, pt_interests_ads, pt_interests_tmp):
        if df['sign'] == 1:
            cindex = self.cmp_value(pt_behaviors_tmp, df['rate'])
            pt_behaviors_ads[cindex].append(df['id'])
        else:
            cindex = self.cmp_value(pt_interests_tmp, df['rate'])
            pt_interests_ads[cindex].append(df['id'])

    ''' 比较信息熵（-plogp），然后将待选择的id放入到指定的集合 '''
    def cmp_value(self, pt_tmp, tmp_value):
        tindex = pt_tmp.index(min(pt_tmp))
        pt_tmp[tindex] = pt_tmp[tindex] - tmp_value * np.log2(tmp_value)
        return tindex

    ''' 将生成的新的behaviors和interests合并成新的pt '''
    def reverse_generate_new_pt(self, pt_behaviors_ads=None, pt_interests_ads=None):
        tmp_pts = []
        for index in range(self.n_differs):
            pt_interests = {}
            pt_behaviors = {}
            for bindex in range(len(pt_behaviors_ads[index])):
                bid = str(pt_behaviors_ads[index][bindex])
                if self.old_pt_dict.get(bid):
                    pt_behaviors[str(bindex)] = {'id': bid, 'name': self.old_pt_dict[bid]}

            for iindex in range(len(pt_interests_ads[index])):
                iid = pt_interests_ads[index][iindex]
                if self.old_pt_dict.get(iid):
                    pt_interests[str(iindex)] = {'id': iid, 'name': self.old_pt_dict[iid]}
            self.old_pt['pt']['adset_spec']['targeting']['behaviors'] = pt_behaviors
            self.old_pt['pt']['adset_spec']['targeting']['interests'] = pt_interests
            tmp_pts.append(self.old_pt)
        return tmp_pts

    ''' 接收一个条件参数进行查询并获取创建时间最近的一个广告的pt并返回 '''
    def find_a_ads(self, condition='bet4_ios_us'):
        db, client = self.mongodb_conn()
        colles_ads = db.ads.find({'delt_name': condition}, {'_id': 0, 'pt': 1}).sort([('create_time', -1)]).limit(1)
        tmp_pt = dict()
        for item in colles_ads:
            tmp_pt = item
        client.close()
        return tmp_pt

    ''' 
    修改pt中的名字以标注此广告由本程序编写投放
    1、pt.name
    2、pt.adset_spec.name
    3、pt.adset_spec.campaign_spec.name
     '''
    def add_name_sign(self, old_pt):
        s = ' [plogp]'
        old_pt['pt']['name'] = old_pt['pt']['name']+ s
        old_pt['pt']['adset_spec']['name'] = old_pt['pt']['adset_spec']['name'] + s
        old_pt['pt']['adset_spec']['campaign_spec']['name'] = old_pt['pt']['adset_spec']['campaign_spec']['name'] + s
        return old_pt

    ''' main主进入口'''
    def main(self, old_pt, value_calc_prob=None, n_differs=2):
        self.n_differs = n_differs
        self.old_pt = self.add_name_sign(old_pt)
        self.get_value_dict()
        self.transformate_to_df(value_calc_prob)
        newpts = self.get_new_pt()
        return newpts


if __name__ == '__main__':
    gnpt = GenerateNewPTs()
    pt = gnpt.find_a_ads()
    import heapp
    value_prob = heapp.test()
    pts = gnpt.main(pt, value_prob, 3)
    print('local test!!!')


