# coding:utf-8

import csv
import numpy as np
import time
import scipy.sparse
from sklearn.model_selection import cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer as TF
from sklearn.cluster import KMeans
from sklearn.model_selection import GridSearchCV
from sklearn import metrics
from sklearn.metrics import accuracy_score, fowlkes_mallows_score
import logging
import json, os

# from pprint import pprint
families = {}
family_dict = {}
family_count = 0

logging.basicConfig(level=logging.INFO)
Logger = logging.getLogger('HoldoutClf.stdout')
Logger.setLevel("INFO")


def getApkList(rootDir, pick_str):
    """
    :param rootDir:  root directory of dataset
    :return: A filepath list of sample
    """
    filePath = []
    for parent, dirnames, filenames in os.walk(rootDir):
        for filename in filenames:
            if pick_str in filename:  # exists .data
                file = os.path.join(parent, filename)
                filePath.append(file)
    return filePath


def evaluate_cluster_performance(X, labels):
    sc = metrics.silhouette_score(X, labels, metric='euclidean')
    chs = metrics.calinski_harabaz_score(X, labels)
    print("silhouette_score:", sc)
    print("calinski_harabaz_score:", chs)
    return [sc, chs]


def get_family_dict(labelcsv):
    global family_count
    with open(labelcsv, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        birth_header = next(csv_reader)
        for row in csv_reader:
            sha256 = row[0]
            family = row[1]
            if family in families:
                family_num = families[family]
            else:
                families[family] = family_count
                family_num = family_count
                family_count += 1
            family_dict[sha256] = family_num


def KmeansCluster(TrainMalSet, labelcsv, FeatureOption):
    Logger.debug("Loading Malware and Goodware Sample Data for training and testing")
    TrainMalSamples = getApkList(TrainMalSet, ".data")

    Logger.info("Loaded Samples")

    FeatureVectorizer = TF(input="filename", tokenizer=lambda x: x.split('\n'), token_pattern=None,
                           binary=FeatureOption)
    X = FeatureVectorizer.fit_transform(TrainMalSamples)

    get_family_dict(labelcsv)

    y_train = []
    for file in TrainMalSamples:
        if "amd" in labelcsv:
            sha256 = os.path.split(file)[-1][:-5].split('_')[-1]
        else:
            sha256 = os.path.split(file)[-1][:-5]
        if sha256 in family_dict:
            y_train.append(family_dict[sha256])
        else:
            y_train.append(-1)

    # test
    print(y_train[:20])

    kmeans = KMeans(n_clusters=family_count, random_state=10).fit(X)
    labels = kmeans.labels_
    score = fowlkes_mallows_score(y_train, labels)

    print(labels[:20])

    print(family_count, score)





