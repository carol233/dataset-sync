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

family_dict = {}
family_count = 0
familyselect = []

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


def get_family_dict(labelcsv, family10csv):
    global family_count
    f1 = open(family10csv, "r")

    ll = f1.readline()
    while(ll):
        familyselect.append(ll.strip())
        ll = f1.readline()

    family_count = len(familyselect)
    print("family count is ", family_count)

    with open(labelcsv, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        birth_header = next(csv_reader)
        for row in csv_reader:
            sha256 = row[0]
            family = row[1]
            if not family in familyselect:
                continue
            family_num = familyselect.index(family)
            family_dict[sha256] = family_num

def jaccard_sim(a, b):
    unions = len(set(a).union(set(b)))
    intersections = len(set(a).intersection(set(b)))
    return format(float(intersections)/float(unions), '.4f')


def KmeansCluster(TrainMalSet, labelcsv, family10csv, FeatureOption):
    Logger.debug("Loading Malware and Goodware Sample Data for training and testing")
    TrainMalSamples = getApkList(TrainMalSet, ".data")

    Logger.info("Loaded Samples")

    FeatureVectorizer = TF(input="filename", tokenizer=lambda x: x.split('\n'), token_pattern=None,
                           binary=FeatureOption)
    X = FeatureVectorizer.fit_transform(TrainMalSamples)

    get_family_dict(labelcsv, family10csv)

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
    # print(y_train[:20])

    kmeans = KMeans(n_clusters=family_count, random_state=10).fit(X)
    labels = kmeans.labels_
    score = fowlkes_mallows_score(y_train, labels)

    #print(labels[:20])

    print(family_count, score)

    s_train = {}
    s_clus = {}
    for i in range(family_count):
        s_train[i] = []
        for j in range(len(y_train)):
            if str(y_train[j]) == str(i):
                # print("y_train_j and i", y_train[j], i)
                s_train[i].append(j)  # j is the num. of sample, should be long

    print(s_train)

    for i in range(family_count):
        s_clus[i] = []
        for j in range(len(labels)):
            if str(labels[j]) == str(i):
                # print("label_j and i", y_train[j], i)
                s_clus[i].append(j)

    print(s_clus)

    label_list = [0] * 10  # index is y_train, value is labels


    jac_dict = {}
    for i in range(family_count):
        max_jac = -1
        jac_dict[i] = [0] * family_count
        for j in range(family_count):
            jac_v = jaccard_sim(s_clus[i], s_train[j])
            jac_dict[i][j] = jac_v
            if jac_v > max_jac:
                max_jac = jac_v
                label_list[i] = j


    print("label_list is ", label_list)

    clus_other_fam = {}
    clus_not_in = {}

    for clus_num in range(family_count):
        clus_other_fam[clus_num] = []
        clus_not_in[clus_num] = []
        fam_num = label_list[clus_num]
        # find sample should in s_clus[clus_num] but in other
        for item in s_train[fam_num]:  # item is the index(num) of sample
            if item not in s_clus[clus_num]:
                clus_other_fam[clus_num].append(label_list[labels[item]])  # chuqu other family num

        for item in s_clus[clus_num]:
            if item not in s_train[fam_num]:
                clus_not_in[clus_num].append(y_train[item])  # not this family but jinlai


    print("jac matrix: ")
    print("classnum, jac_matrix, most_possi_fam, out_fam, out_fam_num, in_fam, in_fam_num, should in, "
          "actual in, rate1, rate2")
    for clus_num in range(family_count):
        fam_num = label_list[clus_num]
        family_name_str = familyselect[fam_num]

        fam_err_chuqu = [0] * family_count
        fam_err_jinlai = [0] * family_count

        for item in clus_other_fam[clus_num]:
            fam_err_chuqu[item] += 1

        for item in clus_not_in[clus_num]:
            fam_err_jinlai[item] += 1

        chuqu_err_max = max(fam_err_chuqu)
        # chuqu / bengai youde
        bili1 = format(float(chuqu_err_max) / float(len(s_train[fam_num])), '.4f')

        jinlai_err_max = max(fam_err_jinlai)
        # jinlai / shijifenguolai
        bili2 = format(float(jinlai_err_max) / float(len(s_clus[clus_num])), '.4f')


        chuqu_fam = fam_err_chuqu.index(chuqu_err_max)
        jilai_fam = fam_err_jinlai.index(jinlai_err_max)

        out_fam_name = familyselect[chuqu_fam]
        if chuqu_err_max == 0:
            out_fam_name = ""
        in_fam_name = familyselect[jilai_fam]
        if jinlai_err_max == 0:
            in_fam_name = ""

        print(clus_num, jac_dict[clus_num], family_name_str, out_fam_name, chuqu_err_max, in_fam_name
              , jinlai_err_max, len(s_train[fam_num]), len(s_clus[clus_num]), fam_err_chuqu, fam_err_jinlai)

