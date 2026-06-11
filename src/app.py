import streamlit as st
import pandas as pd
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="SmartSignal", page_icon="🚦", layout="wide")

DIRECTIONS = ["South → North", "North → South", "East → West", "West → East"]
PASS_TIME_PER_VEHICLE = 2  # 1 vehicle needs 2 signal seconds


def calculate_signal_times(cars, peds, emg, cycle_time):
    scores = {}
    for d in DIRECTIONS:
        scores[d] = cars[d] + peds[d] * 2 + emg[d] * 12

    active = [d for d in DIRECTIONS if scores[d] > 0]
    if not active:
        return {d: 0 for d in DIRECTIONS}, scores

    min_green = 5
    min_ped_green = 8

    reserved = {}
    for d in DIRECTIONS:
        if scores[d] > 0:
            reserved[d] = max(min_green, min_ped_green if peds[d] > 0 else min_green)
        else:
            reserved[d] = 0

    remaining = max(0, cycle_time - sum(reserved.values()))
    total_score = sum(scores[d] for d in active)

    times = reserved.copy()
    for d in active:
        times[d] += int(remaining * scores[d] / total_score)

    diff = cycle_time - sum(times.values())
    if diff != 0:
        max_dir = max(active, key=lambda x: scores[x])
        times[max_dir] += diff

    return times, scores


def waiting_score(cars, green_times, cycle_time):
    return sum(cars[d] * (cycle_time - green_times[d]) for d in DIRECTIONS if cars[d] > 0)


def apply_cycle_result(cars, emg, times):
    remaining_cars = {}
    remaining_emg = {}

    for d in DIRECTIONS:
        capacity = times[d] // PASS_TIME_PER_VEHICLE

        emg_passed = min(emg[d], capacity)
        remaining_capacity = max(0, capacity - emg_passed)

        normal_passed = min(cars[d], remaining_capacity)

        remaining_emg[d] = max(0, emg[d] - emg_passed)
        remaining_cars[d] = max(0, cars[d] - normal_passed)

    return remaining_cars, remaining_emg


