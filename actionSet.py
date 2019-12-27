# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 22:04:00 2019

@author: Kun Lun Huang
"""
from hw5util import hw5util as util
from matplotlib import pyplot as plt

BRAND_LIST = ['zenfone', 'iphone', 'oppo', 'galaxy', 'p10' ,'mate']

def allPos(sourcePath):
    toReturn = dict()
    for brandName in BRAND_LIST:
        try:
            toReturn[brandName] = util.readBrandPos(brandName, sourcePath)
        except:
            print(f'something wrong with \"{brandName} \"')
    return toReturn

def tripleRefine(df):
    temp = util.roleFilter(df)
    temp = util.wordLenFilter(temp)
    temp = util.wordFilter(temp)
    
    return temp

def barChart(df, title):
    plt.figure(figsize=(20, 10))
    plt.bar(df.index, df['count'])
    plt.xticks(size=15) 
    plt.yticks(size=10)
    plt.title(label=title)
    

def wordHist(df, headCnt, title = ""):
    freqWord = util.count_GbyWord(df).head(headCnt)
    barChart(freqWord, title)

    return freqWord

def entityHist(df, headCnt, title = ""):
    freqWord = util.count_GbyEntity(df).head(headCnt)
    barChart(freqWord, title)
    
    return freqWord

def onlyFW(df):
    return util.roleFilter(df, ['fw'], kickOut=False)