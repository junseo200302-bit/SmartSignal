# 🚦 SmartSignal

## Overview

SmartSignal is a traffic signal optimization project developed for the ICT Application Technology course.

Many traffic lights still use fixed signal timing even though traffic conditions change throughout the day. Because of this, some roads receive more green time than necessary while congested roads continue to experience long waiting times.

To address this issue, I developed SmartSignal, a Streamlit-based traffic signal optimization system. The system adjusts signal timing according to traffic demand and provides priority handling for emergency vehicles.

The application simulates a four-way intersection and visualizes how traffic conditions change over multiple signal cycles.

---

## Main Features

* Adaptive signal timing based on traffic demand
* Emergency vehicle priority handling
* Traffic flow simulation
* Waiting time comparison
* Throughput analysis
* Interactive Streamlit dashboard

---

## How It Works

1. Collect traffic demand from four directions.
2. Calculate a weighted demand score.
3. Allocate green-light duration dynamically.
4. Process vehicle movement during the signal cycle.
5. Carry remaining vehicles into the next cycle.
6. Recalculate signal timing when new traffic arrives.

---

## Technologies Used

* Python
* Streamlit
* Pandas
* HTML/CSS/JavaScript

---

## Repository Structure

```text
SmartSignal
├── src/
│   └── app.py
├── data/
│   └── sample_traffic_data.csv
├── README.md
├── 문제해결.md
└── requirements.txt
```

---

## Live Demo

https://smartsignal-teynb22yuz6wpqsqp3cym8.streamlit.app/

## Demo Video

https://www.youtube.com/watch?v=AZ7Uc7IFcnU&feature=youtu.be

---

## Project Purpose

The goal of this project is to demonstrate how adaptive signal control can improve traffic efficiency compared to traditional fixed-time traffic systems.

By dynamically adjusting signal timing and prioritizing emergency vehicles, the system can reduce waiting time and improve traffic flow in a simulated environment.

---

## Future Improvements

* Real traffic camera integration
* Computer vision vehicle detection
* AI-based traffic prediction
* Multi-intersection coordination

---

## Author

Junseo Lee

ICT Application Technology Final Project
