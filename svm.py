#!/usr/bin/env python


import os
import sys
import numpy as np
import ml_metrics as metrics
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler

# Local files
import config as cfg


def convert_theft_to_daily(vectors, apt_num, day_num):
    day_theft = [[] for _ in xrange(day_num)]

    for i in xrange(len(vectors)):
        day_theft[int(vectors[i] / apt_num)].append(vectors[i]%apt_num)

    return day_theft


def run_svm(theft_usage, theft_vectors):
    scaler = StandardScaler()

    training = []
    training_label = []
    for day in xrange(cfg.Svm_Train_Days):
        for apt in xrange(len(theft_usage[day])):
            training.append(theft_usage[day][apt])
            index = day * cfg.Apts + apt
            if index in theft_vectors:
                training_label.append(1)
            else:
                training_label.append(0)
    training = np.asarray(training)
    training = scaler.fit_transform(training)
    training_label = np.asarray(training_label)
    testing = []
    for i in xrange(cfg.Svm_Train_Days, cfg.Days):
        for apt in theft_usage[i]:
            testing.append(apt)
    testing = np.asarray(testing)
    testing = scaler.fit_transform(testing)

    clf = SVC(class_weight={1:5}, random_state=0, probability=True)
    clf.fit(training, training_label)
    print "done fit"

    # For probabilities
    pred_probability = clf.predict_proba(testing)[:, 1]
    sorted_probas = pred_probability.argsort()[::-1] # descending order

    # For theft ids
    pred_results = clf.predict(testing)
    print "done predict"

    pre_number = cfg.Svm_Train_Days * cfg.Apts
    pred_theft = [(i+pre_number) for i in range(testing.shape[0]) if pred_results[i]==1]
    total_theft = [i for i in theft_vectors if i>=pre_number]
    print "total theft, ", len(total_theft)
    print "detect, ", len(pred_theft)
    print "detect theft, ", len(set(pred_theft).intersection(total_theft))

    # compute map@k
    pred_day_theft = convert_theft_to_daily([(i+pre_number) for i in sorted_probas if pred_results[i]==1], cfg.Apts, cfg.Days)
    total_day_theft = convert_theft_to_daily(total_theft, cfg.Apts, cfg.Days)

    # only take the last 70 days(those with theft), as empty list [] (1-349 day) will affect average value.
    for i in range(1, 11):
        mapk = metrics.mapk(total_day_theft[-70:], pred_day_theft[-70:], i)
        print "{}: {}".format(i, mapk)

