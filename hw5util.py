# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path
import re

def readOtherCol(sourcePath):
    theTb = pd.read_csv(next(Path(sourcePath).glob('otherCol.csv')),
                        encoding = 'utf-8-sig')
    try:
        theTb['post_time'] = pd.to_datetime(theTb['post_time'])
    except:
        print('something wrong when dealing with col, /"post_time/"')
        print('return None')
        return None
    
    theTb.columns=['articleID', 'p_type', 's_id', 's_area_id', 's_name', 's_area_name',
                   'content_type', 'main_id', 'content_no', 'comment_count',
                   'post_time', 'title', 'author', 'page_url', 'negative_score',
                   'positive_score', 'pos', 'neg']
    return theTb

def readAndAppend(pathLst, sep = ","):
    if len(pathLst) <= 0:
        print("no csv file fond.")
        raise AttributeError
    
    for filePath in pathLst:
        print(filePath)
    
    theTb = pd.DataFrame()
    for posPath in pathLst:
        try:
            temp = pd.read_csv(posPath, sep = sep, engine='python', encoding='utf-8-sig')
        except:
            print(f'something went wrong when loading with {posPath}')
            print('this file has been skipped')
            continue
    
        try:
            theTb = theTb.append(temp, ignore_index = True)
        except:
            print(f'something went wrong when appending with {posPath}')
            print('this file has been skipped')
        
    return theTb

def readBrandPos(brandName, dataFolder=".\\", sep = ","):
    """
    把所有XXX_pos.csv檔案讀進來成為一個檔案
    不要亂改檔名
    """
    dataFolder = Path(f".\\{dataFolder}")
    if not dataFolder.exists():
        print("Folder not found.")
        raise AttributeError

    posTbList = list(Path(f".\{dataFolder}\\").glob(f"{brandName}*_posTB*.csv"))
    
    if len(posTbList) <= 0:
        print("no csv file fond.")
        raise AttributeError
    
    brandPosTb = readAndAppend(posTbList, sep)
            
    return brandPosTb

def readBrandEntity(brandName, dataFolder=".\\", sep = ","):
    dataFolder = Path(f".\\{dataFolder}")
    if not dataFolder.exists():
        print("Folder not found.")
        raise AttributeError

    entityTbList = list(Path(f".\{dataFolder}\\").glob(f"{brandName}*_entityTB*.csv"))
    
    if len(entityTbList) <= 0:
        print("no csv file fond.")
        raise AttributeError
        
    entityPosTb = readAndAppend(entityTbList)
        
    return entityPosTb

###########################################################
#                       filter fcn                        #
###########################################################


def ifContain(LongStr, shortStrLst, OR = True, ignoreCase = True):
    LongStr = LongStr.replace('\n\r','')
    reRuleLst = []
    if ignoreCase:
        for stuff in shortStrLst:
            reRuleLst.append(re.compile(f".*{stuff}.*", re.IGNORECASE))
    else:
        for stuff in shortStrLst:
            reRuleLst.append(re.compile(f".*{stuff}.*"))
            
    if OR:
        for rule in reRuleLst:
            result = rule.match(LongStr)
            if result:
                return True
        return False
    else:
        for rule in reRuleLst:
            result = rule.match(LongStr)
            if not result:
                return False
        return True

def lenFilter(string, lowerBound, upperBound):
    lowerBound = max(0, lowerBound)
    lowerBound = int(lowerBound)
    strLen = len(string)
    if upperBound <= 0:
        return strLen > lowerBound
    else:
        upperBound = int(upperBound)
        return strLen < upperBound and strLen > lowerBound
    
def inFilter(string, lst):
    return string in lst

preDefined_disLikeRole = ['Nd', 'Neu', 'Nes', 'Di', 'Da','P','T'
                          'I', 'category','FW', "Caa", "Cab",
                          "Cba", 'Cbb', 't', 'de', 'shi', 'whitespace']

preDefined_stopList = ["手機","可以","使用","com","所以","還是","真的","大家",
            "G","問題","知道","應該","選擇","看到","不會","謝謝",
            "大概","請問","感覺","比較","其他","一樣","台灣","不過",
            "但是","希望","不要","以上","什麼","推薦","--","考慮","如果",
            "這樣","說明","各位","自己","可能","例如","部分","需要","有點",
            "然後","補充","已經","其實","很多","好像","系列","時間","一些",
            "一點","之後","文章","網路","旗艦","規格","\n"]


def roleFilter(df, roleLst=preDefined_disLikeRole, kickOut = True):
    localTemp = df.copy(deep=True)
    if kickOut:
        localTemp = localTemp[localTemp.apply(lambda x : not ifContain(x['role'], roleLst), axis = 1)]
    else:
        localTemp = localTemp[localTemp.apply(lambda x : ifContain(x['role'], roleLst), axis = 1)]
    
    return localTemp

def roleAdder(target, source, roleLst=['neu']):
    localTemp = target.copy(deep=True)
    for role in roleLst:
        toAdd = source[source['role']==role]
        print(toAdd.shape)
        localTemp = localTemp.append(toAdd)
    
    return localTemp

