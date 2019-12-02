import numpy as np
import time
import scipy.sparse
import CommonModules as CM
from sklearn.model_selection import cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer as TF
from sklearn.svm import LinearSVC
from sklearn.model_selection import GridSearchCV
from sklearn import metrics
from sklearn.metrics import accuracy_score, roc_curve, auc
import logging
import json, os
import matplotlib.pyplot as plt
#from pprint import pprint

logging.basicConfig(level=logging.INFO)
Logger = logging.getLogger('HoldoutClf.stdout')
Logger.setLevel("INFO")


def SVMClassification(TrainMalSet, TrainGoodSet, TestMalSet, TestGoodSet, FeatureOption, Model, NumTopFeats):
    '''
    Train a classifier for classifying malwares and goodwares using Support Vector Machine technique.
    Compute the prediction accuracy and f1 score of the classifier.
    Modified from Jiachun's code.

    :param String/List TrainMalSet: absolute path/paths of the malware corpus for trainning set
    :param String/List TrainGoodSet: absolute path/paths of the goodware corpus for trainning set
    :param String/List TestMalSet: absolute path/paths of the malware corpus for test set
    :param String/List TestGoodSet: absolute path/paths of the goodware corpus for test set
    :param String FeatureOption: tfidf or binary, specify how to construct the feature vector
    '''
    # step 1: creating feature vector
    Logger.debug("Loading Malware and Goodware Sample Data for training and testing")
    TrainMalSamples = CM.ListFiles(TrainMalSet, ".data")
    TrainGoodSamples = CM.ListFiles(TrainGoodSet, ".data")
    TestMalSamples = CM.ListFiles(TestMalSet, ".data")
    TestGoodSamples = CM.ListFiles(TestGoodSet, ".data")
    AllTestSamples = TestMalSamples + TestGoodSamples
    Logger.info("Loaded Samples")

    FeatureVectorizer = TF(input="filename", tokenizer=lambda x: x.split('\n'), token_pattern=None,
                           binary=FeatureOption)
    x_train = FeatureVectorizer.fit_transform(TrainMalSamples + TrainGoodSamples)
    x_test = FeatureVectorizer.transform(TestMalSamples + TestGoodSamples)

    # label training sets malware as 1 and goodware as -1
    Train_Mal_labels = np.ones(len(TrainMalSamples))
    Train_Good_labels = np.empty(len(TrainGoodSamples))
    Train_Good_labels.fill(-1)
    y_train = np.concatenate((Train_Mal_labels, Train_Good_labels), axis=0)
    Logger.info("Training Label array - generated")

    # label testing sets malware as 1 and goodware as -1
    Test_Mal_labels = np.ones(len(TestMalSamples))
    Test_Good_labels = np.empty(len(TestGoodSamples))
    Test_Good_labels.fill(-1)
    y_test = np.concatenate((Test_Mal_labels, Test_Good_labels), axis=0)
    Logger.info("Testing Label array - generated")

    # step 2: train the model
    Logger.info("Perform Classification with SVM Model")
    Parameters= {'C': [0.001, 0.01, 0.1, 1, 10, 100, 1000]}

    Clf = GridSearchCV(LinearSVC(), Parameters, cv=10, scoring= 'f1', n_jobs=-1 )
    SVMModels= Clf.fit(x_train, y_train)
    y_score = SVMModels.decision_function(x_test)

    fpr, tpr, thresholds = roc_curve(y_test, y_score)
    roc_auc = auc(fpr, tpr)

    print(fpr)
    print(tpr)
    print(roc_auc)

    plt.figure()
    lw = 2
    plt.figure(figsize=(10, 10))
    plt.plot(fpr, tpr, color='darkorange',
             lw=lw, label='ROC curve (area = %0.2f)' % roc_auc)  ###假正率为横坐标，真正率为纵坐标做曲线
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.show()

