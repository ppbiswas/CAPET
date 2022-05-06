#!/usr/bin/env python

"""
    Analyse correlations between theft and the master reading.
"""

import os
import sys
import math
import random
import numpy as np
import ml_metrics as metrics
from scipy import stats

# Local files
import config as cfg


def add_noise(data, noise):
    return np.asarray([d*(1.0+random.uniform(-noise, noise)/100.0) for d in data])


def convert_theft_to_daily(vectors, apt_num, day_num):
    day_theft = [[] for _ in xrange(day_num)]

    for i in xrange(len(vectors)):
        day_theft[int(vectors[i] / apt_num)].append(vectors[i]%apt_num)

    return day_theft



def compute_pearsonr(orig_usage, theft_usage, apt_num, noise):
    # Get master meter usage
    readings_master_meter = orig_usage.sum(axis=0)
    if noise != 0:
        readings_master_meter = add_noise(readings_master_meter, noise)

    readings_sum_submeter = theft_usage.sum(axis=0)
    readings_discrepancy = readings_master_meter - readings_sum_submeter

    discrepancy_coeff = np.zeros((apt_num,2))    #[number of house * 2, coefficient, p value]
    for house in range(apt_num):
        discrepancy_coeff[house] = stats.pearsonr(theft_usage[house], readings_discrepancy)
    discrepancy_coeff = np.asarray([abs(row[0]) for row in discrepancy_coeff])
    np.savetxt("theft_usage.csv", theft_usage, delimiter=",")
    np.savetxt("readings_discrepancy.csv", readings_discrepancy, delimiter=",")
    np.savetxt("discrepancy_coeff.csv", discrepancy_coeff, delimiter=",")

    master_coeff = np.zeros((apt_num,2))
    for house in range(apt_num):
        master_coeff[house] = stats.pearsonr(theft_usage[house], readings_master_meter)
    master_coeff = np.asarray([abs(row[0]) for row in master_coeff])

    return discrepancy_coeff, master_coeff



def run_correlation(thefts, usage, theft_usage, apt_num, day_num, noise, analysis_method):
    daily_thefts=convert_theft_to_daily(vectors=thefts, apt_num=apt_num, day_num=day_num)

    dis_coeffs = []
    mas_coeffs = []
    for day in xrange(day_num):
        if not daily_thefts[day]:
            print "NO theft today: day ", day
            dis_coeffs.extend([-1 for _ in xrange(apt_num)])
            mas_coeffs.extend([-1 for _ in xrange(apt_num)])
            continue
        dis_coeff, mas_coeff = compute_pearsonr(orig_usage=usage[day], theft_usage=theft_usage[day],
                                                apt_num=apt_num, noise=noise)
        dis_coeffs.extend(dis_coeff)
        mas_coeffs.extend(mas_coeff)

    '''analysis_correlation(thefts=thefts,
                         dis_coeffs=dis_coeffs,
                         mas_coeffs=mas_coeffs,
                         apt_num=apt_num,
                         day_num=day_num,
                         analysis_method=analysis_method)'''

    return dis_coeffs, mas_coeffs


