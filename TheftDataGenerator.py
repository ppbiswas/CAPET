#!/usr/bin/env python

"""
    Generate the data needed for Correlation Experiments
    Refer read me for more details

"""


import os
import sys
import shutil
import random
import math
import numpy as np
from scipy import stats


Total_Num = 502560  # 349 days * 24 hours * 60 mins
Frequency = 5       # mins; the smallest is 1 min
Row_Size = 24 * 60 / Frequency  # 24 hours * 4 (15mins frequency)

Days = 349
Total_House = 114
Theft_Percent = 0.1
Daily_Theft_Num = int(Total_House * Theft_Percent)

Min_perc = 0.1
Max_perc = 0.8
Min_Off_Time = 4 # for theft method 2

# Defined data paths. Edit if needed
Ori_Data_Dir = '../data/original_data'
Corr_Data_Dir = '../data/theft_experiment_{}min'.format(Frequency)
Noise_Source_Dir = '../data/theft_experiment_5min/N4_D-70/86-114/data'



def copy_process_original_data(source_dir, target_dir, total_data_num):
    print "\nCopying data to ", target_dir
    if not os.path.isdir(source_dir):
        print "The original data not found. Please check: \n", source_dir
        sys.exit(0)
    target_folder = os.path.join(target_dir, "data")
    if not os.path.isdir(target_folder):
        os.makedirs(target_folder)
        print "Created folder for correlation data at: \n", target_folder

    apt_number = 1
    for file_name in os.listdir(source_dir):
        #if "Apt" not in file_name:
        #    continue
        print "Copying ", file_name

        content = []
        origin_file = os.path.join(source_dir, file_name)

        # dataset 1: smart
        with open(origin_file, 'r') as f:
            for index in xrange(total_data_num): # till 2016-12-14
                content.append(next(f).strip())
        content = content[::Frequency]

        new_file = os.path.join(target_folder, 'Apt' + str(apt_number))
        with open(new_file, 'w') as f:
            for i in xrange(0, len(content), Row_Size):
                f.write(','.join(content[i: i + Row_Size]) + '\n')
        apt_number += 1


def copy_process_noise_data(noise):

# change the path here
    split_numdays = -70
    source_dir = 'Run 2/theft_experiment_5min/data_withNoise_{}'.format(noise) # for copying noise
    target_folder = "Run 2/theft_experiment_5min/N1_D-70/0-114/data_withNoise_" + str(noise)

    if not os.path.isdir(source_dir):
        print "The original data not found. Please check: \n", source_dir
        sys.exit(0)
    if not os.path.isdir(target_folder):
        os.makedirs(target_folder)
        print "Created folder for noise data at: \n", target_folder
               
    apt_number = 1
    for file_name in os.listdir(source_dir):
        print "Copying ", file_name

        origin_file = os.path.join(source_dir, file_name)
        with open(origin_file, 'r') as f:
            orig_content = f.readlines()

        new_file = os.path.join(target_folder, 'Apt' + str(apt_number))
        with open(new_file, 'w') as f:
            content = orig_content[split_numdays:]
            content = f.writelines(content)
        apt_number += 1

