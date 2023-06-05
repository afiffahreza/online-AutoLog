import os, datetime
import pandas as pd
import matplotlib.pyplot as plt
from prometheus_api_client import PrometheusConnect, MetricRangeDataFrame

def evaluate(df):
    print("Results:")
    print("True Positive: ", df[df['result'] == 'True Positive'].shape[0])
    print("True Negative: ", df[df['result'] == 'True Negative'].shape[0])
    print("False Positive: ", df[df['result'] == 'False Positive'].shape[0])
    print("False Negative: ", df[df['result'] == 'False Negative'].shape[0])
    print("\n")

    # Confusion Matrix
    print("Confusion Matrix:")
    print(pd.crosstab(df['injected_anomaly'], df['autolog_anomaly'], rownames=['Actual'], colnames=['Predicted'], margins=True))
    print("\n")

    # Recall, Precision, F1 Score, Accuracy
    recall = df[df['result'] == 'True Positive'].shape[0] / (df[df['result'] == 'True Positive'].shape[0] + df[df['result'] == 'False Negative'].shape[0])
    precision = df[df['result'] == 'True Positive'].shape[0] / (df[df['result'] == 'True Positive'].shape[0] + df[df['result'] == 'False Positive'].shape[0])
    accuracy = (df[df['result'] == 'True Positive'].shape[0] + df[df['result'] == 'True Negative'].shape[0]) / df.shape[0]
    f1_score = 2 * (precision * recall) / (precision + recall)

    print("Recall: ", recall)
    print("Precision: ", precision)
    print("Accuracy: ", accuracy)
    print("F1 Score: ", f1_score)
    print("\n")

if __name__ == '__main__':

    prometheus_host = os.environ.get('PROMETHEUS_HOST', 'http://localhost:9090')

    prom = PrometheusConnect(url=prometheus_host, disable_ssl=True)

    # autolog_injected_anomaly{autolog_injected_anomaly="anomaly"}
    start_time = datetime.datetime(2023, 6, 4, 14, 0, 0)
    end_time = datetime.datetime(2023, 6, 5, 2, 0, 0)

    metric_data_injected_anomaly = prom.get_metric_range_data(
        'autolog_injected_anomaly',
        label_config={'autolog_injected_anomaly': 'anomaly'},
        start_time=start_time,
        end_time=end_time,
        chunk_size=datetime.timedelta(hours=1)
    )

    # autolog_anomaly{autolog_anomaly="anomaly"}
    metric_data_autolog_anomaly = prom.get_metric_range_data(
        'autolog_anomaly',
        label_config={'autolog_anomaly': 'anomaly'},
        start_time=start_time,
        end_time=end_time,
        chunk_size=datetime.timedelta(hours=1)
    )

    metric_df_injected_anomaly = MetricRangeDataFrame(metric_data_injected_anomaly)
    metric_df_autolog_anomaly = MetricRangeDataFrame(metric_data_autolog_anomaly)

    # drop __name__, autolog_injected_anomaly, autolog_anomaly, instance, job columns
    metric_df_injected_anomaly = metric_df_injected_anomaly.drop(['__name__', 'autolog_injected_anomaly', 'instance', 'job'], axis=1)
    metric_df_autolog_anomaly = metric_df_autolog_anomaly.drop(['__name__', 'autolog_anomaly', 'instance', 'job'], axis=1)

    # modify index for merge with format:
    # from timestamp 2023-06-03 08:00:46.573999872 to 2023-06-03 08:00:46
    metric_df_injected_anomaly.index = metric_df_injected_anomaly.index.strftime('%Y-%m-%d %H:%M:%S')
    metric_df_autolog_anomaly.index = metric_df_autolog_anomaly.index.strftime('%Y-%m-%d %H:%M:%S')

    # merge
    merged_df = pd.merge(metric_df_injected_anomaly, metric_df_autolog_anomaly, how='outer', left_index=True, right_index=True)

    # fill NaN with 0
    merged_df = merged_df.fillna(0)

    # rename columns
    merged_df = merged_df.rename(columns={'value_x': 'injected_anomaly', 'value_y': 'autolog_anomaly'})

    # group every 5 rows with value 1 if there is at least one 1 in the group
    merged_df['injected_anomaly'] = merged_df['injected_anomaly'].rolling(5).apply(lambda x: 1 if x.any() else 0, raw=True)
    merged_df['autolog_anomaly'] = merged_df['autolog_anomaly'].rolling(5).apply(lambda x: 1 if x.any() else 0, raw=True)

    # drop rows except the first one of the 5 rows group
    merged_df = merged_df.iloc[::5, :]
    merged_df = merged_df.dropna()

    # count injected_anomaly and normal data
    injected_anomaly_count = merged_df[merged_df['injected_anomaly'] == 1].shape[0]
    normal_count = merged_df[merged_df['injected_anomaly'] == 0].shape[0]
    print("Injected Anomaly Count: ", injected_anomaly_count)
    print("Normal Count: ", normal_count)
    print("\n")

    # create another column with:
    # 'injected_anomaly' = 1 and 'autolog_anomaly' = 1 -> "True Positive"
    # 'injected_anomaly' = 1 and 'autolog_anomaly' = 0 -> "False Negative"
    # 'injected_anomaly' = 0 and 'autolog_anomaly' = 1 -> "False Positive"
    # 'injected_anomaly' = 0 and 'autolog_anomaly' = 0 -> "True Negative"
    merged_df['result'] = merged_df.apply(lambda row: 'True Positive' if row['injected_anomaly'] == 1
                                        and row['autolog_anomaly'] == 1 else 'False Negative' if row['injected_anomaly'] == 1
                                        and row['autolog_anomaly'] == 0 else 'False Positive' if row['injected_anomaly'] == 0
                                        and row['autolog_anomaly'] == 1 else 'True Negative', axis=1)
    
    print(merged_df.head(10))
    print("\n")

    evaluate(merged_df)