def analysis_correlation(thefts, dis_coeffs, mas_coeffs, apt_num, day_num, analysis_method):
    theft_num = len(thefts)

    # Ways to identify thefts:
    # 1. nan
    # 2. extreme small values () < 10^-10)
    # 3. coef_dis / coef_master, coef_dis
    nan_ids = []
    extreme_ids = []
    remaining_coeffs = []
    for i in xrange(len(dis_coeffs)):
        # Nan case
        if math.isnan(dis_coeffs[i]) or math.isnan(mas_coeffs[i]):
            nan_ids.append(i)
            remaining_coeffs.append(-1.0)  # for dis_coeff
            #remaining_coeffs.append(5.0)  # for mas_coeff
        # Extreme small case
        elif (dis_coeffs[i] >= 0) and (dis_coeffs[i] < 10E-10):
            extreme_ids.append(i)
            remaining_coeffs.append(-1.0)  # for dis_coeff
            #remaining_coeffs.append(5.0)  # for mas_coeff
        else:
            if mas_coeffs[i] == 0:
                remaining_coeffs.append(0)
            else:
                remaining_coeffs.append(dis_coeffs[i])

    print "\nSummary"
    print "nan: ", len(nan_ids)
    print "nan correct: ", len(set(nan_ids).intersection(thefts))
    print "extreme: ", len(extreme_ids)
    print "extreme correct: ", len(set(extreme_ids).intersection(thefts))

    remaining_num = theft_num - len(nan_ids) - len(extreme_ids)
    remaining_coeffs = np.asarray(remaining_coeffs)
    sorted_ids = remaining_coeffs.argsort()[::-1]  # descending order for discrepancy
    #sorted_ids = remaining_coeffs.argsort() # ascending order for master meter


    remaining_results = []
    analysis_method = 2 # 0 for CAPET-gamma, 2 for CAPET
    print " -- analysis method: ", analysis_method

    # Example of using mas_correlation as criteria
    if analysis_method == 0:
        for apt in sorted_ids:
            if remaining_num <= 0 or len(remaining_results) == remaining_num:
                break

            #if dis_coeffs[apt] / mas_coeffs[apt] > 1:
            if dis_coeffs[apt] / mas_coeffs[apt] > 1 or 1==1:
                remaining_results.append(apt)


    # Second method for remaining:
    # 1. if top 3, add one more condition
    # 2. if not, still the same condition
    # Second method contains 2 ways: select from each day, or from total amount
    elif analysis_method == 2:
        top3_everyday = []
        for day in xrange(day_num):
            cur_day_dis = np.asarray(dis_coeffs[day * apt_num: (day + 1) * apt_num])
            for i in xrange(len(cur_day_dis)):
                if math.isnan(cur_day_dis[i]) or (cur_day_dis[i] >= 0 and cur_day_dis[i] < 10E-10):
                    cur_day_dis[i] = -1
            sorted_day_ids = cur_day_dis.argsort()[::-1]  # descending order for discrepancy
            top3_everyday.extend([day * apt_num + i for i in sorted_day_ids[:3]])
        print "theft in top3 (210 apts): ", len(set(top3_everyday).intersection(thefts))

        for apt in top3_everyday:
            if remaining_num <= 0 or len(remaining_results) == remaining_num:
                break
            if (dis_coeffs[apt] / mas_coeffs[apt] > 1) or (mas_coeffs[apt] < 0.3): 
                remaining_results.append(apt)

        print "after filter top3"
        print "remaining chose: ", len(remaining_results)
        print "remaining correct: ", len(set(remaining_results).intersection(thefts))

        for apt in sorted_ids:
            if remaining_num <= 0 or len(remaining_results) == remaining_num:
                break
            if apt not in top3_everyday:
                if dis_coeffs[apt] / mas_coeffs[apt] > 1:
                #if dis_coeffs[apt] / mas_coeffs[apt] > 1 or 1==1:
                    remaining_results.append(apt)

    print "remaining chose: ", len(remaining_results)
    print "remaining correct: ", len(set(remaining_results).intersection(thefts))


    # Combine results
    candidates = np.concatenate((extreme_ids, nan_ids), axis=0)
    candidates = np.concatenate((candidates, remaining_results), axis=0)
    caught = set(candidates).intersection(thefts)
    print "\nselected ", len(candidates)
    print "Catch : ", len(caught)
    print "Total theft : ", len(thefts)
    print "P: ", float(len(caught)) / len(thefts)

    # map@k
    selected_day_theft = convert_theft_to_daily(candidates, apt_num, day_num)
    total_day_theft = convert_theft_to_daily(thefts, apt_num, day_num)
    #print "selected: ", selected_day_theft
    #print "total: ", total_day_theft
    for i in range(1, 11):
        mapk = metrics.mapk(total_day_theft, selected_day_theft, i)
        print "{}: {}".format(i, mapk)

    return

