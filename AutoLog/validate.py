import pandas as pd
import logging
from datetime import datetime, timedelta
from src.scoring import Scoring
from src.model import MultilayerAutoEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

if __name__ == "__main__":

    starting_time = datetime.now()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

    print("Starting training...")
    print("Time: " + str(starting_time.strftime("%Y-%m-%d %H:%M:%S")))

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
        time_iteration_dict[time_iteration] = (start_time, start_time + timedelta(seconds=log_period))
        start_time += timedelta(seconds=log_period)
        time_iteration += 1

    # print count time iteration
    print("Time iteration count: " + str(time_iteration))
    log_per_time_per_entity = {}
    time_iteration = 0

    for time_iteration in time_iteration_dict:
        log_per_time_per_entity[time_iteration] = {}
        for application in applications:
            log_per_time_per_entity[time_iteration][application] = []
        log_per_time_per_entity[time_iteration]['label'] = 'OK'

    time_iteration = 0
    label = 'OK'
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
        while log_datetime > time_iteration_dict[time_iteration][1]:
            if log[0] == '-':
                label = 'OK'
            time_iteration += 1
        if time_iteration not in log_per_time_per_entity:
            log_per_time_per_entity[time_iteration] = {}
        if current_entity not in log_per_time_per_entity[time_iteration]:
            log_per_time_per_entity[time_iteration][current_entity] = []
        log_per_time_per_entity[time_iteration][current_entity].append(log_line_without_first_six)
        log_per_time_per_entity[time_iteration]['label'] = label
    
    # Score log lines per entity
    scores = {}
    for entity in applications:
        scoring = Scoring()
        for time_iteration in log_per_time_per_entity:
            if entity in log_per_time_per_entity[time_iteration]:
                scoring.add_lines(lines=log_per_time_per_entity[time_iteration][entity])
            else:
                scoring.add_lines([])
        scores[entity] = scoring.calculate_baseline_score()
        scoring.save("./output/test230606/scoring_" + entity + ".pkl")
    
    # Add id and label to scores
    scores['Label'] = []
    scores['Id'] = []
    for time_iteration in log_per_time_per_entity:
        scores['Label'].append(log_per_time_per_entity[time_iteration]['label'])
        scores['Id'].append(time_iteration)

    # Create pandas dataframe
    df = pd.DataFrame(scores)
    # add dummy column
    df['dummy'] = 0
    df.head()

    # order last 2 column to first 2
    cols = df.columns.tolist()
    cols = cols[-2:] + cols[:-2]
    df = df[cols]
    df.head()

    # save to csv
    df.to_csv("./output/test230606/scoring.csv", index=False)

    df['Label'] = np.where(df['Label'] == 'OK', 0, 1)

    # Split anomalous and normal data
    good = df[df['Label'] == 0]
    bad = df[df['Label'] == 1]

    # Split good data into train and test
    x_train, x_test = train_test_split(good, test_size=0.016, random_state=345)

    # Concat bad data to test
    x_test = pd.concat([x_test, bad])

    # Split data into features and labels
    y_train = x_train['Label']
    y_test = x_test['Label']
    x_train = x_train.drop(['Label', 'dummy'], axis=1)
    x_test = x_test.drop(['Label', 'dummy'], axis=1)

    # Convert to numpy array
    x_train = x_train.values
    x_test = x_test.values

    # Scale data
    scaler = MinMaxScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    # Train model
    input_dim = x_train.shape[1]
    autoencoder = MultilayerAutoEncoder(input_dim = input_dim)
    autoencoder.summary()
    history, threshold = autoencoder.train(x_train_scaled, x_train_scaled, percentile=90, visualize=True)
    autoencoder.evaluate(x_test_scaled, y_test, threshold, visualize=True)

    # save model
    autoencoder.save_model("./output/test230606/model.pkl")

    print("Finished training.")
    print("Time: " + str(datetime.now()))
    print("Total time: " + str(datetime.now() - starting_time))
