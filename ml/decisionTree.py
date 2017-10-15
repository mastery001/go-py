#-*- coding: utf-8 -*-
#!/usr/bin/env python

# 决策树算法

'''
---- 创建决策树 ----
假设有n个特征，依次根据数据增益情况求出最优特征，然后根据特征求出对应的分支
1. 根据数据集选取出最佳特征
2. 计算该特征对应的值分别对应的结果标签--- 可能是结果标签，也可能是其他特征的决策树
'''

from math import log
import operator

############### 划分数据集 start ######################

'''
计算数据集无序程度的方法：
1. 香农熵：熵被定义为信息的期望值,熵越高，则混合的数据越多
2. 基尼不纯度(Gini impurity)：从一个数据集中随机选取子项，度量其被错误分类到其他分组里的概率
'''
# 计算给定数据集的香农熵

def caclShannonEnt(dataSet) :
	# 数据集的个数(标签总数)
	numEntries = len(dataSet)
	# 标签字典
	labelCounts = {}

	for featVal in dataSet :
		# 数据每一行的最后一列为当前标签
		currentLabel = featVal[-1]

		if currentLabel not in labelCounts.keys() :
			labelCounts[currentLabel] = 0
		labelCounts[currentLabel] += 1

	shannotEnt = 0.0

	# 香农熵计算公式
	for key in labelCounts :
		# 当前标签出现的概率（当前标签个数除以标签总数）
		prob = float(labelCounts[key]) / numEntries
		# 以2为底求对数
		shannotEnt += -prob * log(prob , 2)

	return shannotEnt

'''
@description：根据给定特定划分数据集
@param dataSet 数据集
@param axis    列
@param value   指定特征值
'''
def splitDataSet(dataSet , axis , value) :
	retDataSet = []
	for featVec in dataSet :
		# 如果指定列的值符合预期value
		if featVec[axis] == value :
			# 去除axis对应列的值，组成新的行
			# 例如原始数组为[1 , 2 , 3] , axis为0时，reducedFeatVec = [2 , 3] ;axis为1时，reducedFeatVec = [1 , 3]
			reducedFeatVec = featVec[:axis]
			reducedFeatVec.extend(featVec[axis+1 :])
			retDataSet.append(reducedFeatVec)

	return retDataSet

'''
数据格式为：n(feature) + 1(label)
选择最优数据集划分方式
'''
def chooseBestFeatureToSplit(dataSet) :
	# 得到有多少个特征值
	numFeatures = len(dataSet[0]) - 1
	# 整个数据集的香农熵
	baseEntropy = caclShannonEnt(dataSet)

	bestInfoGain = 0.0 ; bestFeature = -1
	for i in range(numFeatures) :
		# 第i列的特征值
		featList = [example[i] for example in dataSet]
		# 去重
		uniqueVals = set(featList)

		# 求出对应特征的子数据集最小的香农熵
		newEntropy = 0.0
		# 计算每一个特征值的香农熵
		for value in uniqueVals :
			subDataSet = splitDataSet(dataSet , i , value)
			prob = len(subDataSet)/float(len(dataSet))
			newEntropy += prob * caclShannonEnt(subDataSet)

		infoGain = baseEntropy - newEntropy

		if (infoGain > bestInfoGain) :
			bestInfoGain = infoGain
			bestFeature = i

	return bestFeature

############### 划分数据集 end ######################

'''
@param classList 结果列表
'''
def majorityCnt(classList) :
	classCounts = {}
	for vote in classCounts :
		if vote not in classCounts.keys() : classCounts[vote] = 0
		classCounts[vote] += 1

	# 根据标签个数从大到小排序
	sortedLabelCount = sorted(classCounts.iteritems() , key = operator.itemgetter(1) , reverse=True)

	return sortedLabelCount[0][0]

'''
@param dataSet 
@param labels 特征标签
'''
def createTree(dataSet , labels) :
	# 获取到类别列表
	classList = [example[-1] for example in dataSet] 
	# 类别完全相同时停止继续划分
	# 如果类别列表中所有值都等于第一个类别，则停止划分
	if classList.count(classList[0]) == len(classList) :
		return classList[0]

	# 如果数据集只剩下标签，则找出出现次数最多的标签
	if len(dataSet[0]) == 1:
		return majorityCnt(classList)

	# 最优划分
	bestFeat = chooseBestFeatureToSplit(dataSet)
	# 最优标签
	bestFeatureLabel = labels[bestFeat]
	myTree = {bestFeatureLabel : {}}
	# 删除当前最优标签
	del(labels[bestFeat])
	# 标签对应的值，并去重
	featValues = [example[bestFeat] for example in dataSet]
	uniqueVals = set(featValues)

	for value in uniqueVals :
		# copy 标签
		subLabels = labels[:]
		myTree[bestFeatureLabel][value] = createTree(splitDataSet(dataSet , bestFeat , value) , subLabels)

	return myTree

'''
@param decisionTree 已经构建好的决策树
@param featLabels   特征标签
@param testVec 		待分类的特征
'''
def classify(decisionTree , featLabels , testVec) :
	firstStr = decisionTree.keys()[0]
	secondTree = decisionTree[firstStr]
	featIndex = featLabels.index(firstStr)
	for key in secondTree.keys() :
		if testVec[featIndex] == key :
			if type(secondTree[key]).__name__ == 'dict' :
				classLabel = classify(secondTree , featLabels , testVec)
			else :
				classLabel = secondTree[key]

	return classLabel

