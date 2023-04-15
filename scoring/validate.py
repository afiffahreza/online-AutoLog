import os, time
from datetime import datetime, timedelta, timezone
from app.weighting import weight_baseline
from app.preprocess import preprocess, tokenize

if __name__ == "__main__":

    print("Starting scoring service...\n")

    applications = ['ID','NULL','R00','R01','R02','R03','R04','R05','R06','R07','R10','R11','R12','R13','R14','R15','R16','R17','R20',
        'R21','R22','R23','R24','R25','R26','R27','R30','R31','R32','R33','R34','R35','R36','R37','R40','R41','R42','R43',
        'R44','R45','R46','R47','R50','R51','R52','R53','R54','R55','R56','R57','R60','R61','R62','R63','R64','R65',
        'R66','R67','R70','R71','R72','R73','R74','R75','R76','R77','UNKNOWNLOCATION','UNSPECIFIED','Label']
    log_period = 300

    # Read log file
    log_file = open("dataset/BGL_2k.log", "r") # 700 MB LMAOOOO RIP RAM
    
    # Log Structure
    # <log type> <id> <date> <logging entity> <datetime> <logging entity> <log>
    # date format: YYYY.MM.DD
    # logging entity format: RXX-{unimportant string} or UNKNOWN_LOCATION for 'UNKNOWNLOCATION' or NULL for 'UNSPECIFIED'
    # datetime format: YYYY-MM-DD-HH.MM.SS.mmmmmm

    # Split log file into lines
    log_lines = log_file.read().splitlines()

    # Group log lines by logging entity and datetime using P=300s
    log_per_time_per_entity = {}
    log_group_datetime = None
    time_iteration = 0
    for log_line in log_lines:
        log = log_line.split(" ")
        log_datetime = datetime.strptime(log[4], "%Y-%m-%d-%H.%M.%S.%f")
        current_entity = log[3][0:3]
        log_line_without_first_six = " ".join(log[6:])
        if log_group_datetime is None:
            log_group_datetime = log_datetime
        if log_datetime - log_group_datetime > timedelta(seconds=log_period):
            log_group_datetime = log_datetime
            time_iteration += 1
        if time_iteration not in log_per_time_per_entity:
            log_per_time_per_entity[time_iteration] = {}
        if current_entity not in log_per_time_per_entity[time_iteration]:
            log_per_time_per_entity[time_iteration][current_entity] = []
        log_per_time_per_entity[time_iteration][current_entity].append(log_line_without_first_six)

    # Preprocess log lines
    preprocessed_log_per_time_per_entity = {}
    for time_iteration in log_per_time_per_entity:
        for entity in log_per_time_per_entity[time_iteration]:
            preprocessed_log_per_time_per_entity[time_iteration] = {}
            preprocessed_log_per_time_per_entity[time_iteration][entity] = tokenize(preprocess(log_per_time_per_entity[time_iteration][entity]))

    # Print preprocessed log lines
    # for time_iteration in preprocessed_log_per_time_per_entity:
    #     for entity in preprocessed_log_per_time_per_entity[time_iteration]:
    #         print("Time iteration: " + str(time_iteration))
    #         print("Entity: " + entity)
    #         print("Log lines: " + str(preprocessed_log_per_time_per_entity[time_iteration][entity]))
    #         print("")
    
    # Score log lines per entity
    scores = [[0 for x in range(len(applications))] for y in range(len(preprocessed_log_per_time_per_entity))]
    for entity in applications:
        current_array_log = []
        for time_iteration in preprocessed_log_per_time_per_entity:
            # print(entity)
            # print(preprocessed_log_per_time_per_entity[time_iteration])
            if entity in preprocessed_log_per_time_per_entity[time_iteration]:
                current_array_log.append(preprocessed_log_per_time_per_entity[time_iteration][entity])
            else:
                current_array_log.append([])
    # Print scores
    for entity in applications:
        print("Entity: " + entity)
        print("Scores: " + str(scores[applications.index(entity)]))
        print("")
