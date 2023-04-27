#!/usr/bin/env python

import iplom as IPLoM
import Spell

input_dir    = './dataset/'  # The input directory of log file
output_dir   = './dataset/result/'  # The output directory of parsing results
log_file     = 'logs_test.txt'  # The input log file name
log_format   = '<Date> <Content>'  # BGL log format
# maxEventLen  = 200  # The maximal token number of log messages (default: 200)
# step2Support = 0  # The minimal support for creating a new partition (default: 0)
# CT           = 0.35  # The cluster goodness threshold (default: 0.35)
# lowerBound   = 0.25  # The lower bound distance (default: 0.25)
# upperBound   = 0.9  # The upper bound distance (default: 0.9)
# regex        = []  # Regular expression list for optional preprocessing (default: [])

# parser = IPLoM.LogParser(log_format=log_format, indir=input_dir, outdir=output_dir,
#                          maxEventLen=maxEventLen, step2Support=step2Support, CT=CT, 
#                          lowerBound=lowerBound, upperBound=upperBound, rex=regex)
tau        = 0.5  # Message type threshold (default: 0.5)
ip_regex = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?'
id_regex = r'[0-9a-fA-F]{32}'
hexa_regex = r'0x[0-9a-fA-F]+'
regex      = [ip_regex, id_regex, hexa_regex]  # Regular expression list for optional preprocessing (default: [])

parser = Spell.LogParser(indir=input_dir, outdir=output_dir, log_format=log_format, tau=tau, rex=regex)

parser.parse(log_file)
