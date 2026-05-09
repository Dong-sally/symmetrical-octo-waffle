import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# ====================== Page Configuration ======================
st.set_page_config(
    page_title="2D Collision Simulation",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("2D Perfectly Elastic Collision Simulation")

# ====================== Session State Initialization ======================
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "reset_count" not in st.session_state:
    st.session_state.reset_count = 0
if "data_idx" not in st.session_state:
    st.session_state.data_idx = 0
if "time_list" not in st.session_state:
    st.session_state.time_list = []
if "v_sum1_list" not in st.session_state:
    st.session_state.v_sum1_list = []
if "v_sum2_list" not in st.session_state:
    st.session_state.v_sum2_list = []
if "ek_total_list" not in st.session_state:
    st.session_state.ek_total_list = []
if "px_total_list" not in st.session_state:
    st.session_state.px_total_list = []

# ====================== 2D Collision Core Formula ======================
def two_d_collision(m1, m2, x1, y1, x2, y2, v1x, v1y, v2x, v2y, e):
    dx = x2 - x1
    dy = y2 - y1
    dist = np.hypot(dx, dy)
    if dist < 1e-6:
        return v1x, v1y, v2x, v2y
    nx = dx / dist
    ny = dy / dist
    v1n = v1x * nx + v1y * ny
    v2n = v2x * nx + v2y * ny
    v1t_x = v1x - v1n * nx
    v1t_y = v1y - v1n * ny
    v2t_x = v2x - v2n * nx
    v2t_y = v2y - v2y * ny

    v1n_new = ((m1 - e * m2) * v1n + (1 + e) * m2 * v2n) / (m1 + m2)
    v2n_new = ((m2 - e * m1) * v2n + (1 + e) * m1 * v1n) / (m1 + m2)

    new_v1x = v1t_x + v1n_new * nx
    new_v1y = v1t_y + v1n_new * ny
    new_v2x = v2t_x + v2n_new * nx
    new_v2y = v2t_y + v2n_new * ny
    return new_v1x, new_v1y, new_v2x, new_v2y

# ====================== Sidebar Parameter Settings ======================
with st.sidebar:
    st.header("Simulation Parameters")
    col_m, col_v = st.columns(2)
    with col_m:
        m1 = st.slider("Mass m1 (kg)", 0.5, 5.0, 1.0, 0.1)
        m2 = st.slider("Mass m2 (kg)", 0.5, 5.0, 1.0, 0.1)
    with col_v:
        v1x = st.slider("V1 X", -4.0, 4.0, 1.5, 0.1)
        v1y = st.slider("V1 Y", -4.0, 4.0, 1.0, 0.1)
        v2x = st.slider("V2 X", -4.0, 4.0, 0.0, 0.1)
        v2y = st.slider("V2 Y", -4.0, 4.0, 0.0, 0.1)

    col_pos, col_set = st.columns(2)
    with col_pos:
        pos1_x = st.slider("Pos1 X", 50, 450, 120, 5)
        pos1_y = st.slider("Pos1 Y", 50, 350, 200, 5)
        pos2_x = st.slider("Pos2 X", 50, 450, 300, 5)
        pos2_y = st.slider("Pos2 Y", 50, 350, 200, 5)
    with col_set:
        dt_step = st.slider("Time Step", 0.01, 0.1, 0.05, 0.01)
        total_time = st.slider("Total Time", 5, 30, 15, 1)
        e_coeff = st.slider("Restitution Coefficient e", 0.0, 1.0, 1.0, 0.05)

# ====================== Center Control Buttons ======================
col_play, col_pause, col_reset = st.columns(3)
with col_play:
    btn_play = st.button("▶ Play", use_container_width=True)
with col_pause:
    btn_pause = st.button("⏸ Pause", use_container_width=True)
with col_reset:
    btn_reset = st.button("🔄 Reset", use_container_width=True)

# Button Logic
if btn_play:
    st.session_state.is_running = True
if btn_pause:
    st.session_state.is_running = False
if btn_reset:
    st.session_state.is_running = False
    st.session_state.reset_count += 1
    st.session_state.data_idx = 0
    st.session_state.time_list.clear()
    st.session_state.v_sum1_list.clear()
    st.session_state.v_sum2_list.clear()
    st.session_state.ek_total_list.clear()
    st.session_state.px_total_list.clear()

# ====================== HTML Canvas 2D Animation ======================
canvas_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body {{margin:0;padding:10px;background:#f8f9fa;}}
#simCanvas {{border:2px solid #333;border-radius:6px;background:#fff;}}
</style>
</head>
<body>
<canvas id="simCanvas" width="500" height="400"></canvas>
<script>
const cvs = document.getElementById('simCanvas');
const ctx = cvs.getContext('2d');
const W = cvs.width;
const H = cvs.height;

// Physical Params
const m1 = {m1}, m2 = {m2};
let v1x = {v1x}, v1y = {v1y};
let v2x = {v2x}, v2y = {v2y};
let x1 = {pos1_x}, y1 = {pos1_y};
let x2 = {pos2_x}, y2 = {pos2_y};
const e = {e_coeff};
const dt = {dt_step};
const r = 18;
let runState = {str(st.session_state.is_running).lower()};
let resetSig = {str(btn_reset).lower()};

function resetScene(){{
    x1 = {pos1_x}; y1 = {pos1_y};
    x2 = {pos2_x}; y2 = {pos2_y};
    v1x = {v1x}; v1y = {v1y};
    v2x = {v2x}; v2y = {v2y};
}}
if(resetSig) resetScene();

function collisionCalc(x1,y1,x2,y2,v1x,v1y,v2x,v2y){{
    let dx = x2 - x1;
    let dy = y2 - y1;
    let dist = Math.hypot(dx,dy);
    let nx = dx/dist;
    let ny = dy/dist;
    let v1n = v1x*nx + v1y*ny;
    let v2n = v2x*nx + v2y*ny;
    let v1tx = v1x - v1n*nx;
    let v1ty = v1y - v1n*ny;
    let v2tx = v2x - v2n*nx;
    let v2ty = v2y - v2n*ny;
    let v1nn = ((m1-e*m2)*v1n + (1+e)*m2*v2n)/(m1+m2);
    let v2nn = ((m2-e*m1)*v2n + (1+e)*m1*v1n)/(m1+m2);
    return [v1tx+v1nn*nx, v1ty+v1nn*ny, v2tx+v2nn*nx, v2ty+v2nn*ny];
}}

function drawArrow(sx,sy,ex,ey,color){{
    ctx.beginPath();
    ctx.strokeStyle=color;
    ctx.lineWidth=2;
    ctx.moveTo(sx,sy);
    ctx.lineTo(ex,ey);
    ctx.stroke();
}}

function render(){{
    ctx.clearRect(0,0,W,H);
    // Boundary bounce
    if(x1<=r||x1>=W-r) v1x=-v1x;
    if(y1<=r||y1>=H-r) v1y=-v1y;
    if(x2<=r||x2>=W-r) v2x=-v2x;
    if(y2<=r||y2>=H-r) v2y=-v2y;
    // Collision detect
    if(Math.hypot(x2-x1,y2-y1) <= 2*r){{
        [v1x,v1y,v2x,v2y] = collisionCalc(x1,y1,x2,y2,v1x,v1y,v2x,v2y);
        // Position correction
        let midX = (x1+x2)/2;
        let midY = (y1+y2)/2;
        x1 = midX - r;
        x2 = midX + r;
    }}
    // Update position
    if(runState){{
        x1 += v1x;
        y1 += v1y;
        x2 += v2x;
        y2 += v2y;
    }}
    // Draw ball1 Cyan
    ctx.beginPath();
    ctx.arc(x1,y1,r,0,Math.PI*2);
    ctx.fillStyle="#00b8d9";
    ctx.fill();
    ctx.strokeStyle="#007799";
    ctx.stroke();
    // Draw ball2 Pink
    ctx.beginPath();
    ctx.arc(x2,y2,r,0,Math.PI*2);
    ctx.fillStyle="#ff79a3";
    ctx.fill();
    ctx.strokeStyle="#cc4477";
    ctx.stroke();
    // Draw velocity vector
    drawArrow(x1,y1,x1+v1x*12,y1+v1y*12,"#005577");
    drawArrow(x2,y2,x2+v2x*12,y2+v2y*12,"#aa2255");
    requestAnimationFrame(render);
}}
render();
</script>
</body>
</html>
"""
st.components.v1.html(canvas_code, height=420)

# ====================== Real-Time Data Recording ======================
if st.session_state.is_running:
    current_t = len(st.session_state.time_list) * dt_step
    v1_sum = np.hypot(v1x, v1y)
    v2_sum = np.hypot(v2x, v2y)
    total_ek = 0.5 * m1 * (v1x**2 + v1y**2) + 0.5 * m2 * (v2x**2 + v2y**2)
    total_px = m1 * v1x + m2 * v2x

    st.session_state.time_list.append(round(current_t, 3))
    st.session_state.v_sum1_list.append(round(v1_sum, 3))
    st.session_state.v_sum2_list.append(round(v2_sum, 3))
    st.session_state.ek_total_list.append(round(total_ek, 3))
    st.session_state.px_total_list.append(round(total_px, 3))

# ====================== Three Timing Charts ======================
col_chart1, col_chart2, col_chart3 = st.columns(3)

# 1. Resultant Velocity - Time
df_v = pd.DataFrame({
    "Time(s)": st.session_state.time_list,
    "Ball1_Velocity": st.session_state.v_sum1_list,
    "Ball2_Velocity": st.session_state.v_sum2_list
})
fig_v = px.line(df_v, x="Time(s)", y=["Ball1_Velocity", "Ball2_Velocity"],
                title="Resultant Velocity - Time Curve")
fig_v.update_layout(xaxis_title="Time (s)", yaxis_title="Velocity (m/s)", template="plotly_white")
with col_chart1:
    st.plotly_chart(fig_v, use_container_width=True)

# 2. Total Kinetic Energy - Time
df_ek = pd.DataFrame({
    "Time(s)": st.session_state.time_list,
    "Total_Kinetic_Energy": st.session_state.ek_total_list
})
fig_ek = px.line(df_ek, x="Time(s)", y="Total_Kinetic_Energy",
                 title="Total Kinetic Energy - Time Curve", color_discrete_sequence=["#00b8d9"])
fig_ek.update_layout(xaxis_title="Time (s)", yaxis_title="Energy (J)", template="plotly_white")
with col_chart2:
    st.plotly_chart(fig_ek, use_container_width=True)

# 3. X Direction Total Momentum - Time
df_px = pd.DataFrame({
    "Time(s)": st.session_state.time_list,
    "X_Total_Momentum": st.session_state.px_total_list
})
fig_px = px.line(df_px, x="Time(s)", y="X_Total_Momentum",
                 title="X-axis Total Momentum - Time Curve", color_discrete_sequence=["#ff79a3"])
fig_px.update_layout(xaxis_title="Time (s)", yaxis_title="Momentum (kg·m/s)", template="plotly_white")
with col_chart3:
    st.plotly_chart(fig_px, use_container_width=True)
