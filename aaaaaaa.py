import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import time
import streamlit.components.v1 as components

# --------------------------
# Page Configuration (Wide Layout, FIXED)
# --------------------------
st.set_page_config(
    page_title="1D Collision Simulation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------
# Session State Initialization (FIXED LOGIC)
# --------------------------
if "running" not in st.session_state:
    st.session_state.running = False
if "t_list" not in st.session_state:
    st.session_state.t_list = [0.0]
if "v1_list" not in st.session_state:
    st.session_state.v1_list = [0.0]
if "v2_list" not in st.session_state:
    st.session_state.v2_list = [0.0]
if "ke1_list" not in st.session_state:
    st.session_state.ke1_list = [0.0]
if "ke2_list" not in st.session_state:
    st.session_state.ke2_list = [0.0]
if "p1_list" not in st.session_state:
    st.session_state.p1_list = [0.0]
if "p2_list" not in st.session_state:
    st.session_state.p2_list = [0.0]
if "x1" not in st.session_state:
    st.session_state.x1 = 80.0
if "x2" not in st.session_state:
    st.session_state.x2 = 480.0
if "v1" not in st.session_state:
    st.session_state.v1 = 4.0
if "v2" not in st.session_state:
    st.session_state.v2 = -2.0

# --------------------------
# Title & Collision Formula (FIXED, UNCHANGED)
# --------------------------
st.title("One-Dimensional Collision Simulation")
st.markdown("### Collision Physics Formula")
st.latex(r'''
\begin{align*}
v_1' &= \frac{(m_1 - e m_2)v_1 + (1+e)m_2 v_2}{m_1 + m_2} \\
v_2' &= \frac{(1+e)m_1 v_1 + (m_2 - e m_1)v_2}{m_1 + m_2}
\end{align*}
''')
st.caption("e = Coefficient of Restitution | m = Mass | v = Initial Velocity | v' = Final Velocity")

# --------------------------
# Sidebar Controls (FIXED PARAMETER RANGES)
# --------------------------
st.sidebar.header("Simulation Parameters")
m1 = st.sidebar.slider("Mass of Ball 1 (m₁)", 0.5, 10.0, 2.0, 0.1)
m2 = st.sidebar.slider("Mass of Ball 2 (m₂)", 0.5, 10.0, 3.0, 0.1)
v1_init = st.sidebar.slider("Initial Velocity of Ball 1 (v₁)", -10.0, 10.0, 4.0, 0.1)
v2_init = st.sidebar.slider("Initial Velocity of Ball 2 (v₂)", -10.0, 10.0, -2.0, 0.1)
e = st.sidebar.slider("Coefficient of Restitution (e)", 0.0, 1.0, 1.0, 0.01)
dt = 0.05

# --------------------------
# Play / Pause / Reset Buttons (FIXED)
# --------------------------
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("▶️ Play"):
        st.session_state.running = True
with col2:
    if st.button("⏸️ Pause"):
        st.session_state.running = False
with col3:
    if st.button("🔄 Reset"):
        st.session_state.running = False
        st.session_state.t_list = [0.0]
        st.session_state.v1_list = [v1_init]
        st.session_state.v2_list = [v2_init]
        st.session_state.x1 = 80.0
        st.session_state.x2 = 480.0
        st.session_state.v1 = v1_init
        st.session_state.v2 = v2_init
        
        ke1_init = 0.5 * m1 * v1_init**2
        ke2_init = 0.5 * m2 * v2_init**2
        p1_init = m1 * v1_init
        p2_init = m2 * v2_init
        
        st.session_state.ke1_list = [ke1_init]
        st.session_state.ke2_list = [ke2_init]
        st.session_state.p1_list = [p1_init]
        st.session_state.p2_list = [p2_init]

# --------------------------
# Initial Kinetic Energy Display (FIXED)
# --------------------------
st.subheader("Initial Kinetic Energy")
ke1_initial = 0.5 * m1 * v1_init **2
ke2_initial = 0.5 * m2 * v2_init**2
total_initial_ke = ke1_initial + ke2_initial

col_k1, col_k2, col_tot = st.columns(3)
col_k1.metric("Ball 1 Initial KE", f"{ke1_initial:.2f} J")
col_k2.metric("Ball 2 Initial KE", f"{ke2_initial:.2f} J")
col_tot.metric("Total Initial KE", f"{total_initial_ke:.2f} J")

# --------------------------
# Canvas Animation (FIXED SIZE: 600×150, RED/GREEN BALLS, JS ANIMATION)
# --------------------------
st.subheader("Collision Animation")
canvas_placeholder = st.empty()

# --------------------------
# Real-time Plots Placeholder (FIXED)
# --------------------------
st.subheader("Time History Graphs")
plot_placeholder = st.empty()

# --------------------------
# Collision Calculation Function (FIXED LOGIC)
# --------------------------
def calculate_collision(m1, m2, v1, v2, e):
    v1_new = ((m1 - e*m2)*v1 + (1+e)*m2*v2) / (m1 + m2)
    v2_new = ((1+e)*m1*v1 + (m2 - e*m1)*v2) / (m1 + m2)
    return v1_new, v2_new

# --------------------------
# Main Simulation Loop
# --------------------------
while st.session_state.running:
    x1 = st.session_state.x1
    x2 = st.session_state.x2
    v1 = st.session_state.v1
    v2 = st.session_state.v2

    # Collision detection
    if abs(x2 - x1) <= 30:
        v1, v2 = calculate_collision(m1, m2, v1, v2, e)

    # Update positions
    x1 += v1 * dt * 3
    x2 += v2 * dt * 3

    # Boundary limits
    x1 = np.clip(x1, 15, 585)
    x2 = np.clip(x2, 15, 585)

    # Update state
    st.session_state.x1 = x1
    st.session_state.x2 = x2
    st.session_state.v1 = v1
    st.session_state.v2 = v2

    # Record data
    t_new = st.session_state.t_list[-1] + dt
    st.session_state.t_list.append(t_new)
    st.session_state.v1_list.append(v1)
    st.session_state.v2_list.append(v2)
    st.session_state.ke1_list.append(0.5*m1*v1**2)
    st.session_state.ke2_list.append(0.5*m2*v2**2)
    st.session_state.p1_list.append(m1*v1)
    st.session_state.p2_list.append(m2*v2)

    # Limit data points
    max_points = 200
    if len(st.session_state.t_list) > max_points:
        for key in ["t_list", "v1_list", "v2_list", "ke1_list", "ke2_list", "p1_list", "p2_list"]:
            st.session_state[key] = st.session_state[key][-max_points:]

    # --------------------------
    # JS Canvas (600×150, RED GREEN BALLS)
    # --------------------------
    with canvas_placeholder:
        js_canvas = f"""
        <canvas id="collisionCanvas" width="600" height="150" style="background:white; border:1px solid #ccc;"></canvas>
        <script>
            const canvas = document.getElementById('collisionCanvas');
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0,0,600,150);
            
            // Ground line
            ctx.beginPath();
            ctx.moveTo(0, 120);
            ctx.lineTo(600, 120);
            ctx.lineWidth = 3;
            ctx.strokeStyle = 'black';
            ctx.stroke();
            
            // Ball 1 (RED)
            ctx.beginPath();
            ctx.arc({x1}, 120, 15, 0, Math.PI*2);
            ctx.fillStyle = 'red';
            ctx.fill();
            ctx.strokeStyle = 'black';
            ctx.stroke();
            
            // Ball 2 (GREEN)
            ctx.beginPath();
            ctx.arc({x2}, 120, 15, 0, Math.PI*2);
            ctx.fillStyle = 'limegreen';
            ctx.fill();
            ctx.strokeStyle = 'black';
            ctx.stroke();
        </script>
        """
        components.html(js_canvas, height=155)

    # --------------------------
    # Three English Graphs (FIXED STYLE)
    # --------------------------
    with plot_placeholder:
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 4))
        
        # Velocity vs Time
        ax1.plot(st.session_state.t_list, st.session_state.v1_list, label="Ball 1", color="red", linewidth=2)
        ax1.plot(st.session_state.t_list, st.session_state.v2_list, label="Ball 2", color="limegreen", linewidth=2)
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Velocity (m/s)")
        ax1.set_title("Velocity vs Time")
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_locator(MaxNLocator(5))

        # Kinetic Energy vs Time
        ax2.plot(st.session_state.t_list, st.session_state.ke1_list, label="Ball 1", color="red", linewidth=2)
        ax2.plot(st.session_state.t_list, st.session_state.ke2_list, label="Ball 2", color="limegreen", linewidth=2)
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Kinetic Energy (J)")
        ax2.set_title("Kinetic Energy vs Time")
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_locator(MaxNLocator(5))

        # Momentum vs Time
        ax3.plot(st.session_state.t_list, st.session_state.p1_list, label="Ball 1", color="red", linewidth=2)
        ax3.plot(st.session_state.t_list, st.session_state.p2_list, label="Ball 2", color="limegreen", linewidth=2)
        ax3.set_xlabel("Time (s)")
        ax3.set_ylabel("Momentum (kg·m/s)")
        ax3.set_title("Momentum vs Time")
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.xaxis.set_major_locator(MaxNLocator(5))

        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)

    time.sleep(0.01)

