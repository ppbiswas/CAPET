#!/usr/bin/env python


import os
import sys
import numpy as np
import random
import math


# Local files
import correlation
import svm
import linearRegression
import config as cfg


Analysis_Options = ["1", "2", "3"]
Theft_Behaviors = ["0", "1", "2", "3", "4", "5"]
Frequencys = ["5", "15", "30", "45", "60"]
Noises = ["0", "0.1", "0.5", "1"]


# Return a 3d array with days as rows, apts as columns, and each
# unit is a list of usage for particular apt of a day
def load_energy_usage(log_folder, apt_num, day_num):
    if not os.path.isdir(log_folder):
        print "Log directory not found: ", log_folder
        sys.exit(0)

    usage = [[None for _ in xrange(apt_num)] for _ in xrange(day_num)]
    house_indx = 0
    for i in xrange(cfg.Apts):
        apt_log = os.path.join(log_folder, "Apt" + str(i+1))
        if not os.path.isfile(apt_log):
            continue
        with open(apt_log, 'r') as f:
            lines = f.readlines()
            for j in xrange(len(lines)):
                usage[j][house_indx] = [float(n) for n in lines[j].split(',')]
            house_indx += 1
    return np.asarray(usage)

# Return a list of theft IDs in universal form
def load_theft_ids(log_file):
    with open(log_file, 'r') as f:
        thefts = [int(v) for v in f.readline().split(',')]
    return thefts

# Return a list of theft stealing percentage
def load_constant_vars(log_file):
    # theft constant steal - random for diff sample
    with open(log_file, 'r') as f:
        constant_steal_vars = [float(i.strip()) for i in f.readlines()]
    return constant_steal_vars

# Return a 2D list with thefts as row, individual perc for each t as column
def load_random_vars(log_file, frequency):
    with open(log_file, 'r') as f:
        random_vars = []
        for line in f.readlines():
            values = [float(v) for v in line.strip().split(',')]
            # IMP: need to scale down to match time interval!!
            random_vars.append(values[::int(frequency/cfg.Default_Interval)])
    return random_vars

def load_max_min_random_values(log_file):
    with open(log_file, 'r') as f:
        load_values = []
        for line in f.readlines():
            load_values.append([float(v) for v in line.strip().split(',')])
    return load_values



# Convert universal IDs into daily IDs with corresponding vars index
def process_theft_id_coeff(thefts, apt_num, days):
    # day_theft is a list of 349 days, each day is a list of tokens
    # token = [theft apt, index]
    day_theft = [[] for _ in xrange(days)]

    for i in xrange(len(thefts)):
        day_theft[int(thefts[i] / apt_num)].append([thefts[i] % apt_num, i])

    return day_theft



def generate_theft_usage(usage, pattern, info_dir, apt_num, day_num, frequency):
    theft_usage = np.copy(usage)
    thefts = load_theft_ids(os.path.join(info_dir, cfg.Log_Theft_ID))
    daily_thefts_with_coeffs = process_theft_id_coeff(thefts, apt_num, day_num)
    if pattern == 0:
        return thefts, apply_mixed_patterns(usage=theft_usage,
                                            thefts=daily_thefts_with_coeffs,
                                            info_dir=info_dir,
                                            day_num=day_num,
                                            frequency=frequency)
    else:
        return thefts, apply_single_pattern(usage=theft_usage,
                                            pattern=pattern,
                                            thefts=daily_thefts_with_coeffs,
                                            info_dir=info_dir,
                                            day_num=day_num,
                                            frequency=frequency)

# Generate thefts with mixed patterns
def apply_mixed_patterns(usage, thefts, info_dir, day_num, frequency):
    daily_record_num = 24 * 60 / frequency
    # Load all vars
    constant_vars = load_constant_vars(os.path.join(info_dir, cfg.Log_Constant_Var))
    random_vars = load_random_vars(os.path.join(info_dir, cfg.Log_Random_Var), frequency)
    random_mean_vars = theft_vars = load_random_vars(os.path.join(info_dir, cfg.Log_Random_Mean_Var), frequency)
    #max_min_random_values = load_max_min_random_values(os.path.join(info_dir, cfg.Log_Max_Min_Random_Values))

    pattern_index = 0
    for day in xrange(day_num):
        # Reset here to ensure svm shares same theft info with the other two
        if day == (cfg.Days - cfg.Lr_Days):
            pattern_index = 0

        for theft in thefts[day]:
            theft_apt = theft[0]  # theft index in day
            coeff_id = theft[1]  # theft index in general

            if pattern_index == 0:
                for i in xrange(daily_record_num):
                    usage[day][theft_apt][i] *= constant_vars[coeff_id]
            elif pattern_index == 1:
                for i in xrange(daily_record_num):
                    usage[day][theft_apt][i] *= random_vars[coeff_id][i]
            elif pattern_index == 2:
                mean = np.mean(usage[day][theft_apt])
                for i in xrange(daily_record_num):
                    usage[day][theft_apt][i] = random_mean_vars[coeff_id][i] * mean
            elif pattern_index == 3:
                mean = np.mean(usage[day][theft_apt])
                for i in xrange(daily_record_num):
                    usage[day][theft_apt][i] = mean