def generate_theft(frequency, total_house, daily_theft_num):

    theft_folder = os.path.join(Corr_Data_Dir, "theft_experiment_{}min".format(frequency))
    if not os.path.isdir(theft_folder):
        os.makedirs(theft_folder)
        print "Created folder for correlation data at: \n", theft_folder
    '''for i in xrange(1, 10):
        temp = theft_folder + str(i)
        if not os.path.isdir(temp):
            theft_folder = temp
            os.makedirs(theft_folder)
            break'''

    # ----------------
    # For theft ids
    # ----------------
    print "Generating theft ids"
    thefts = []
    for day in xrange(Days):
        daily_thefts = random.sample(xrange(0, total_house), daily_theft_num)
        thefts.extend([ t+day*total_house for t in daily_thefts])
    log_file = os.path.join(theft_folder, "theft-vectors")
    with open(log_file, 'w') as f:
        f.write(','.join([str(t) for t in thefts]))


    print "Generating theft method data"
    theft_number = daily_theft_num * Days
    # ----------------
    # First theft method
    # ----------------
    log_file = os.path.join(theft_folder, "theft-constant-steal")
    with open(log_file, 'w') as f:
        f.write('\n'.join([str(random.uniform(Min_perc, Max_perc)) for _ in xrange(theft_number)]))

    # ----------------
    # Second theft method
    # ----------------
    log_file = os.path.join(theft_folder, "theft-period-steal")
    with open(log_file, 'w') as f:
        start_time = random.randint(0, 23 - Min_Off_Time)
        end_time = start_time + random.randint(Min_Off_Time, 24)
        f.write("{}\n{}".format(start_time, end_time))

    # ----------------
    # Third theft method
    # ----------------
    log_file = os.path.join(theft_folder, "theft-constant-steal-random-diff-sample")
    with open(log_file, 'w') as f:
        for i in xrange(theft_number):
            f.write(','.join([str(random.uniform(Min_perc, Max_perc)) for _ in xrange(Row_Size)]))
            f.write('\n')

    # ----------------
    # Fourth theft method
    # ----------------
    log_file = os.path.join(theft_folder, "theft-mean-random-diff-sample")
    with open(log_file, 'w') as f:
        for i in xrange(theft_number):
            f.write(','.join([str(random.uniform(Min_perc, Max_perc)) for _ in xrange(Row_Size)]))
            f.write('\n')

def normal_round(n):
    if (n - math.floor(n)) < 0.5:
        return int(math.floor(n))
    return int(math.ceil(n))


def split_thefts_days():

    print "Number of sets to split: (>=1)"
    split_num = int(raw_input())
    print "Number of days to choose: ([-349, -1],[1, 349], pos=from beginning; neg=from end)"
    split_days = int(raw_input())

    # Get experiment directory
    print "Index of experiment data to split: "
    #theft_exp_dir = os.path.join(Corr_Data_Dir, "theft_experiment"+raw_input())
    theft_exp_dir = Corr_Data_Dir
    if not os.path.isdir(theft_exp_dir):
        print "The data for experiment doesn't exist: ", theft_exp_dir
        sys.exit(0)

    # Create sub folder
    split_dir = os.path.join(theft_exp_dir, "N{}_D{}".format(split_num, split_days))
    if os.path.isdir(split_dir):
        print "{} folder already exist. Would you like to overwrite it? Y/N".format(split_dir)
        reply = raw_input()
        if reply.lower() == "y" or reply.lower() == 'yes':
            shutil.rmtree(split_dir)
        else:
            print "Quiting"
            sys.exit(0)
    os.makedirs(split_dir)

    origin_usage_dir = os.path.join(Corr_Data_Dir, "data")
    if not os.path.isdir(origin_usage_dir):
        print "data usage cannot be found: ", origin_usage_dir
        sys.exit(0)
    for i in xrange(split_num):
        start_apt = normal_round(Total_House * float(i)/split_num)
        end_apt = normal_round(Total_House * float(i+1)/split_num)
        print "apt start {} end {}".format(start_apt, end_apt)
        split_sub_dir = os.path.join(split_dir, "{}-{}".format(start_apt, end_apt))
        os.makedirs(split_sub_dir)
        
        # copy energy usage
        new_usage_dir = os.path.join(split_sub_dir, "data")
        os.makedirs(new_usage_dir)
        if split_days > 0:
            start_day = 0
            end_day = split_days
        else:
            start_day = Days + split_days
            end_day = Days
        print "day start {} end {}".format(start_day, end_day)
        for apt in xrange(start_apt, end_apt):
            with open(os.path.join(origin_usage_dir, "Apt{}".format(apt+1)), 'r') as f:
                content = f.readlines()
            content = content[start_day:end_day]

            with open(os.path.join(new_usage_dir, "Apt{}".format(apt+1)), 'w') as f:
                for l in content:
                    f.write(l)

        # copy theft vectors
        origin_vector_file = os.path.join(theft_exp_dir, "theft-vectors")
        new_vector_file = os.path.join(split_sub_dir, "theft-vectors")
        with open(origin_vector_file, 'r') as f:
            vectors = [int(v) for v in f.readline().split(',')]
        new_vectors = []
        new_vectors_index = [] # for 3rd, 4th theft method
        for i, v in enumerate(vectors):
            v_day = v / Total_House
            v_apt = v % Total_House
            if (v_day >= start_day and v_day < end_day and 
                v_apt >= start_apt and v_apt < end_apt):
                new_day = v_day - start_day
                new_apt = v_apt - start_apt
                new_vectors.append(new_day*(end_apt-start_apt) + new_apt)
                new_vectors_index.append(i)
        with open(new_vector_file, 'w') as f:
            f.write(','.join([str(t) for t in new_vectors]))

        # First theft method
        origin_log = os.path.join(theft_exp_dir, "theft-constant-steal")
        new_log = os.path.join(split_sub_dir, "theft-constant-steal")
        with open(origin_log, 'r') as f:
            constant_steal_coeff = f.readlines()
        with open(new_log, 'w') as f:
            f.write(''.join([constant_steal_coeff[index] for index in new_vectors_index]))

        # Second theft method
        origin_log = os.path.join(theft_exp_dir, "theft-period-steal")
        new_log = os.path.join(split_sub_dir, "theft-period-steal")
        shutil.copy2(origin_log, new_log)

        # Third theft method
        origin_log = os.path.join(theft_exp_dir, "theft-constant-steal-random-diff-sample")
        new_log = os.path.join(split_sub_dir, "theft-constant-steal-random-diff-sample")
        with open(origin_log, 'r') as f:
            random_steal_coeff = f.readlines()
        with open(new_log, 'w') as f:
            f.write(''.join([random_steal_coeff[index] for index in new_vectors_index]))

        # Forth theft method
        origin_log = os.path.join(theft_exp_dir, "theft-mean-random-diff-sample")
        new_log = os.path.join(split_sub_dir, "theft-mean-random-diff-sample")
        with open(origin_log, 'r') as f:
            mean_coeff = f.readlines()
        with open(new_log, 'w') as f:
            f.write(''.join([mean_coeff[index] for index in new_vectors_index]))


    # Create files for sub-folder
    #log_file = os.path.join()


