from grafana_loki_client.api.query_range import get_loki_api_v1_query_range

def get_logs(client, app, time_start, time_end):
    query = '{app="'+app+'"}'
    res = get_loki_api_v1_query_range.sync(client=client, query=query, start=time_start, end=time_end, limit=5000)
    if res:
        logs = []
        for log in res.data.result[0].values:
            logs.append(log[1])
        return logs
    else:
        return []
