from grafana_loki_client import Client
from grafana_loki_client.api.query_range import get_loki_api_v1_query_range

client = Client(base_url="http://localhost:3100")
query = "{app=\"frontend\"}"
res = get_loki_api_v1_query_range.sync(client=client, query=query, start="2023-05-18T10:00:00Z", end="2023-05-18T11:00:00Z", limit=5000)
print(res)
