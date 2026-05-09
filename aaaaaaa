import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ====================== Page Config ======================
st.set_page_config(
    page_title="1D Elastic Collision Simulation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== Session State Init ======================
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "reset_flag" not in st.session_state:
    st.session_state.reset_flag = True
if "time_data" not in st.session_state:
    st.session_state.time_data = []
if "v1_data" not in st.session_state:
    st.session_state.v1_data = []
if "v2_data" not in st.session_state:
    st.session_state.v2_data = []
if "ek_data" not in st.session_state:
    st.session_state.ek_data = []
if "p_data" not in st.session_state:
    st.session_state.p_data = []

# ====================== Collision Formula ======================
def collision_velocity(m1, m2, v1, v2, e):
    v1f = ((m1 - e * m2) * v1 + (1 + e) * m2 * v2) / (m1 + m2)
    v2f = ((m2 - e * m1) * v2 + (1 + e) * m1 * v1) / (m1 + m2)
    return v1f, v2f

# ====================== Main Layout ======================
col_ctrl, col_param = st.columns([3, 1])

# Control Buttons
with col_ctrl:
    btn_play, btn_pause, btn_reset = st.columns(3)
    with btn_play:
        play = st.button("▶ Play", use_container_width=True)
    with btn_pause:
        pause = st.button("⏸ Pause", use_container_width=True)
    with btn_reset:
        reset = st.button("🔄 Reset", use_container_width=True)

# Parameter Settings
with col_param:
    st.subheader("Parameter Settings")
    m1 = st.slider("Mass m1 (kg)", 0.5, 5.0, 1.0, 0.1)
    m2 = st.slider("Mass m2 (kg)", 0.5, 5.0, 1.0, 0.1)
    v1_init = st.slider("Initial Velocity v1 (m/s)", -5.0, 5.0, 2.0, 0.1)
    v2_init = st.slider("Initial Velocity v2 (m/s)", -5.0, 5.0, 0.0, 0.1)
    e = st.slider("Restitution Coefficient e", 0.0, 1.0, 1.0, 0.05)

# Initial Kinetic Energy Display
ek_initial = 0.5 * m1 * v1_init**2 + 0.5 * m2 * v2_init**2
st.metric("Initial Total Kinetic Energy (J)", f"{ek_initial:.3f}")

# Button Logic
if play:
    st.session_state.is_running = True
    st.session_state.reset_flag = False
if pause:
    st.session_state.is_running = False
if reset:
    st.session_state.is_running = False
    st.session_state.reset_flag = True
    st.session_state.time_data.clear()
    st.session_state.v1_data.clear()
    st.session_state.v2_data.clear()
    st.session_state.ek_data.clear()
    st.session_state.p_data.clear()

# ====================== HTML Canvas Animation ======================
canvas_html = f"""
<html>
<head>
<meta charset="utf-8">
<style>
body{{margin:0;padding:10px;background:#f5f7fa;}}
#canvas{{border:2px solid #444;border-radius:8px;background:#ffffff;}}
</style>
</head>
<body>
<canvas id="canvas" width="900" height="180"></canvas>
<script>
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let w = canvas.width, h = canvas.height;

// Physical Params
let m1 = {m1}, m2 = {m2};
let v1 = {v1_init}, v2 = {v2_init};
let e = {e};
let x1 = 80, x2 = 350;
let r = 25;
let run = {str(st.session_state.is_running).lower()};
let reset = {str(st.session_state.reset_flag).lower()};

function resetBall(){{
    x1 = 80; x2 = 350;
    v1 = {v1_init}; v2 = {v2_init};
}}
if(reset) resetBall();

function draw(){{
    ctx.clearRect(0,0,w,h);
    // Ground line
    ctx.beginPath();
    ctx.moveTo(0, h/2+35);
    ctx.lineTo(w, h/2+35);
    ctx.strokeStyle="#999";ctx.lineWidth=2;ctx.stroke();

    // Ball1 Red
    ctx.beginPath();
    ctx.arc(x1, h/2, r, 0, Math.PI*2);
    ctx.fillStyle="#ff4444";ctx.fill();ctx.stroke();
    // Ball2 Cyan
    ctx.beginPath();
    ctx.arc(x2, h/2, r, 0, Math.PI*2);
    ctx.fillStyle="#00cccc";ctx.fill();ctx.stroke();

    // Collision judge
    if(x1 + r >= x2 - r){{
        let v1f = ((m1 - e*m2)*v1 + (1+e)*m2*v2)/(m1+m2);
        let v2f = ((m2 - e*m1)*v2 + (1+e)*m1*v1)/(m1+m2);
        v1 = v1f; v2 = v2f;
    }}
    // Wall bounce
    if(x1 - r <= 0 || x1 + r >= w) v1 *= -1;
    if(x2 - r <= 0 || x2 + r >= w) v2 *= -1;

    if(run){{
        x1 += v1;
        x2 += v2;
    }}
    requestAnimationFrame(draw);
}}
draw();
</script>
</body>
</html>
"""
st.components.v1.html(canvas_html, height=220)

# ====================== Data Record & Plot ======================
dt = 0.05
if st.session_state.is_running and not st.session_state.reset_flag:
    last_t = st.session_state.time_data[-1] if st.session_state.time_data else 0
    current_t = last_t + dt

    if len(st.session_state.v1_data) == 0:
        cv1, cv2 = v1_init, v2_init
    else:
        cv1 = st.session_state.v1_data[-1]
        cv2 = st.session_state.v2_data[-1]

    # Simple record data
    total_p = m1 * cv1 + m2 * cv2
    total_ek = 0.5*m1*cv1**2 + 0.5*m2*cv2**2

    st.session_state.time_data.append(current_t)
    st.session_state.v1_data.append(cv1)
    st.session_state.v2_data.append(cv2)
    st.session_state.p_data.append(total_p)
    st.session_state.ek_data.append(total_ek)

# Draw three charts
col1, col2, col3 = st.columns(3)

# 1. Velocity-Time
df_v = pd.DataFrame({
    "Time(s)": st.session_state.time_data,
    "v1(m/s)": st.session_state.v1_data,
    "v2(m/s)": st.session_state.v2_data
})
fig_v = px.line(df_v, x="Time(s)", y=["v1(m/s)","v2(m/s)"],
                title="Velocity - Time Curve")
fig_v.update_layout(xaxis_title="Time (s)", yaxis_title="Velocity (m/s)")
with col1:
    st.plotly_chart(fig_v, use_container_width=True)

# 2. Kinetic Energy-Time
df_ek = pd.DataFrame({
    "Time(s)": st.session_state.time_data,
    "Total_Energy(J)": st.session_state.ek_data
})
fig_ek = px.line(df_ek, x="Time(s)", y="Total_Energy(J)",
                 title="Kinetic Energy - Time Curve", color_discrete_sequence=["#ff4444"])
fig_ek.update_layout(xaxis_title="Time (s)", yaxis_title="Kinetic Energy (J)")
with col2:
    st.plotly_chart(fig_ek, use_container_width=True)

# 3. Momentum-Time
df_p = pd.DataFrame({
    "Time(s)": st.session_state.time_data,
    "Total_Momentum": st.session_state.p_data
})
fig_p = px.line(df_p, x="Time(s)", y="Total_Momentum",
                title="Momentum - Time Curve", color_discrete_sequence=["#00cccc"])
fig_p.update_layout(xaxis_title="Time (s)", yaxis_title="Momentum (kg·m/s)")
with col3:
    st.plotly_chart(fig_p, use_container_width=True)