## By PPB
            elif pattern_index == 4:
                timeshift = 4; # timeshift by _ hours
                timeshiftnumel = int(timeshift*60/frequency);
                for i in xrange(daily_record_num-timeshiftnumel-1):
                    temp = usage[day][theft_apt][i]
                    usage[day][theft_apt][i] = usage[day][theft_apt][i+timeshiftnumel]
                    usage[day][theft_apt][daily_record_num - timeshiftnumel] = temp
            elif pattern_index == 5:
                timeshift = random.randint(1,6); # timeshift randomly between 1 to 6 hours
                timeshiftnumel = int(timeshift*60/frequency);
                for i in xrange(daily_record_num-timeshiftnumel-1):
                    temp = usage[day][theft_apt][i]
                    usage[day][theft_apt][i] = usage[day][theft_apt][i+timeshiftnumel]
                    usage[day][theft_apt][daily_record_num - timeshiftnumel] = temp
##            elif pattern_index == 4:
##                for i in xrange(daily_record_num / 2):
##                    temp = usage[day][theft_apt][i]
##                    usage[day][theft_apt][i] = usage[day][theft_apt][(daily_record_num-1) - i]
##                    usage[day][theft_apt][(daily_record_num-1) - i] = temp
            #elif pattern_index == 5:
            #    for i in xrange(daily_record_num):
            #        usage[day][theft_apt][i] = max_min_random_values[coeff_id][i]
            else:
                print "Wrong pattern index"

            pattern_index += 1
            if pattern_index == 5:
                pattern_index = 0

    return usage

# Generate thefts with single pattern
def apply_single_pattern(usage, pattern, thefts, info_dir, day_num, frequency):
    daily_record_num = 24 * 60 / frequency
    # Load variables for different types of thefts
    if pattern == 1:
        theft_vars = load_constant_vars(os.path.join(info_dir, cfg.Log_Constant_Var))
    elif pattern == 2:
        theft_vars = load_random_vars(os.path.join(info_dir, cfg.Log_Random_Var), frequency)
    elif pattern == 3:
        theft_vars = load_random_vars(os.path.join(info_dir, cfg.Log_Random_Mean_Var), frequency)
    elif pattern == 4 or pattern == 5:
        theft_vars = []
    # elif pattern == 6:
    #    theft_vars = load_max_min_random_values(os.path.join(info_dir, cfg.Log_Max_Min_Random_Values))
    else:
        print "Invalid theft pattern ", pattern
        sys.exit(0)

    for day in xrange(day_num):
        for theft in thefts[day]:
            theft_apt = theft[0]  # theft index in day
            coeff_id = theft[1]  # theft index in general

            if pattern == 1:
                for i in xrange(daily_record_num):
                    usage[day][theft_apt][i] *= theft_vars[coeff_id]
            elif pattern == 2:
                for i in xrange(daily_record_num):
                    usage[day][theft_apt][i] *= theft_vars[coeff_id][i]
            elif pattern == 3:
                mean = np.mean(usage[day][theft_apt])
                for i in xrange(daily_record_num):
                    usage[day][theft_apt][i] = theft_vars[coeff_id][i] * mean
            elif pattern == 4:
                mean = np.mean(usage[day][theft_apt])
                for i in xrange(daily_record_num):
                    usage[day][theft_apt][i] = mean
