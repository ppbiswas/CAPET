#!/usr/bin/env python


# General

Method_Correlation = 1
Method_SVM = 2
Method_Linear_Regression = 3

Days = 349
Apts = 114
Default_Interval = 5  # mins

Min_perc = 0.1
Max_perc = 0.8

Log_Theft_ID = "theft-vectors"
Log_Constant_Var = "theft-constant-steal"
Log_Random_Var = "theft-constant-steal-random-diff-sample"
Log_Random_Mean_Var = "theft-mean-random-diff-sample"
Log_Max_Min_Random_Values = "theft-max-min-random-energyUsage"


# Correlation
Corr_Days = 70
Apt_Num_Sets = [[114], [57, 57], [38, 38, 38], [29, 28, 29, 28]]
Divide_Sets = [["N1_D-70/0-114"], ["N2_D-70/0-57", "N2_D-70/57-114"], 
               ["N3_D-70/0-38", "N3_D-70/38-76", "N3_D-70/76-114"],
               ["N4_D-70/0-29", "N4_D-70/29-57", "N4_D-70/57-86", "N4_D-70/86-114"]]


Corr_Origin_Data_Dir = 'theft_experiment_{}min/{}/data'
Corr_Noise_Data_Dir = 'theft_experiment_{}min/{}/data_withNoise_{}'
Corr_Theft_Info_Dir = 'theft_experiment_{}min/{}'
Corr_Theft_Id_Total = 'theft_experiment_{}min/N1_D-70/0-114/' + Log_Theft_ID


# Svm
Svm_Train_Days = 279
Svm_Test_Days = 70
Svm_Origin_Data_Dir = '../theft_experiment_{}min/data'
Svm_Noise_Data_Dir = '../theft_experiment_{}min/data_withNoise_{}'
Svm_Theft_Info_Dir = '../theft_experiment_{}min'


# Linear Regression
Lr_Days = 70
Lr_Origin_Data_Dir = '../theft_experiment_{}min/N1_D-70/0-114/data'
Lr_Noise_Data_Dir = '../theft_experiment_{}min/N1_D-70/0-114/data_withNoise_{}'
Lr_Theft_Info_Dir = '../theft_experiment_{}min/N1_D-70/0-114'