def canvas_html(c1_cars, c1_peds, c1_emg, c1_times,
                inc_cars, inc_peds, inc_emg,
                c2_cars, c2_peds, c2_emg, c2_times):

    payload = {
        "directions": DIRECTIONS,
        "passTime": PASS_TIME_PER_VEHICLE,
        "cycle1": {"cars": c1_cars, "peds": c1_peds, "emg": c1_emg, "times": c1_times},
        "incoming": {"cars": inc_cars, "peds": inc_peds, "emg": inc_emg},
        "cycle2": {"cars": c2_cars, "peds": c2_peds, "emg": c2_emg, "times": c2_times}
    }

    data_json = json.dumps(payload)

    return f"""
<!DOCTYPE html>
<html>
<head>
<style>
    body {{
        margin: 0;
        background: #0f172a;
        color: white;
        font-family: Arial, sans-serif;
    }}
    .wrap {{
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 28px;
        padding: 24px;
        min-height: 1180px;
    }}
    .title {{
        font-size: 34px;
        font-weight: 900;
        margin-bottom: 6px;
    }}
    .sub {{
        color: #94a3b8;
        font-size: 18px;
        margin-bottom: 18px;
    }}
    .status {{
        background: #020617;
        border: 1px solid #334155;
        border-radius: 18px;
        padding: 16px;
        font-size: 21px;
        font-weight: 900;
        margin-bottom: 18px;
        line-height: 1.45;
    }}
    .layout {{
        display: grid;
        grid-template-columns: 1.25fr 1fr;
        gap: 18px;
        align-items: start;
    }}
    canvas {{
        width: 100%;
        background: #111827;
        border: 1px solid #475569;
        border-radius: 24px;
    }}
    .cards {{
        display: grid;
        grid-template-columns: 1fr;
        gap: 12px;
    }}
    .card {{
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 18px;
        padding: 14px;
    }}
    .active {{
        border-color: #22c55e;
        box-shadow: 0 0 18px rgba(34,197,94,.65);
    }}
    .dim {{
        opacity: .48;
    }}
    .dir {{
        font-size: 19px;
        font-weight: 900;
        margin-bottom: 6px;
    }}
    .num {{
        font-size: 24px;
        font-weight: 900;
    }}
    .line {{
        color: #bae6fd;
        font-size: 15px;
        font-weight: 700;
        margin-top: 3px;
    }}
    .green {{
        color: #86efac;
        font-size: 16px;
        font-weight: 900;
        margin-top: 4px;
    }}
    .incoming {{
        display: none;
        margin-top: 16px;
        background: #facc15;
        color: #111827;
        border-radius: 16px;
        padding: 14px;
        font-size: 18px;
        font-weight: 900;
        line-height: 1.45;
    }}
</style>
</head>

<body>
<div class="wrap">
    <div class="title">🚦 SmartSignal Simulation Mode</div>
    <div class="sub">Canvas simulation · emoji vehicles · 5x demo speed · 1 vehicle passes every 2 signal seconds</div>

    <div id="status" class="status">Starting simulation...</div>

    <div class="layout">
        <canvas id="simCanvas" width="820" height="560"></canvas>

        <div>
            <div id="cycleTitle" class="status">Cycle 1: Initial Optimization</div>

            <div class="cards">
                <div id="card0" class="card">
                    <div class="dir">South → North</div>
                    <div class="num"><span id="cars0"></span> cars</div>
                    <div class="line">🚑 Emergency: <span id="emg0"></span></div>
                    <div class="line">🚶 Pedestrians: <span id="ped0"></span></div>
                    <div class="green">Green: <span id="green0"></span> sec</div>
                </div>
                <div id="card1" class="card">
                    <div class="dir">North → South</div>
                    <div class="num"><span id="cars1"></span> cars</div>
                    <div class="line">🚑 Emergency: <span id="emg1"></span></div>
                    <div class="line">🚶 Pedestrians: <span id="ped1"></span></div>
                    <div class="green">Green: <span id="green1"></span> sec</div>
                </div>
                <div id="card2" class="card">
                    <div class="dir">East → West</div>
                    <div class="num"><span id="cars2"></span> cars</div>
                    <div class="line">🚑 Emergency: <span id="emg2"></span></div>
                    <div class="line">🚶 Pedestrians: <span id="ped2"></span></div>
                    <div class="green">Green: <span id="green2"></span> sec</div>
                </div>
                <div id="card3" class="card">
                    <div class="dir">West → East</div>
                    <div class="num"><span id="cars3"></span> cars</div>
                    <div class="line">🚑 Emergency: <span id="emg3"></span></div>
                    <div class="line">🚶 Pedestrians: <span id="ped3"></span></div>
                    <div class="green">Green: <span id="green3"></span> sec</div>
                </div>
            </div>

            <div id="incomingBox" class="incoming"></div>
        </div>
    </div>
</div>

<script>
const DATA = {data_json};
const directions = DATA.directions;
const PASS_TIME = DATA.passTime;

let cycleData = [
    {{
        title: "Cycle 1: Initial Optimization",
        cars: DATA.cycle1.cars,
        peds: DATA.cycle1.peds,
        emg: DATA.cycle1.emg,
        times: DATA.cycle1.times
    }},
    {{
        title: "Cycle 2: Re-Optimization After New Demand Arrives",
        cars: DATA.cycle2.cars,
        peds: DATA.cycle2.peds,
        emg: DATA.cycle2.emg,
        times: DATA.cycle2.times
    }}
];

const canvas = document.getElementById("simCanvas");
const ctx = canvas.getContext("2d");

let cycleIndex = 0;
let phaseIndex = 0;
let current = cycleData[0];

let moving = null;
let moveStart = null;
let moveDuration = 400; // visual vehicle speed
let phaseCapacity = 0;
let phasePassed = 0;
let secondsLeft = 0;

const paths = {{
    "South → North": {{ start: [410, 515], end: [410, 45], label: "🚗⬆️", emg: "🚑⬆️" }},
    "North → South": {{ start: [410, 45], end: [410, 515], label: "🚗⬇️", emg: "🚑⬇️" }},
    "East → West": {{ start: [760, 280], end: [60, 280], label: "⬅️🚗", emg: "⬅️🚑" }},
    "West → East": {{ start: [60, 280], end: [760, 280], label: "🚗➡️", emg: "🚑➡️" }}
}};

function drawRoad() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = "#111827";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = "#475569";
    ctx.fillRect(360, 0, 100, 560);
    ctx.fillRect(0, 240, 820, 100);

    ctx.fillStyle = "#64748b";
    ctx.fillRect(360, 240, 100, 100);

    ctx.strokeStyle = "#cbd5e1";
    ctx.setLineDash([16, 16]);
    ctx.lineWidth = 3;

    ctx.beginPath();
    ctx.moveTo(410, 0);
    ctx.lineTo(410, 560);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(0, 290);
    ctx.lineTo(820, 290);
    ctx.stroke();

    ctx.setLineDash([]);

    drawSignalBox("South → North", 500, 420, phaseIndex === 0);
    drawSignalBox("North → South", 500, 75, phaseIndex === 1);
    drawSignalBox("East → West", 610, 355, phaseIndex === 2);
    drawSignalBox("West → East", 80, 165, phaseIndex === 3);

    ctx.font = "bold 18px Arial";
    ctx.fillStyle = "#e5e7eb";
    ctx.fillText("North", 382, 28);
    ctx.fillText("South", 380, 540);
    ctx.fillText("West", 25, 285);
    ctx.fillText("East", 755, 285);
}}

function drawSignalBox(name, x, y, active) {{
    ctx.fillStyle = active ? "#064e3b" : "#1e293b";
    ctx.strokeStyle = active ? "#22c55e" : "#334155";
    ctx.lineWidth = 2;
    roundRect(x, y, 185, 50, 12, true, true);

    ctx.beginPath();
    ctx.fillStyle = active ? "#22c55e" : "#ef4444";
    ctx.arc(x + 18, y + 25, 8, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 14px Arial";
    ctx.fillText(name, x + 34, y + 21);

    const t = current.times[name] || 0;
    ctx.fillStyle = "#fde68a";
    ctx.font = "bold 13px Arial";
    ctx.fillText("Green: " + t + " sec", x + 34, y + 39);
}}

function drawEmoji(text, x, y) {{
    ctx.font = "34px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(text, x, y);
}}

function drawStaticQueues() {{
    directions.forEach((d) => {{
        const p = paths[d].start;
        const cars = current.cars[d] || 0;
        const emg = current.emg[d] || 0;

        ctx.fillStyle = "#0f172a";
        ctx.strokeStyle = "#334155";
        ctx.lineWidth = 1;
        roundRect(p[0] - 70, p[1] - 58, 140, 46, 10, true, true);

        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 14px Arial";
        ctx.textAlign = "center";
        ctx.fillText("🚗 " + cars + " / 🚑 " + emg, p[0], p[1] - 30);
    }});
}}

function roundRect(x, y, w, h, r, fill, stroke) {{
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
    if (fill) ctx.fill();
    if (stroke) ctx.stroke();
}}

function updateCards() {{
    document.getElementById("cycleTitle").innerHTML = current.title;

    directions.forEach((d, i) => {{
        document.getElementById("cars" + i).innerHTML = current.cars[d];
        document.getElementById("emg" + i).innerHTML = current.emg[d];
        document.getElementById("ped" + i).innerHTML = current.peds[d];
        document.getElementById("green" + i).innerHTML = current.times[d];

        const card = document.getElementById("card" + i);
        card.className = i === phaseIndex ? "card active" : "card dim";
    }});
}}

function animate(timestamp) {{
    drawRoad();
    drawStaticQueues();

    if (moving) {{
        if (!moveStart) moveStart = timestamp;
        const progress = Math.min((timestamp - moveStart) / moveDuration, 1);

        const path = paths[moving.direction];
        const x = path.start[0] + (path.end[0] - path.start[0]) * progress;
        const y = path.start[1] + (path.end[1] - path.start[1]) * progress;

        drawEmoji(moving.emoji, x, y);

        if (progress >= 1) {{
            moveStart = null;

            if (moving.type === "emergency") {{
                current.emg[moving.direction] = Math.max(0, current.emg[moving.direction] - 1);
            }} else {{
                current.cars[moving.direction] = Math.max(0, current.cars[moving.direction] - 1);
            }}

            phasePassed += 1;
            secondsLeft -= PASS_TIME;

            moving = null;
            updateCards();

            setTimeout(nextVehicleOrPhase, 180);
        }}
    }}

    requestAnimationFrame(animate);
}}

function nextVehicleOrPhase() {{
    const direction = directions[phaseIndex];

    if (secondsLeft < PASS_TIME || phasePassed >= phaseCapacity) {{
        phaseIndex += 1;
        setTimeout(nextAction, 350);
        return;
    }}

    if ((current.emg[direction] || 0) > 0) {{
        document.getElementById("status").innerHTML =
            "🚑 Emergency vehicle passing: " + direction +
            " | Remaining Signal Time: " + secondsLeft +
            " sec | Capacity left: " + (phaseCapacity - phasePassed);
        moving = {{ direction: direction, type: "emergency", emoji: paths[direction].emg }};
        return;
    }}

    if ((current.cars[direction] || 0) > 0) {{
        document.getElementById("status").innerHTML =
            "🟢 Normal vehicle passing: " + direction +
            " | Remaining Signal Time: " + secondsLeft +
            " sec | Capacity left: " + (phaseCapacity - phasePassed);
        moving = {{ direction: direction, type: "normal", emoji: paths[direction].label }};
        return;
    }}

    phaseIndex += 1;
    setTimeout(nextAction, 350);
}}

function nextAction() {{
    if (phaseIndex >= directions.length) {{
        if (cycleIndex === 0) {{
            showIncoming();
            setTimeout(() => {{
                document.getElementById("incomingBox").style.display = "none";
                cycleIndex = 1;
                phaseIndex = 0;
                current = cycleData[1];
                updateCards();
                nextAction();
            }}, 1900);
        }} else {{
            document.getElementById("status").innerHTML =
                "✅ Simulation complete: remaining vehicles are kept if green time was not enough.";
            return;
        }}
        return;
    }}

    const direction = directions[phaseIndex];
    const green = current.times[direction] || 0;

    updateCards();

    if (green <= 0) {{
        document.getElementById("status").innerHTML =
            "⏭️ " + direction + " skipped because there is no active demand.";
        phaseIndex += 1;
        setTimeout(nextAction, 350);
        return;
    }}

    phaseCapacity = Math.floor(green / PASS_TIME);
    phasePassed = 0;
    secondsLeft = green;

    document.getElementById("status").innerHTML =
        "🚦 Green signal started: " + direction +
        " | Green: " + green +
        " sec | Max vehicles this phase: " + phaseCapacity;

    setTimeout(nextVehicleOrPhase, 400);
}}

function showIncoming() {{
    const inc = DATA.incoming;

    document.getElementById("incomingBox").style.display = "block";
    document.getElementById("incomingBox").innerHTML =
        "New demand arrived after Cycle 1:<br>" +
        "🚗 Cars — " +
        "S→N +" + inc.cars["South → North"] + ", " +
        "N→S +" + inc.cars["North → South"] + ", " +
        "E→W +" + inc.cars["East → West"] + ", " +
        "W→E +" + inc.cars["West → East"] + "<br>" +
        "🚑 Emergency — " +
        "S→N +" + inc.emg["South → North"] + ", " +
        "N→S +" + inc.emg["North → South"] + ", " +
        "E→W +" + inc.emg["East → West"] + ", " +
        "W→E +" + inc.emg["West → East"] + "<br>" +
        "🚶 Pedestrians — " +
        "S→N +" + inc.peds["South → North"] + ", " +
        "N→S +" + inc.peds["North → South"] + ", " +
        "E→W +" + inc.peds["East → West"] + ", " +
        "W→E +" + inc.peds["West → East"];
}}

updateCards();
requestAnimationFrame(animate);
setTimeout(nextAction, 700);
</script>
</body>
</html>
"""