# --------------------------
# Static Display When Paused/Reset
# --------------------------
if not st.session_state.running:
    with canvas_placeholder:
        js_canvas = f"""
        <canvas id="collisionCanvas" width="600" height="150" style="background:white; border:1px solid #ccc;"></canvas>
        <script>
            const canvas = document.getElementById('collisionCanvas');
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0,0,600,150);
            ctx.beginPath();
            ctx.moveTo(0, 120);
            ctx.lineTo(600, 120);
            ctx.lineWidth = 3;
            ctx.strokeStyle = 'black';
            ctx.stroke();
            
            ctx.beginPath();
            ctx.arc({st.session_state.x1}, 120, 15, 0, Math.PI*2);
            ctx.fillStyle = 'red';
            ctx.fill();
            ctx.stroke();
            
            ctx.beginPath();
            ctx.arc({st.session_state.x2}, 120, 15, 0, Math.PI*2);
            ctx.fillStyle = 'limegreen';
            ctx.fill();
            ctx.stroke();
        </script>
        """
        components.html(js_canvas, height=155)

    with plot_placeholder:
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 4))
        ax1.plot(st.session_state.t_list, st.session_state.v1_list, color="red", label="Ball 1", linewidth=2)
        ax1.plot(st.session_state.t_list, st.session_state.v2_list, color="limegreen", label="Ball 2", linewidth=2)
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Velocity (m/s)")
        ax1.set_title("Velocity vs Time")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        ax2.plot(st.session_state.t_list, st.session_state.ke1_list, color="red", label="Ball 1", linewidth=2)
        ax2.plot(st.session_state.t_list, st.session_state.ke2_list, color="limegreen", label="Ball 2", linewidth=2)
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Kinetic Energy (J)")
        ax2.set_title("Kinetic Energy vs Time")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        ax3.plot(st.session_state.t_list, st.session_state.p1_list, color="red", label="Ball 1", linewidth=2)
        ax3.plot(st.session_state.t_list, st.session_state.p2_list, color="limegreen", label="Ball 2", linewidth=2)
        ax3.set_xlabel("Time (s)")
        ax3.set_ylabel("Momentum (kg·m/s)")
        ax3.set_title("Momentum vs Time")
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
