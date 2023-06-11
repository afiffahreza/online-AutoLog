<h1 align="center">Final Project Repository<br/>AutoLog Online Learning on K8s Microservice</h1>
<p align="center">Afif Fahreza (18219058) - Information System and Technology - Bandung Institute of Technology</p>

## Overview
This repository contains the final project of the course II4091 & II4092 (Final Project 1 & 2). The project is about implementing AutoLog with Online Learning + Online Detection on K8s Microservice.

## Repository Structure
```
.
├── AutoLog                         # AutoLog parent folder
│   ├── src                         # Module used for AutoLog
│   ├── Dockerfile                  # Dockerfile for AutoLog serving app
│   ├── Dockerfile.training         # Dockerfile for AutoLog training app
│   ├── requirements.txt            # Python dependencies for Dockerized app
│   ├── requirements.local.txt      # Python dependencies for local ARM64 app
│   ├── validate.py                 # Python app for validating AutoLog using BGL dataset
│   ├── training.py                 # Python app for training AutoLog using Loki log backend
│   ├── serving.py                  # Python app for serving AutoLog using Loki log backend
│   ├── retraining.py               # Python app for simulating retraining AutoLog using Loki log backend
│   ├── drain3.ini                  # Configuration file for Drain3
├── explorations                    # Explorations for the project
│   ├── anomaly-detection           # AutoLog anomaly detection model exploration
│   ├── loki-retriever              # Loki logging querier exploration
│   ├── scoring                     # AutoLog scoring exploration
├── fault-injector                  # Fault injector for simulating log anomaly
├── k6                              # Load testing using k6
├── k8s                             # K8s deployment files
├── scripts                         # Scripts for running the project
├── terraform                       # Terraform files for deploying the project
├── testing                         # Testing files

```

## References
- https://github.com/ScalingLab/AutoLog
- https://github.com/logpai/Drain3/tree/master/drain3
