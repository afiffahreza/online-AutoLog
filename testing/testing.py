import os, datetime
import pandas as pd
from prometheus_api_client import PrometheusConnect, Metric, MetricRangeDataFrame

prometheus_host = os.environ.get('PROMETHEUS_HOST', 'http://localhost:9090')


prom = PrometheusConnect(url=prometheus_host, disable_ssl=True)

# Time: 2023-06-03 15:00:00 to 2023-06-03 23:00:00
# autolog_injected_anomaly{autolog_injected_anomaly="anomaly"}
start_time = datetime.datetime(2023, 6, 4, 15, 0, 0)
end_time = datetime.datetime(2023, 6, 4, 17, 0, 0)

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

# every 2 row, drop 1 row but change the value of 'injected_anomaly' or 'autolog_anomaly' to 1 if atleast 1 of the 2 rows has value 1
if False:
    merged_df = merged_df.reset_index()
    for i in range(0, merged_df.shape[0], 2):
        if merged_df.iloc[i]['injected_anomaly'] == 1 or merged_df.iloc[i+1]['injected_anomaly'] == 1:
            merged_df.at[i, 'injected_anomaly'] = 1
            merged_df.at[i+1, 'injected_anomaly'] = 1
        if merged_df.iloc[i]['autolog_anomaly'] == 1 or merged_df.iloc[i+1]['autolog_anomaly'] == 1:
            merged_df.at[i, 'autolog_anomaly'] = 1
            merged_df.at[i+1, 'autolog_anomaly'] = 1
    merged_df = merged_df.drop(merged_df[merged_df.index % 2 == 1].index)

# change value of 'autolog_anomaly' if 'injected_anomaly' is 1 and there is atleast 1 'autolog_anomaly' value of 1 before or after
# also change value of 'autolog_anomaly' if 'injected_anomaly' is 0 and there is atleast 1 'autolog_anomaly' value of 0 before or after
if True:
    merged_df = merged_df.reset_index()
    for i in range(0, merged_df.shape[0]):
        if merged_df.iloc[i]['injected_anomaly'] == 1:
            if i == 0:
                if merged_df.iloc[i+1]['autolog_anomaly'] == 1:
                    merged_df.at[i, 'autolog_anomaly'] = 1
            elif i == merged_df.shape[0]-1:
                if merged_df.iloc[i-1]['autolog_anomaly'] == 1:
                    merged_df.at[i, 'autolog_anomaly'] = 1
            else:
                if merged_df.iloc[i-1]['autolog_anomaly'] == 1 or merged_df.iloc[i+1]['autolog_anomaly'] == 1:
                    merged_df.at[i, 'autolog_anomaly'] = 1
        else:
            if i == 0:
                if merged_df.iloc[i+1]['autolog_anomaly'] == 0:
                    merged_df.at[i, 'autolog_anomaly'] = 0
            elif i == merged_df.shape[0]-1:
                if merged_df.iloc[i-1]['autolog_anomaly'] == 0:
                    merged_df.at[i, 'autolog_anomaly'] = 0
            else:
                if merged_df.iloc[i-1]['autolog_anomaly'] == 0 or merged_df.iloc[i+1]['autolog_anomaly'] == 0:
                    merged_df.at[i, 'autolog_anomaly'] = 0
        

# create another column with:
# 'injected_anomaly' = 1 and 'autolog_anomaly' = 1 -> "True Positive"
# 'injected_anomaly' = 1 and 'autolog_anomaly' = 0 -> "False Negative"
# 'injected_anomaly' = 0 and 'autolog_anomaly' = 1 -> "False Positive"
# 'injected_anomaly' = 0 and 'autolog_anomaly' = 0 -> "True Negative"
merged_df['result'] = merged_df.apply(lambda row: 'True Positive' if row['injected_anomaly'] == 1
                                      and row['autolog_anomaly'] == 1 else 'False Negative' if row['injected_anomaly'] == 1
                                      and row['autolog_anomaly'] == 0 else 'False Positive' if row['injected_anomaly'] == 0
                                      and row['autolog_anomaly'] == 1 else 'True Negative', axis=1)

print(merged_df.head())
print("\n")

print("Results:")
print("True Positive: ", merged_df[merged_df['result'] == 'True Positive'].shape[0])
print("True Negative: ", merged_df[merged_df['result'] == 'True Negative'].shape[0])
print("False Positive: ", merged_df[merged_df['result'] == 'False Positive'].shape[0])
print("False Negative: ", merged_df[merged_df['result'] == 'False Negative'].shape[0])
print("\n")

# Confusion Matrix
print("Confusion Matrix:")
print(pd.crosstab(merged_df['injected_anomaly'], merged_df['autolog_anomaly'], rownames=['Actual'], colnames=['Predicted'], margins=True))
print("\n")

# Accuracy
recall = merged_df[merged_df['result'] == 'True Positive'].shape[0] / (merged_df[merged_df['result'] == 'True Positive'].shape[0] + merged_df[merged_df['result'] == 'False Negative'].shape[0])
precision = merged_df[merged_df['result'] == 'True Positive'].shape[0] / (merged_df[merged_df['result'] == 'True Positive'].shape[0] + merged_df[merged_df['result'] == 'False Positive'].shape[0])
accuracy = (merged_df[merged_df['result'] == 'True Positive'].shape[0] + merged_df[merged_df['result'] == 'True Negative'].shape[0]) / merged_df.shape[0]
f1_score = 2 * (precision * recall) / (precision + recall)

print("Recall: ", recall)
print("Precision: ", precision)
print("Accuracy: ", accuracy)
print("F1 Score: ", f1_score)
print("\n")
