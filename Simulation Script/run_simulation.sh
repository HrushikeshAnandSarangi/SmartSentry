#!/bin/bash
python3 ./simulation_script.py &
python3 ./data_logger.py &
wait