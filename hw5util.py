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
    localTemp = pd.DataFrame(df)
    if kickOut:
        localTemp = localTemp[localTemp.apply(lambda x : not ifContain(x['role'], roleLst), axis = 1)]
    else:
        localTemp = localTemp[localTemp.apply(lambda x : ifContain(x['role'], roleLst), axis = 1)]
    
    return localTemp

def roleAdder(target, source, roleLst=['neu']):
    localTemp = pd.DataFrame(target)
    for role in roleLst:
        toAdd = source[source['role']==role]
        print(toAdd.shape)
        localTemp = localTemp.append(toAdd)
    
    return localTemp

def wordFilter(df, wordLst = preDefined_stopList, kickOut = True):
    localTemp = pd.DataFrame(df)
    if kickOut:
        localTemp = localTemp[localTemp.apply(lambda x : not ifContain(x['word'], wordLst), axis = 1)]
    else:
        localTemp = localTemp[localTemp.apply(lambda x : ifContain(x['word'], wordLst), axis = 1)]
    return localTemp

def entityFilter(df, wordLst = preDefined_stopList, kickOut = True):
    localTemp = pd.DataFrame(df)
    if kickOut:
        localTemp = localTemp[localTemp.apply(lambda x : not ifContain(x['entity'], wordLst), axis = 1)]
    else:
        localTemp = localTemp[localTemp.apply(lambda x : ifContain(x['entity'], wordLst), axis = 1)]
    return localTemp

def wordLenFilter(df, lowerBound=1, upperBound = -1, kickOut = True):
    localTemp = pd.DataFrame(df)
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
    
    localTemp = pd.DataFrame(df)
    localTemp.index = list(range(localTemp.shape[0]))
    
    indices = wordFilter(localTemp, wordLst=desiredWord, kickOut=False).index
    expandedIndices = []
    intervalTag = []
    innerIdx = []
    for i, idx in enumerate(indices):
        #print(idx)
        thisArticleID = localTemp.loc[idx,'articleID']
        newIndices = list(range(idx-width_pre, idx+width_post))
        if removeSelf:
            newIndices.remove(idx)
        try:    
            window = localTemp[localTemp['articleID']==thisArticleID]
            window = window.reindex(newIndices)['articleID']
            #window = window.loc[newIndices,'articleID']
            window.dropna(axis=0,inplace=True)
            newIndices = window.index
        except KeyError:
            newIndices = []
            
        expandedIndices.extend(newIndices)
        intervalTag.extend([f'interval_{i}']*len(newIndices))
        innerIdx.extend(list(range(len(newIndices))))
        
    toReturn = localTemp.loc[expandedIndices]
    toReturn['interval_n'] = intervalTag
    toReturn['innerIdx'] = innerIdx
    
    return toReturn

def idFilter(target, desiredIdSeries):
    return desiredIdSeries.merge(target, on = 'articleID', how='left')


###########################################################
#                     aggregate fcn                       #
###########################################################
    
def count_gby(df, colName):
    temp = df.groupby([colName]).count().iloc[:,0:1]
    temp.columns = ['count']    
    return temp
    
def count_GbyRole(df, ascending = False):
    temp = count_gby(df, 'role')
    return temp.sort_values(by = 'count', ascending=ascending)

def count_GbyWord(df, ascending = False):
    temp = count_gby(df, 'word')
    return temp.sort_values(by = 'count', ascending=ascending)

def count_GbyEntity(df, ascending = False):
    temp = count_gby(df, 'entity')
    return temp.sort_values(by = 'count', ascending=ascending)

###########################################################
#                          time                           #
###########################################################
    
def timeFilter_getID(otherColdf, lowerBound, upperBound):
    localTemp = pd.DataFrame(otherColdf[['id','post_time']])
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
