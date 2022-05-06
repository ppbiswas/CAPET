# CAPET
Electricity theft pinpointing 
-----------------------------------------------------------------
How to Run: Codes for data preprocessing and theft data generation
-----------------------------------------------------------------

1. Install python 2.7 and libraries
   Libs: numpy, scipy, ml_metrics, sklearn.

2. Open "TheftDataGenerator.py". Ensure that you edit paths for the raw data downloaded from the Smart* website.

3. Input options as prompted and as per your requirement.
	E.g. Option 1: Generate the theft vector.
	     Option 2: Import and format the original data.
	     
	     
**How to run: You can use either of 'dataGenerator.py' or 'TheftDataGenerator.py' file**

-----------------------------------------------
Code
-----------------------------------------------

[analyzer.py, correlation.py, svm.py, linearRegression.py, config.py, dataGenerator.py]

 - analyzer.py: main script to execute the three analysis methods.
 - correlation.py, svm.py, linearRegression.py: provide computation functions.
 - config.py: configurations.
 - dataGenerator.py: provide helper functions to prepare data before running analyzer



-----------------------------------------------
Data
-----------------------------------------------

Besides the orginal data (in 1mins), there are processed data in 5, 15, 30, 45, 60 mins.

 - 5 min is the base for experiments.
 - There are four sub-group under each frequency.
 - Noise data only avail for 5 min now; If needed, could use dataGenerator.py to generate for other frequency.
 - Theft Ids and detail info can be found here.



-----------------------------------------------
How to Run
-----------------------------------------------

0. Install python 2.7 and libraries
   Libs: numpy, scipy, ml_metrics, sklearn.

1. Go to "code" directory, run "python analyzer.py"

2. Key in "Analysis Options"; Avail 1, 2, 3

3. Key in "Theft Behaviors"; Avail 0, 1, 2, 3, 4, 5
   0 is mixture of all while 1-5 represent specific behaviors

4. Key in "Frequency input in mins"; Avail 5, 15, 30, 45, 60 mins

5. Key in "Noise:"; Avail 0, 0.1, 0.5, 1

6. Key in "Number of Sub-group to split"; Avail is 1, 2, 3, 4

7. The script will compute number of thefts caught, percentage and map@k values for 10
