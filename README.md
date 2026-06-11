# 🚦 SmartSignal

Adaptive Traffic Signal Optimization System built with Streamlit.

## Project Overview

SmartSignal is an intelligent traffic signal optimization system that dynamically adjusts green-light duration according to real-time traffic demand.

Unlike traditional fixed-time traffic lights, SmartSignal allocates signal timing based on:

* Vehicle volume
* Pedestrian demand
* Emergency vehicle priority

The system simulates a four-way intersection and continuously recalculates signal timing to improve traffic flow and reduce waiting time.

---

## Key Features

* Dynamic signal timing optimization
* Emergency vehicle priority handling
* Traffic simulation visualization
* Throughput and waiting-time analysis
* Interactive Streamlit dashboard
* Multiple traffic scenarios

---

## System Logic

1. Collect traffic demand from all directions.
2. Calculate weighted demand scores.
3. Allocate green-light duration proportionally.
4. Process vehicle movement during the signal cycle.
5. Carry remaining vehicles into the next cycle.
6. Recalculate timing when new traffic arrives.

---

## Technology Stack

* Python
* Streamlit
* Pandas
* HTML / CSS / JavaScript (embedded simulation)

---

## Repository Structure

```text
SmartSignal
├── src/
│   └── app.py
├── data/
│   └── sample_traffic_data.csv
├── README.md
├── 문제 해결.md
└── requirements.txt
```

## Video Demonstration

Add your video link here.

Example:

https://youtube.com/your-video-link

---

## Future Improvements

* Real camera integration
* Computer vision vehicle detection
* AI-based traffic prediction
* Multi-intersection coordination

---

## Author

Junseo Lee

ICT Application Technology Final Project
