import pandas as pd
from datetime import datetime, timedelta
from app.weighting import weight_baseline
from app.preprocess import preprocess, tokenize
from os.path import dirname

from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from drain3.file_persistence import FilePersistence

persistence = FilePersistence("drain3_state.bin")

config = TemplateMinerConfig()
config.load(dirname(__file__) + "/drain3.ini")
config.profiling_enabled = False

template_miner = TemplateMiner(persistence, config)

if __name__ == "__main__":

    print("Starting scoring service...")
    print("Time: " + str(datetime.now()))

    applications = ['R00','R01','R02','R03','R04','R05','R06','R07','R10','R11','R12','R13','R14','R15','R16','R17','R20',
        'R21','R22','R23','R24','R25','R26','R27','R30','R31','R32','R33','R34','R35','R36','R37','R40','R41','R42','R43',
        'R44','R45','R46','R47','R50','R51','R52','R53','R54','R55','R56','R57','R60','R61','R62','R63','R64','R65',
        'R66','R67','R70','R71','R72','R73','R74','R75','R76','R77','UNKNOWNLOCATION','UNSPECIFIED']
    log_period = 300

    # Read log file
    log_file = open("dataset/BGL.log", "r")
    
    # Log Structure
    # <log type> <id> <date> <logging entity> <datetime> <logging entity> <log>
    # date format: YYYY.MM.DD
    # logging entity format: RXX-{unimportant string} or UNKNOWN_LOCATION for 'UNKNOWNLOCATION' or NULL for 'UNSPECIFIED'
    # datetime format: YYYY-MM-DD-HH.MM.SS.mmmmmm

    # Split log file into lines
    log_lines = log_file.read().splitlines()

    # Close log file
    log_file.close()

    # Group log lines by logging entity and datetime using P=300s
    # Log time full 2005-06-03-15.42.50.363779 until 2006-01-04-08.00.05.233639
    # Time iteration: 2005-06-03-15.40 - 2005-06-03-15.45, ..., 2006-01-04-08.00 - 2006-01-04-08.05
    # Total time iterations: ~ 288 * 180 = 51840
    time_iteration_dict = {}
    start_time = datetime.strptime("2005-06-03-15.40.00", "%Y-%m-%d-%H.%M.%S")
    end_time = datetime.strptime("2006-01-04-08.05.00", "%Y-%m-%d-%H.%M.%S")
    time_iteration = 0
    while start_time < end_time:
        # print("Time iteration: " + str(time_iteration) + " - " + str(start_time) + " - " + str(start_time + timedelta(seconds=log_period)))
        time_iteration_dict[time_iteration] = (start_time, start_time + timedelta(seconds=log_period))
        start_time += timedelta(seconds=log_period)
        time_iteration += 1

    # print count time iteration
    print("Time iteration count: " + str(time_iteration))
    log_per_time_per_entity = {}
    # log_group_datetime = None
    time_iteration = 0

    # print("Creating default scoring dict...")
    # print("Time: " + str(datetime.now()))
    for time_iteration in time_iteration_dict:
        log_per_time_per_entity[time_iteration] = {}
        for application in applications:
            log_per_time_per_entity[time_iteration][application] = []
        log_per_time_per_entity[time_iteration]['label'] = 'OK'
    # print("Done creating default scoring dict...")
    # print("Time: " + str(datetime.now()))

    time_iteration = 0
    label = 'OK'
    # error_lines = {}
    for log_line in log_lines:
        log = log_line.split(" ")
        log_datetime = datetime.strptime(log[4], "%Y-%m-%d-%H.%M.%S.%f")
        current_entity = log[3][0:3]
        if label == 'OK' and log[0] == '-':
            label = 'OK'
        else:
            label = 'ALERT'
        if current_entity == "UNK":
            current_entity = "UNKNOWNLOCATION"
        elif current_entity == "NUL":
            current_entity = "UNSPECIFIED"
        log_line_without_first_six = " ".join(log[6:])
        template_miner.add_log_message(log_line_without_first_six)
        # if log_group_datetime is None:
        #     log_group_datetime = log_datetime
        while log_datetime > time_iteration_dict[time_iteration][1]:
            if log[0] == '-':
                label = 'OK'
            time_iteration += 1
        # if log_datetime - log_group_datetime > timedelta(seconds=log_period):
        #     if log[0] == '-':
        #         label = 'OK'
        #     log_group_datetime = log_datetime
        #     time_iteration += 1
        if time_iteration not in log_per_time_per_entity:
            log_per_time_per_entity[time_iteration] = {}
        if current_entity not in log_per_time_per_entity[time_iteration]:
            log_per_time_per_entity[time_iteration][current_entity] = []
        log_per_time_per_entity[time_iteration][current_entity].append(log_line_without_first_six)
        log_per_time_per_entity[time_iteration]['label'] = label
        # if label == 'ALERT':
        #     if time_iteration not in error_lines:
        #         error_lines[time_iteration] = []
        #     error_lines[time_iteration].append(log_line)

    # Preprocess log lines
    preprocessed_log_per_time_per_entity = {}
    for time_iteration in log_per_time_per_entity:
        for entity in log_per_time_per_entity[time_iteration]:
            if entity == 'label':
                continue
            if time_iteration not in preprocessed_log_per_time_per_entity:
                preprocessed_log_per_time_per_entity[time_iteration] = {}
            templates = []
            for template in log_per_time_per_entity[time_iteration][entity]:
                # print(template)
                result = template_miner.match(template)
                if result is None:
                    # print("none")
                    templates.append('')
                else:
                    # print("hit")
                    templates.append(result.get_template())
            # print(templates)
            preprocessed_log_per_time_per_entity[time_iteration][entity] = tokenize(preprocess(templates))
            # print(preprocessed_log_per_time_per_entity[time_iteration][entity])
            # if time_iteration in error_lines:
            #     print("Time iteration: " + str(time_iteration))
            #     print("Entity: " + entity)
            #     print("Log lines: " + str(preprocessed_log_per_time_per_entity[time_iteration][entity]))

    # Print preprocessed log lines
    # for time_iteration in preprocessed_log_per_time_per_entity:
    #     for entity in preprocessed_log_per_time_per_entity[time_iteration]:
    #         print("Time iteration: " + str(time_iteration))
    #         print("Entity: " + entity)
    #         print("Log lines: " + str(preprocessed_log_per_time_per_entity[time_iteration][entity]))
    #         print("")
    
    # Score log lines per entity
    scores = {}
    for entity in applications:
        current_log = []
        for time_iteration in preprocessed_log_per_time_per_entity:
            # print(entity)
            # print(preprocessed_log_per_time_per_entity[time_iteration])
            if entity in preprocessed_log_per_time_per_entity[time_iteration]:
                current_log.append(preprocessed_log_per_time_per_entity[time_iteration][entity])
            else:
                current_log.append({})
        scores[entity] = weight_baseline(current_log)
    
    # Add id and label to scores
    scores['Label'] = []
    scores['Id'] = []
    for time_iteration in log_per_time_per_entity:
        scores['Label'].append(log_per_time_per_entity[time_iteration]['label'])
        scores['Id'].append(time_iteration)
        
    # Print scores
    # for entity in applications:
    #     print("Entity: " + entity)
    #     print("Scores: " + str(scores[entity]))
    #     print("")

    # Create pandas dataframe
    df = pd.DataFrame(scores)
    df.to_csv("./dataset/scores_final.csv", index=False)

    # Create error log
    # error_log = open("dataset/error_log.log", "w")
    # for time_iteration in error_lines:
    #     error_log.write("Time iteration: " + str(time_iteration))
    #     error_log.write("\n")
    #     for line in error_lines[time_iteration]:
    #         error_log.write(line)
    #         error_log.write("\n")
    #     error_log.write("\n")

    print("Finished scoring service.")
    print("Time: " + str(datetime.now()))
