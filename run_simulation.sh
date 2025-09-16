#!/bin/bash
python3 ./Simulation Script/simulation_script.py &
python3 ./Simulation Script/data_logger.py &
python3 ./ml model/anomally_predictor.py &
wait