st.title("🚦 SmartSignal")
st.subheader("Real-Time Adaptive Traffic Signal Control System")

st.write(
    "SmartSignal recalculates signal timing every cycle based on normal vehicles, "
    "emergency vehicles, pedestrian demand, and new incoming traffic."
)

st.sidebar.header("Demo Scenario")

scenario = st.sidebar.selectbox(
    "Select Scenario",
    ["Custom", "Morning Rush Hour", "West-Side Congestion", "Pedestrian Heavy", "Emergency Priority"]
)

if scenario == "Morning Rush Hour":
    sn_default, ns_default, ew_default, we_default = 10, 40, 20, 30
    sn_ped_default, ns_ped_default, ew_ped_default, we_ped_default = 3, 5, 2, 4
    sn_emg_default, ns_emg_default, ew_emg_default, we_emg_default = 0, 0, 0, 0
elif scenario == "West-Side Congestion":
    sn_default, ns_default, ew_default, we_default = 8, 15, 10, 70
    sn_ped_default, ns_ped_default, ew_ped_default, we_ped_default = 2, 3, 2, 5
    sn_emg_default, ns_emg_default, ew_emg_default, we_emg_default = 0, 0, 0, 0
elif scenario == "Pedestrian Heavy":
    sn_default, ns_default, ew_default, we_default = 5, 10, 7, 8
    sn_ped_default, ns_ped_default, ew_ped_default, we_ped_default = 20, 25, 18, 22
    sn_emg_default, ns_emg_default, ew_emg_default, we_emg_default = 0, 0, 0, 0