def scale_values():
    print "Pls provide input variable file:"
    log = raw_input()
    if not os.path.isfile(log):
        print "File not exist: ", log
        sys.exit(0)

    print "Pls provide scale value [-1, 1] (Pos=scale*x, Neg=scale*x+1):"
    scale = float(raw_input())

    with open(log, 'r') as readf:
        lines = readf.readlines()

    new_log = log + "_scale" + str(scale)
    with open(new_log, 'w') as writef:
        for line in lines:
            value = float(line.strip()) * scale
            if value < 0:
                value = value + 1.0
            writef.write(str(value) + "\n")


def add_noise(source_dir):
    print source_dir
    print "Key in noise percentage. (Unit is %, meaning if key in 50 => 50%)"
    noise_perc = float(raw_input())

    new_folder = source_dir + "_withNoise_" + str(noise_perc)
    if not os.path.isdir(new_folder):
        os.makedirs(new_folder)

    for log in os.listdir(source_dir):
        print "Add noise for ", log

        with open(os.path.join(source_dir, log), 'r') as f:
            lines = f.readlines()

        with open(os.path.join(new_folder, log), 'w') as f:
            for line in lines:
                new_values = [str(float(v)*(1.0+random.uniform(-noise_perc, noise_perc)/100.0)) for v in line.strip().split(',')]
                f.write(','.join(new_values))
                f.write('\n')


def compute_cross_correlations(daily_usage):
    results = []
    for i in xrange(len(daily_usage) - 1):
        for j in xrange(i+1, len(daily_usage), 1):
            results.append(abs(
                stats.pearsonr(np.asarray(daily_usage[i]), np.asarray(daily_usage[j])) [0]
                ))
    return results


