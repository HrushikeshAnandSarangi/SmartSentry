# Time Series Data Simulation

This project simulates a **time series dataset** by sending each row of a `.txt` dataset over a network port at a fixed interval (default: 5 seconds). The data is sent sequentially, not randomly, to mimic a real-time feed.

---

## Requirements

- Python 3.x
- Network access (for sending data via TCP socket)

---

## Files

- `simulate_data.py` – Python script that reads the dataset and publishes it row by row.
- `data.txt` – Your dataset file (one row per line).
- `run_simulation.bat` – Windows batch file to run the simulation.
- `run_simulation.sh` – Linux/macOS shell script to run the simulation.

---

## Setup

1. Place `simulate_data.py` and `data.txt` in the same folder.
2. Modify the script if needed:
   - Change `HOST` and `PORT` to your target IP and port.
   - Change `time.sleep(5)` to adjust the interval between data rows.

---

## Running on Windows

1. Double-click `run_simulation.bat`  
   **OR**  
2. Open Command Prompt, navigate to the folder, and run:

```bat
run_simulation.bat
```

- The console will display each row sent.
- Press `Ctrl+C` to stop the simulation.

---

## Running on Linux/macOS

1. Make the shell script executable (first time only):

```bash
chmod +x run_simulation.sh
```

2. Run the simulation:

```bash
./run_simulation.sh
```

- The console will display each row sent.
- Press `Ctrl+C` to stop.



---

## Notes

- Ensure your firewall allows the chosen port.
- Empty lines in the dataset are skipped automatically.
- You can customize the Python script to parse or transform data before sending.
