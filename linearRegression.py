#!/usr/bin/env python


import os
import sys
import random
import numpy as np
import ml_metrics as metrics
from scipy.stats import t
from sklearn import linear_model

# Local files
import config as cfg


def add_noise(data, noise):
    return np.asarray([d*(1.0+random.uniform(-noise, noise)/100.0) for d in data])


def convert_theft_to_daily(vectors, apt_num, day_num):
    day_theft = [[] for _ in xrange(day_num)]

    for i in xrange(len(vectors)):
        day_theft[int(vectors[i] / apt_num)].append(vectors[i]%apt_num)

    return day_theft


def compute_precision_recall(thievesid, theft_consump, ori_consump, noise=0):
    #use sum of individual original readings as the master meter reading
    #shape: number of timestamps * 0
    readings_master_meter = ori_consump.sum(axis=0)
    if noise != 0:
        readings_master_meter = add_noise(readings_master_meter, noise)

    #sum of reported consumption, shape: number of timestamps * 0
    readings_sum_submeter = theft_consump.sum(axis=0)
    #difference between master_meter and sum_of_sub_meter at every timestamp
    readings_discrepancy = readings_master_meter - readings_sum_submeter

    if readings_discrepancy.sum() == 0:
        return 0, 0, [1 for _ in xrange(len(ori_consump))], [0 for _ in xrange(len(ori_consump))]

    # solve the linear regression model
    # option 1, using sklearn
    regr = linear_model.LinearRegression()
    regr.fit(theft_consump.T, readings_discrepancy)
    # shape: number of houses * 0
    theft_coefficients = regr.coef_
    sorted_houses = np.argsort(regr.coef_)

    #to get the t test p value
    params = np.append(regr.intercept_,regr.coef_)
    predictions = regr.predict(theft_consump.T)
    newX = np.append(np.ones((len(theft_consump.T),1)), theft_consump.T, axis=1)
    MSE = (sum((readings_discrepancy-predictions)**2))/(len(newX)-len(newX[0]))
    var_b = MSE*(np.linalg.inv(np.dot(newX.T,newX)).diagonal())
    sd_b = np.sqrt(var_b)
    ts_b = params/ sd_b

    p_values =[2*(1-t.cdf(np.abs(i),(len(newX)-1))) for i in ts_b]
    sd_b = np.round(sd_b,3)
    ts_b = np.round(ts_b,3)
    p_values = np.round(p_values,3)
    params = np.round(params,4)

    #sort the houses by their coeffient and remove those with p value >=0.01
    indexes = [i for i,v in enumerate(p_values) if v<1]
    pred_thievesid = [i for i,v in enumerate(theft_coefficients) if v>0.1]
    refined_sorted_houses = [x for x in sorted_houses if x in set(indexes)]
    refined_sorted_houses = [x for x in refined_sorted_houses if x in set(pred_thievesid)]

    caught_thefts = set(refined_sorted_houses).intersection(thievesid)

    return len(refined_sorted_houses), len(caught_thefts), p_values.tolist(), theft_coefficients.tolist()


def run_linear_regression(usage, thefts, theft_usage, day_num, apt_num, noise):
    daily_thefts = convert_theft_to_daily(thefts, apt_num, day_num)

    caught_total = 0
    caught_thefts_total = 0
    total_pvalues = []
    total_coeffs = []

    for day in xrange(day_num):
        caught, caught_theft, daily_pvalue, daily_coef = compute_precision_recall(daily_thefts[day],
                                                                                  theft_usage[day],
                                                                                  usage[day],
                                                                                  noise=noise)
        caught_total += caught
        caught_thefts_total += caught_theft
        total_pvalues.extend(daily_pvalue)
        total_coeffs.extend(daily_coef)

    print "Summary"
    print "Theft {}. Caught {}. Correct {}".format(len(thefts), caught_total, caught_thefts_total)

    print "map@k"
    indexes = [i for i,v in enumerate(total_pvalues) if v<1]
    pred_thievesid = [i for i,v in enumerate(total_coeffs) if v>0.1]
    sorted_houses = np.argsort(total_coeffs)
    refined_sorted_houses = [x for x in sorted_houses if x in set(indexes)]
    refined_sorted_houses = [x for x in refined_sorted_houses if x in set(pred_thievesid)]

    for i in range(1, 11):
        mapk = metrics.mapk(convert_theft_to_daily(thefts, cfg.Apts, cfg.Lr_Days),
                            convert_theft_to_daily(refined_sorted_houses, cfg.Apts, cfg.Lr_Days),
                            i)
        print "{}: {}".format(i, mapk)