def generate_max_min_random_usage():
    print "Key in data directory: "
    log_folder = raw_input()
    print "Key in number of apt: "
    apt_num = int(raw_input())
    print "Key in number of day: "
    day_num = int(raw_input())

    energy = load_energy_usage(log_folder, apt_num, day_num)
    print "loaded energy usage"

    print "Key in theft id log file: "
    theft_id_log = raw_input()
    thefts = load_theft_ids(theft_id_log)
    daily_thefts = convert_theft_to_daily(thefts, apt_num, day_num)

    random_energy_results = []
    for day in xrange(day_num):
        for theft in daily_thefts[day]:
            max_value = max(energy[day][theft])
            min_value = min(energy[day][theft])
            new_values = []
            for i in xrange(len(energy[day][theft])):
                new_values.append(random.uniform(min_value, max_value))
            random_energy_results.append(new_values)

    print "Key in output directory: "
    output_dir = raw_input()
    with open(os.path.join(output_dir, "theft-max-min-random-energyUsage"), 'w+') as f:
        for line in random_energy_results:
            f.write(','.join([str(v) for v in line]) + '\n')


def load_energy_usage(log_folder, apt_num, day_num):
    if not os.path.isdir(log_folder):
        print "Log directory not found: ", log_folder
        sys.exit(0)

    usage = [[None for _ in xrange(apt_num)] for _ in xrange(day_num)]
    house_indx = 0
    for i in xrange(Total_House):
        apt_log = os.path.join(log_folder, "Apt" + str(i+1))
        if not os.path.isfile(apt_log):
            continue
        with open(apt_log, 'r') as f:
            lines = f.readlines()
            for j in xrange(len(lines)):
                usage[j][house_indx] = [float(n) for n in lines[j].split(',')]
            house_indx += 1
    return np.asarray(usage)

def load_theft_ids(log_file):
    with open(log_file, 'r') as f:
        thefts = [int(v) for v in f.readline().split(',')]
    return thefts

def convert_theft_to_daily(vectors, apt_num, day_num):
    day_theft = [[] for _ in xrange(day_num)]

    for i in xrange(len(vectors)):
        day_theft[int(vectors[i] / apt_num)].append(vectors[i]%apt_num)

    return day_theft


def scale_usage_interval():
    print "Key in usage log file: "
    log_file = raw_input()

    print "Key in scale factor: (if log has 10 values, scale=2, result will have 5 values)"
    factor = int(raw_input())

    with open(log_file, 'r+') as f:
        lines = f.readlines()

    with open(log_file, 'w+') as f:
        for line in lines:
            values = line.strip().split(',')
            values = values[::factor]
            f.write(','.join(values) + '\n')


def main():
    print "Options"
    print "1. Generate theft folder and details."
    print "2. Copy original data to correlation experiment folder."
    print "3. Split existing theft data into smaller groups / days."
    print "4. Scale values of an variable file."
    print "5. Add noises for usages."
    print "6. Generate random usages between max/min values"
    print "7. Interval scale down for data usage:"
    print "8. Copy noisy data set into sub-folder. Make sure noisy data are generated first (i.e. option 5):"
    print "Your input is: ",
    option = raw_input()

    if option == "1":
        generate_theft(frequency=Frequency,
                       total_house=Total_House,
                       daily_theft_num=Daily_Theft_Num)
    elif option == "2":
        copy_process_original_data(source_dir=Ori_Data_Dir,
                                   target_dir=Corr_Data_Dir,
                                   total_data_num=Total_Num)
    elif option == "3":
        split_thefts_days()
    elif option == "4":
        scale_values()
    elif option == "5":
        add_noise(Noise_Source_Dir)
    elif option == "6":
        generate_max_min_random_usage()
    elif option == "7":
        scale_usage_interval()
    elif option == "8":
        print "Key in noise percentage. (Unit is %, meaning if key in 50 => 50%)"
        print "The original noise folder must contain the noisy data for copying"
        noise_perc = float(raw_input())
        copy_process_noise_data(noise = noise_perc)
    else:
        print "Wrong input!  Quiting..."


if __name__ == '__main__':
    main()