def wordFilter(df, wordLst = preDefined_stopList, kickOut = True):
    localTemp = df.copy(deep=True)
    if kickOut:
        localTemp = localTemp[localTemp.apply(lambda x : not ifContain(x['word'], wordLst), axis = 1)]
    else:
        localTemp = localTemp[localTemp.apply(lambda x : ifContain(x['word'], wordLst), axis = 1)]
    return localTemp

def entityFilter(df, wordLst = preDefined_stopList, kickOut = True):
    localTemp = df.copy(deep=True)
    if kickOut:
        localTemp = localTemp[localTemp.apply(lambda x : not ifContain(x['entity'], wordLst), axis = 1)]
    else:
        localTemp = localTemp[localTemp.apply(lambda x : ifContain(x['entity'], wordLst), axis = 1)]
    return localTemp

def wordLenFilter(df, lowerBound=1, upperBound = -1, kickOut = True):
    localTemp = df.copy(deep=True)
    if kickOut:
        filterSer = localTemp.apply(lambda x : lenFilter(x['word'],
                                                             lowerBound,
                                                             upperBound),
                                    axis = 1)
        
                
    else:
        filterSer = localTemp.apply(lambda x : not lenFilter(x['word'],
                                                         lowerBound,
                                                         upperBound),
                                    axis = 1)
    localTemp = localTemp[filterSer]
    return localTemp

def nearBy(df, desiredWord, width_pre = 5, width_post = 5, removeSelf=True):
    if len(desiredWord) == 0:
        print('no word specified.')
        return df
    
    if type(desiredWord) != list:
        print('need to be list')
        return df
    
    localTemp = df.copy(deep=True)
    try:
        localTemp.reset_index(level=0, inplace=True)
        localTemp.set_index(['articleID', 'wordCnt'], inplace = True)
    except:
        print('something went wrong, check if its a \" POS \" table')
        
    indices = wordFilter(localTemp, wordLst=desiredWord, kickOut=False).index
    IDX = pd.IndexSlice
    
    toReturn = pd.DataFrame(columns=['articleID', 'wordCnt', 'index',
                                     'role', 'word', 'interval_n', 'innerIdx'])
    toReturn.set_index(['articleID', 'wordCnt'], inplace=True)
    
    for i, idx in enumerate(indices):
        ub = idx[1]+width_post
        lb = idx[1]-width_pre
        temp = localTemp.loc[IDX[idx[0],:],:]
        temp2 = temp.loc[IDX[:,lb:ub],:]
        del temp
        temp2['interval_n'] = i
        temp2['innerIdx'] = list(range(temp2.shape[0]))
        toReturn = pd.concat([toReturn, temp2], axis = 0)
        
    toReturn.reset_index(level=[0,1], inplace = True)
    toReturn.set_index('index', inplace = True)
    toReturn.index.name=None
    return toReturn
    
    
def idFilter(target, desiredIdSeries):
    return desiredIdSeries.merge(target, on = 'articleID', how='inner')


###########################################################
#                     aggregate fcn                       #
###########################################################
    
def count_gby(df, colName, porpotion='Fasle'):
    temp = df.groupby([colName]).count().iloc[:,0:1]
    temp.columns = ['count']
    
    return temp
    
def count_GbyRole(df, ascending = False):
    temp = count_gby(df, 'role')
    return temp.sort_values(by = 'count', ascending=ascending)

def count_GbyWord(df, ascending = False):
    temp = count_gby(df, 'word')
    return temp.sort_values(by = 'count', ascending=ascending)

def porpotion_gby(df, colName):
    return None

def porpotion_GbyWord(df, ascending = False):
    totalArticleCnt = df.articleID.nunique()
    temp = df.groupby(['word']).nunique('articleID').iloc[:,0:1]
    temp['articleID'] = temp['articleID'] / totalArticleCnt
    temp.columns = ['porpotion']
    
    return temp.sort_values(by = 'porpotion', ascending=ascending)
    

def count_GbyEntity(df, ascending = False):
    temp = count_gby(df, 'entity')
    return temp.sort_values(by = 'count', ascending=ascending)

###########################################################
#                          time                           #
###########################################################
    
def timeFilter_getID(otherColdf, lowerBound, upperBound):
    localTemp = pd.DataFrame(otherColdf[['articleID','post_time']])
    try:
        localTemp = localTemp[localTemp['post_time'] <= upperBound]
        #print(localTemp.shape)
    except:
        print('upperbound failure, no upperBound applied')
    
    try:
        localTemp = localTemp[localTemp['post_time'] >= lowerBound]
        #print(localTemp.shape)
    except:
        print('lowerBound failure, no lowerBound applied')
        
    localTemp.columns=['articleID', 'post_time']

    return localTemp.iloc[:, 0:1]

def timeFilter(target, otherColdf, lowerBound, upperBound):
    ids = timeFilter_getID(otherColdf, lowerBound, upperBound)
    localTemp = pd.DataFrame(target)
    localTemp = idFilter(localTemp, ids)

    return localTemp