elif scenario == "Emergency Priority":
    sn_default, ns_default, ew_default, we_default = 12, 20, 18, 25
    sn_ped_default, ns_ped_default, ew_ped_default, we_ped_default = 3, 4, 2, 3
    sn_emg_default, ns_emg_default, ew_emg_default, we_emg_default = 0, 1, 0, 0
else:
    sn_default, ns_default, ew_default, we_default = 10, 40, 20, 30
    sn_ped_default, ns_ped_default, ew_ped_default, we_ped_default = 3, 5, 2, 4
    sn_emg_default, ns_emg_default, ew_emg_default, we_emg_default = 0, 0, 0, 0

st.divider()

st.header("1. Initial Traffic Input")

c1, c2, c3, c4 = st.columns(4)

with c1:
    sn_count = st.number_input("South → North Cars", min_value=0, value=sn_default, step=5)
    sn_emg = st.number_input("South → North Emergency", min_value=0, value=sn_emg_default, step=1)
    sn_ped = st.number_input("South → North Pedestrians", min_value=0, value=sn_ped_default, step=1)

with c2:
    ns_count = st.number_input("North → South Cars", min_value=0, value=ns_default, step=5)
    ns_emg = st.number_input("North → South Emergency", min_value=0, value=ns_emg_default, step=1)
    ns_ped = st.number_input("North → South Pedestrians", min_value=0, value=ns_ped_default, step=1)