##            elif pattern == 5:
##                for i in xrange(daily_record_num / 2):
##                    temp = usage[day][theft_apt][i]
##                    usage[day][theft_apt][i] = usage[day][theft_apt][(daily_record_num-1) - i]
##                    usage[day][theft_apt][(daily_record_num-1) - i] = temp
##  By PPB
            elif pattern == 5:
                timeshift = 4; # timeshift by _ hours
                timeshiftnumel = int(timeshift*60/frequency);
                for i in xrange(daily_record_num-timeshiftnumel-1):
                    temp = usage[day][theft_apt][i]
                    usage[day][theft_apt][i] = usage[day][theft_apt][i+timeshiftnumel]
                    usage[day][theft_apt][daily_record_num - timeshiftnumel] = temp
            elif pattern == 6:
                timeshift = random.randint(1,6); # timeshift randomly between 1 to 6 hours
                timeshiftnumel = int(timeshift*60/frequency);
                for i in xrange(daily_record_num-timeshiftnumel-1):
                    temp = usage[day][theft_apt][i]
                    usage[day][theft_apt][i] = usage[day][theft_apt][i+timeshiftnumel]
                    usage[day][theft_apt][daily_record_num - timeshiftnumel] = temp
            #elif pattern == 6:
            #    for i in xrange(daily_record_num):
            #        usage[day][theft_apt][i] = theft_vars[coeff_id][i]

    return usage
    
def execute_correlation(theft_behavior, frequency, noise):

    print "\nNumber of sub-group to split (Avail: 1, 2, 3, 4)"
    print " - 1: apts [1, 114]"
    print " - 2: apts [1, 57], [58, 114]"
    print " - 3: apts [1, 38], [39, 76], [77, 114]"
    print " - 4: apts [1, 29], [29, 57], [58, 86], [87, 114]"
    print "Input: "
    split_num = int(raw_input())
    if split_num not in [1,2,3,4]:
        print "Invalid number of split. Quit"
        sys.exit(0)

    apt_num_set = cfg.Apt_Num_Sets[split_num-1]
    division_set = cfg.Divide_Sets[split_num-1]

    dis_coeffs_matrix = [[] for _ in xrange(cfg.Corr_Days)]
    mas_coeffs_matrix = [[] for _ in xrange(cfg.Corr_Days)]
    
    for div_id, division in enumerate(division_set):
        print "\nRuning for ", div_id, " - ", division

        if noise == 0:
            data_dir = cfg.Corr_Origin_Data_Dir.format(frequency, division)
        else:
            data_dir = cfg.Corr_Noise_Data_Dir.format(frequency, division, noise)
        theft_info_dir = cfg.Corr_Theft_Info_Dir.format(frequency, division)

        usage = load_energy_usage(log_folder=data_dir,
                              apt_num=apt_num_set[div_id],
                              day_num=cfg.Corr_Days)

        thefts, theft_usage = generate_theft_usage(usage=usage,
                                               pattern=theft_behavior,
                                               info_dir=theft_info_dir,
                                               apt_num=apt_num_set[div_id],
                                               day_num=cfg.Corr_Days,
                                               frequency=frequency)

        dis_coeffs, mas_coeffs = correlation.run_correlation(thefts=thefts,
                                                 usage=usage,
                                                 theft_usage=theft_usage,
                                                 apt_num=apt_num_set[div_id],
                                                 day_num=cfg.Corr_Days,
                                                 noise=noise, 
                                                 analysis_method=2)

        for j,v in enumerate(dis_coeffs):
            dis_coeffs_matrix[j/apt_num_set[div_id]].append(v)
        for j,v in enumerate(mas_coeffs):
            mas_coeffs_matrix[j/apt_num_set[div_id]].append(v)

    np.savetxt("discoeff.csv", dis_coeffs_matrix, delimiter=",")
    total_dis_coeffs = []
    total_mas_coeffs = []
    for row in dis_coeffs_matrix:
        total_dis_coeffs.extend(row)
    for row in mas_coeffs_matrix:
        total_mas_coeffs.extend(row)
    np.savetxt("totdiscoeff.csv", total_dis_coeffs, delimiter=",")
    np.savetxt("totmascoeff.csv", total_mas_coeffs, delimiter=",")
    
    # Get thefts id
    with open(cfg.Corr_Theft_Id_Total.format(frequency), 'r') as f:
        total_theft = [int(v) for v in f.readline().split(',')]

    correlation.analysis_correlation(thefts=total_theft,
                         dis_coeffs=total_dis_coeffs,
                         mas_coeffs=total_mas_coeffs,
                         apt_num=cfg.Apts,
                         day_num=cfg.Corr_Days,
                         analysis_method=2)


