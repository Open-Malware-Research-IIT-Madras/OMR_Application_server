"""
Module Name: os_scripts_production_ready.py

Description:
    Compares baseline OS process data against new process logs to
    identify deviations. Loads a base pickle file and a new CSV,
    constructs process-to-PID mappings, excludes processes based on
    differences, and outputs a filtered CSV report.

Functions:
    os_scripts(filename):
        Compares the baseline process dataset with a new dataset from
        returned OS logs, removes excluded processes, and writes a
        processed CSV to the report directory.

Classes:
    None defined in this file.

Usage:
    Import and call os_scripts() with a filename (without extension) to
    process OS logs:
        os_scripts("log1")

Author:
    Allan Pais
"""


import pandas as pd

def os_scripts(filename):
    path = "/home/omrapp/Desktop/reporthash/"
    PATH = "/home/omrapp/Desktop/reporthash/returned_os_logs/" + filename + ".csv"
    
    # Load the base dataframe and the new CSV to compare
    df = pd.read_pickle("/home/omrapp/Desktop/Jugaad_testV1/base_image.pkl")
    df1 = pd.read_csv(PATH)

    # ----- For the first dataframe -----
    keys = df['Process Name'].unique()
    dict_processes = {key: [] for key in keys}  # dictionary comprehension
    
    for i in range(len(df['Process Name'])):
        process = df['Process Name'].iloc[i]
        process_id = df['PID'].iloc[i]
        if process_id not in dict_processes[process]:
            dict_processes[process].append(process_id)

    # ----- For the second dataframe -----
    keys_1 = df1['Process Name'].unique()
    dict_processes_1 = {key: [] for key in keys_1}  # dictionary comprehension

    for i in range(len(df1['Process Name'])):
        process = df1['Process Name'].iloc[i]
        process_id = df1['PID'].iloc[i]
        if process_id not in dict_processes_1[process]:
            dict_processes_1[process].append(process_id)

    # Processes to exclude based on symmetric difference between sets
    processes_to_exclude = list(
        set(df['Process Name']) - set(dict_processes_1.keys()).symmetric_difference(set(dict_processes.keys()))
    )

    # Drop rows corresponding to excluded processes
    for process in processes_to_exclude:
        indices = df[df['Process Name'] == process].index
        df.drop(index=list(indices), inplace=True)

    # Reset index and save filtered CSVs
    df.index = range(1, len(df) + 1)
    df.to_csv(path + "radar_processed_ostrails_" + filename + ".csv", sep=",")