with c3:
    ew_count = st.number_input("East → West Cars", min_value=0, value=ew_default, step=5)
    ew_emg = st.number_input("East → West Emergency", min_value=0, value=ew_emg_default, step=1)
    ew_ped = st.number_input("East → West Pedestrians", min_value=0, value=ew_ped_default, step=1)

with c4:
    we_count = st.number_input("West → East Cars", min_value=0, value=we_default, step=5)
    we_emg = st.number_input("West → East Emergency", min_value=0, value=we_emg_default, step=1)
    we_ped = st.number_input("West → East Pedestrians", min_value=0, value=we_ped_default, step=1)

st.header("2. New Demand After One Cycle")

n1, n2, n3, n4 = st.columns(4)

with n1:
    sn_incoming = st.number_input("New South → North Cars", min_value=0, value=5, step=1)
    sn_new_emg = st.number_input("New South → North Emergency", min_value=0, value=0, step=1)
    sn_new_ped = st.number_input("New South → North Pedestrians", min_value=0, value=2, step=1)

with n2:
    ns_incoming = st.number_input("New North → South Cars", min_value=0, value=12, step=1)
    ns_new_emg = st.number_input("New North → South Emergency", min_value=0, value=0, step=1)
    ns_new_ped = st.number_input("New North → South Pedestrians", min_value=0, value=3, step=1)