def execute_svm(theft_behavior, frequency, noise):
    print "Execute svm"

    if noise == 0:
        data_folder = cfg.Svm_Origin_Data_Dir.format(frequency)
    else:
        data_folder = cfg.Svm_Noise_Data_Dir.format(frequency, noise)
    theft_info_folder = cfg.Svm_Theft_Info_Dir.format(frequency)

    usage = load_energy_usage(log_folder=data_folder, apt_num=cfg.Apts, day_num=cfg.Days)

    thefts, theft_usage = generate_theft_usage(usage=usage, pattern=theft_behavior, info_dir=theft_info_folder,
                                               apt_num=cfg.Apts, day_num=cfg.Days, frequency=frequency)

    svm.run_svm(theft_usage=theft_usage, theft_vectors=thefts)


def execute_linearRegression(theft_behavior, frequency, noise):
    print "Execute linear regression"

    if noise == 0:
        data_folder = cfg.Lr_Origin_Data_Dir.format(frequency)
    else:
        data_folder = cfg.Lr_Noise_Data_Dir.format(frequency, noise)
    theft_info_folder = cfg.Lr_Theft_Info_Dir.format(frequency)

    usage = load_energy_usage(log_folder=data_folder, apt_num=cfg.Apts, day_num=cfg.Lr_Days)

    thefts, theft_usage = generate_theft_usage(usage=usage, pattern=theft_behavior, info_dir=theft_info_folder,
                                               apt_num=cfg.Apts, day_num=cfg.Lr_Days, frequency=frequency)

    linearRegression.run_linear_regression(usage=usage, thefts=thefts, theft_usage=theft_usage,
                                           day_num=cfg.Lr_Days, apt_num=cfg.Apts, noise=noise)


def get_analysis_option():
    print "(Values can be changed in config.py file)"
    print "\nAnalysis Options"
    print "1. Correlation Analysis"
    print "2. Svm"
    print "3. Linear Regression"
    print "Input:  "
    analysis_option = raw_input()
    if analysis_option not in Analysis_Options:
        print "Invalid option. Quit"
        sys.exit(0)

    return int(analysis_option)

def get_theft_behavior():
    print "\nTheft Behaviors:"
    print "1. Constant steal. (Theft_usage = Real_usage * steal_percent)"
    print "2. Random steal at t. (Theft_usage = Real_usage * steal_percent_t, steal_percent_t varies at time t)"
    print "3. Mean with random coefficient. (Theft_usage = Mean * steal_percent_t)"
    print "4. Mean value. (Theft_usage = Mean)"
    print "5. Reverse values. (Theft_usage at t = Real_usage at 24-t)"
    #print "6. "
    print "0. Mixture of all"
    print "Input:  "
    theft_behavior = raw_input()
    if theft_behavior not in Theft_Behaviors:
        print "Invalid theft. Quit"
        sys.exit(0)

    return int(theft_behavior)

def get_frequency():
    print "\nFrequency input (Avail: 5, 15, 30, 45, 60) in mins: "
    frequency = raw_input()
    if frequency not in Frequencys:
        print "Please choose one from avail frequency"
        sys.exit(0)

    return int(frequency)

def get_noise():
    print "\nNoise: "
    print " - Avail: 0, 0.1, 0.5, 1"
    print " - 0.1 means noise is within 0.1% of usage."
    print " - noise is avail for 5 mins currently."
    print "Input: "
    noise = raw_input()
    if noise not in Noises:
        print "Please choose one from avail frequency"
        sys.exit(0)

    return float(noise)

def main():
    
    analysis_option = get_analysis_option()
    theft_behavior = get_theft_behavior()
    frequency = get_frequency()
    noise = get_noise()

    print ""
    
    if analysis_option == cfg.Method_Correlation:
        execute_correlation(theft_behavior=theft_behavior, frequency=frequency, noise=noise)

    elif analysis_option == cfg.Method_SVM:
        execute_svm(theft_behavior=theft_behavior, frequency=frequency, noise=noise)

    elif analysis_option == cfg.Method_Linear_Regression:
        if frequency == 5:
            execute_linearRegression(theft_behavior=theft_behavior, frequency=frequency, noise=noise)
        else:
            print "For linear regression, only 5min is allowed for frequency."


if __name__ == '__main__':
    main()
