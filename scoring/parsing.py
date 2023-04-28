import json
import pandas as pd
from os.path import dirname

from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from drain3.file_persistence import FilePersistence

persistence = FilePersistence("drain3_state.bin")

config = TemplateMinerConfig()
config.load(dirname(__file__) + "/drain3.ini")
config.profiling_enabled = False

template_miner = TemplateMiner(persistence, config)

log_file = open("dataset/BGL_2k.log", "r") # 700 MB LMAOOOO RIP RAM
log_lines = log_file.read().splitlines()
log_file.close()

for log_line in log_lines:
    result = template_miner.add_log_message(log_line)
    result_json = json.dumps(result)
    # print(result_json)
    # template = result["template_mined"]
    # params = template_miner.extract_parameters(template, log_line)
    # print("Parameters: " + str(params))

# print("Training done. Mined clusters:")

# for cluster in template_miner.drain.clusters:
#     print(cluster)

parsed_log_lines = []

for log_line in log_lines:
    result = template_miner.match(log_line)
    template = result.get_template()
    parsed_log_lines.append(template)

for log_line in parsed_log_lines:
    print(log_line)

# while True:
#     log_line = input("> ")
#     if log_line == 'q':
#         break
#     result = template_miner.add_log_message(log_line)
#     result_json = json.dumps(result)
#     print(result_json)
#     template = result["template_mined"]
#     params = template_miner.extract_parameters(template, log_line)
#     print("Parameters: " + str(params))

# print("Training done. Mined clusters:")
# for cluster in template_miner.drain.clusters:
#     print(cluster)

# print(f"Starting inference mode, matching to pre-trained clusters. Input log lines or 'q' to finish")
# while True:
#     log_line = input("> ")
#     if log_line == 'q':
#         break
#     cluster = template_miner.match(log_line)
#     if cluster is None:
#         print(f"No match found")
#     else:
#         template = cluster.get_template()
#         print(f"Matched template #{cluster.cluster_id}: {template}")
#         print(f"Parameters: {template_miner.get_parameter_list(template, log_line)}")