with n3:
    ew_incoming = st.number_input("New East → West Cars", min_value=0, value=7, step=1)
    ew_new_emg = st.number_input("New East → West Emergency", min_value=0, value=0, step=1)
    ew_new_ped = st.number_input("New East → West Pedestrians", min_value=0, value=1, step=1)

with n4:
    we_incoming = st.number_input("New West → East Cars", min_value=0, value=3, step=1)
    we_new_emg = st.number_input("New West → East Emergency", min_value=0, value=0, step=1)
    we_new_ped = st.number_input("New West → East Pedestrians", min_value=0, value=2, step=1)

cycle_time = st.slider("Total Signal Cycle Time (seconds)", 40, 160, 80, step=10)

st.caption(
    "Simulation rule: 1 vehicle needs 2 signal seconds to pass. "
    "If green time is not enough, remaining vehicles stay for the next cycle."
)

st.divider()

if st.button("🚦 Run Adaptive Signal Simulation", type="primary"):
    cycle1_cars = {
        "South → North": sn_count,
        "North → South": ns_count,
        "East → West": ew_count,
        "West → East": we_count
    }

    cycle1_peds = {
        "South → North": sn_ped,
        "North → South": ns_ped,
        "East → West": ew_ped,
        "West → East": we_ped
    }

    cycle1_emg = {
        "South → North": sn_emg,
        "North → South": ns_emg,
        "East → West": ew_emg,
        "West → East": we_emg
    }

    incoming_cars = {
        "South → North": sn_incoming,
        "North → South": ns_incoming,
        "East → West": ew_incoming,
        "West → East": we_incoming
    }

    incoming_peds = {
        "South → North": sn_new_ped,
        "North → South": ns_new_ped,
        "East → West": ew_new_ped,
        "West → East": we_new_ped
    }

    incoming_emg = {
        "South → North": sn_new_emg,
        "North → South": ns_new_emg,
        "East → West": ew_new_emg,
        "West → East": we_new_emg
    }

    cycle1_times, cycle1_scores = calculate_signal_times(
        cycle1_cars, cycle1_peds, cycle1_emg, cycle_time
    )

    remaining_cars_after_cycle1, remaining_emg_after_cycle1 = apply_cycle_result(
        cycle1_cars, cycle1_emg, cycle1_times
    )

    cycle2_cars = {
        d: remaining_cars_after_cycle1[d] + incoming_cars[d]
        for d in DIRECTIONS
    }

    cycle2_peds = {
        d: cycle1_peds[d] + incoming_peds[d]
        for d in DIRECTIONS
    }

    cycle2_emg = {
        d: remaining_emg_after_cycle1[d] + incoming_emg[d]
        for d in DIRECTIONS
    }

    cycle2_times, cycle2_scores = calculate_signal_times(
        cycle2_cars, cycle2_peds, cycle2_emg, cycle_time
    )

    fixed_times = {d: cycle_time // 4 for d in DIRECTIONS}

    fixed_score = waiting_score(cycle1_cars, fixed_times, cycle_time)
    smart_score = waiting_score(cycle1_cars, cycle1_times, cycle_time)

    improvement = 0 if fixed_score == 0 else ((fixed_score - smart_score) / fixed_score) * 100

    st.header("3. Simulation Mode")

    components.html(
        canvas_html(
            cycle1_cars, cycle1_peds, cycle1_emg, cycle1_times,
            incoming_cars, incoming_peds, incoming_emg,
            cycle2_cars, cycle2_peds, cycle2_emg, cycle2_times
        ),
        height=1300
    )

    st.header("4. Fixed Signal vs SmartSignal")

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric("Fixed Signal Waiting Score", int(fixed_score))

    with m2:
        st.metric("SmartSignal Waiting Score", int(smart_score))

    with m3:
        st.metric("Improvement", f"{improvement:.1f}%")

    st.header("5. Green Time Change")

    chart_df = pd.DataFrame({
        "Direction": DIRECTIONS,
        "Cycle 1": [cycle1_times[d] for d in DIRECTIONS],
        "Cycle 2": [cycle2_times[d] for d in DIRECTIONS]
    })

    st.bar_chart(chart_df.set_index("Direction"))

    st.header("6. Cycle Comparison Table")

    table_df = pd.DataFrame({
        "Direction": DIRECTIONS,
        "Initial Cars": [cycle1_cars[d] for d in DIRECTIONS],
        "Initial Emergency": [cycle1_emg[d] for d in DIRECTIONS],
        "Initial Pedestrians": [cycle1_peds[d] for d in DIRECTIONS],
        "Cycle 1 Demand Score": [cycle1_scores[d] for d in DIRECTIONS],
        "Cycle 1 Green": [cycle1_times[d] for d in DIRECTIONS],
        "Remaining Cars After Cycle 1": [remaining_cars_after_cycle1[d] for d in DIRECTIONS],
        "Remaining Emergency After Cycle 1": [remaining_emg_after_cycle1[d] for d in DIRECTIONS],
        "New Cars": [incoming_cars[d] for d in DIRECTIONS],
        "New Emergency": [incoming_emg[d] for d in DIRECTIONS],
        "New Pedestrians": [incoming_peds[d] for d in DIRECTIONS],
        "Cycle 2 Cars": [cycle2_cars[d] for d in DIRECTIONS],
        "Cycle 2 Emergency": [cycle2_emg[d] for d in DIRECTIONS],
        "Cycle 2 Pedestrians": [cycle2_peds[d] for d in DIRECTIONS],
        "Cycle 2 Demand Score": [cycle2_scores[d] for d in DIRECTIONS],
        "Cycle 2 Green": [cycle2_times[d] for d in DIRECTIONS]
    })

    st.dataframe(table_df, width="stretch")

    st.header("7. Optimization Pseudo-code")

    st.code(
        """
1. Collect normal vehicle count, emergency vehicle count, pedestrian count, and new arrivals
2. Calculate demand score = normal vehicles + pedestrians × 2 + emergency vehicles × 12
3. Allocate green time based on weighted demand ratio
4. During each phase, 1 vehicle passes every 2 signal seconds
5. If green time is not enough, remaining vehicles stay for the next cycle
6. Add newly arrived vehicles, pedestrians, and emergency vehicles
7. Recalculate signal timing for the next cycle
8. Compare fixed signal control with SmartSignal
        """,
        language="text"
    )

    st.header("8. ICT Pipeline Mapping")

    st.markdown("""
1. **Data Generation** → Normal vehicles, emergency vehicles, pedestrians, and new incoming traffic are entered.  
2. **Transmission** → Traffic data is transmitted through the web interface.  
3. **Collection** → The system collects four-way intersection demand data.  
4. **AI / Recovery** → The adaptive rule-based algorithm calculates green-light time using weighted demand.  
5. **Decision** → Remaining vehicles are preserved and signal timing is recalculated after traffic conditions change.  
6. **Dashboard** → The simulation, comparison, chart, table, and pseudo-code visualize the result.
""")

else:
    st.info("Enter traffic values and click 'Run Adaptive Signal Simulation'.")
