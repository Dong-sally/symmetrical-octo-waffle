import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import time
from streamlit_drawable_canvas import st_canvas

# --------------------------
# Page Configuration (Wide Layout)
# --------------------------
st.set_page_config(
    page_title="1D Collision Simulation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------
# Initialize Session State (Persistent Variables)
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
    st.session_state.x1 = 20.0
if "x2" not in st.session_state:
    st.session_state.x2 = 80.0
if "v1" not in st.session_state:
    st.session_state.v1 = 5.0
if "v2" not in st.session_state:
    st.session_state.v2 = -2.0

# --------------------------
# Title & Physics Formula (Styled)
# --------------------------
st.title("One-Dimensional Collision Simulation")
st.markdown("### Physics Formula: Velocity After Collision")
st.latex(r'''
\begin{align*}
v_1' &= \frac{(m_1 - e m_2)v_1 + (1+e)m_2 v_2}{m_1 + m_2} \\
v_2' &= \frac{(1+e)m_1 v_1 + (m_2 - e m_1)v_2}{m_1 + m_2}
\end{align*}
''')
st.caption("e = Coefficient of Restitution | m = Mass | v = Initial Velocity | v' = Final Velocity")

# --------------------------
# Control Panel (Sidebar)
# --------------------------
st.sidebar.header("Simulation Parameters")
m1 = st.sidebar.slider("Mass of Ball 1 (m₁)", 0.5, 10.0, 2.0, 0.1)
m2 = st.sidebar.slider("Mass of Ball 2 (m₂)", 0.5, 10.0, 3.0, 0.1)
v1_init = st.sidebar.slider("Initial Velocity of Ball 1 (v₁)", -10.0, 10.0, 5.0, 0.1)
v2_init = st.sidebar.slider("Initial Velocity of Ball 2 (v₂)", -10.0, 10.0, -2.0, 0.1)
e = st.sidebar.slider("Coefficient of Restitution (e)", 0.0, 1.0, 1.0, 0.01)
dt = 0.05  # Time step (fixed for smooth animation)

# --------------------------
# Control Buttons
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
        st.session_state.x1 = 20.0
        st.session_state.x2 = 80.0
        st.session_state.v1 = v1_init
        st.session_state.v2 = v2_init
        # Reset kinetic energy/momentum lists
        ke1 = 0.5 * m1 * v1_init**2
        ke2 = 0.5 * m2 * v2_init**2
        p1 = m1 * v1_init
        p2 = m2 * v2_init
        st.session_state.ke1_list = [ke1]
        st.session_state.ke2_list = [ke2]
        st.session_state.p1_list = [p1]
        st.session_state.p2_list = [p2]

# --------------------------
# Canvas Settings (Standard Size)
# --------------------------
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 200
BALL_RADIUS = 15
GROUND_Y = 150

# --------------------------
# Real-Time Kinetic Energy Display
# --------------------------
st.subheader("Real-Time Physical Quantities")
ke1_current = 0.5 * m1 * st.session_state.v1 **2
ke2_current = 0.5 * m2 * st.session_state.v2**2
total_ke = ke1_current + ke2_current
p1_current = m1 * st.session_state.v1
p2_current = m2 * st.session_state.v2
total_p = p1_current + p2_current

col_ke1, col_ke2, col_totke = st.columns(3)
col_ke1.metric("Kinetic Energy - Ball 1", f"{ke1_current:.2f} J")
col_ke2.metric("Kinetic Energy - Ball 2", f"{ke2_current:.2f} J")
col_totke.metric("Total Kinetic Energy", f"{total_ke:.2f} J")

# --------------------------
# Collision Physics Calculation
# --------------------------
def calculate_collision(m1, m2, v1, v2, e):
    v1_new = ((m1 - e*m2)*v1 + (1+e)*m2*v2) / (m1 + m2)
    v2_new = ((1+e)*m1*v1 + (m2 - e*m1)*v2) / (m1 + m2)
    return v1_new, v2_new

# --------------------------
# Dynamic Canvas Animation
# --------------------------
st.subheader("Collision Animation")
canvas_placeholder = st.empty()

# --------------------------
# Real-Time Plots Placeholder
# --------------------------
st.subheader("Time-History Graphs")
plot_placeholder = st.empty()

# --------------------------
# Main Simulation Loop
# --------------------------
while st.session_state.running:
    # Current state
    x1 = st.session_state.x1
    x2 = st.session_state.x2
    v1 = st.session_state.v1
    v2 = st.session_state.v2

    # Detect collision (balls touch)
    if abs(x2 - x1) <= 2 * BALL_RADIUS:
        v1, v2 = calculate_collision(m1, m2, v1, v2, e)

    # Update positions
    x1 += v1 * dt * 2  # Scale speed for visibility
    x2 += v2 * dt * 2

    # Boundary limits (prevent balls from leaving canvas)
    x1 = np.clip(x1, BALL_RADIUS, CANVAS_WIDTH - BALL_RADIUS)
    x2 = np.clip(x2, BALL_RADIUS, CANVAS_WIDTH - BALL_RADIUS)

    # Update session state
    st.session_state.x1 = x1
    st.session_state.x2 = x2
    st.session_state.v1 = v1
    st.session_state.v2 = v2

    # Record time and physical quantities
    t_new = st.session_state.t_list[-1] + dt
    st.session_state.t_list.append(t_new)
    st.session_state.v1_list.append(v1)
    st.session_state.v2_list.append(v2)
    st.session_state.ke1_list.append(0.5*m1*v1**2)
    st.session_state.ke2_list.append(0.5*m2*v2**2)
    st.session_state.p1_list.append(m1*v1)
    st.session_state.p2_list.append(m2*v2)

    # Keep data length limited (smooth plotting)
    max_points = 200
    if len(st.session_state.t_list) > max_points:
        for key in ["t_list", "v1_list", "v2_list", "ke1_list", "ke2_list", "p1_list", "p2_list"]:
            st.session_state[key] = st.session_state[key][-max_points:]

    # --------------------------
    # Draw Canvas Animation
    # --------------------------
    with canvas_placeholder:
        canvas = st_canvas(
            fill_color="#f0f2f6",
            stroke_width=2,
            stroke_color="black",
            background_color="#ffffff",
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            drawing_mode=False,
            key="canvas",
            display_only=True
        )
        
        # Draw ground line
        import PIL
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), "white")
        draw = ImageDraw.Draw(img)
        draw.line([(0, GROUND_Y), (CANVAS_WIDTH, GROUND_Y)], fill="black", width=3)
        
        # Draw Ball 1 (Blue)
        draw.ellipse(
            [x1-BALL_RADIUS, GROUND_Y-BALL_RADIUS,
             x1+BALL_RADIUS, GROUND_Y+BALL_RADIUS],
            fill="#1f77b4", outline="black"
        )
        # Draw Ball 2 (Red)
        draw.ellipse(
            [x2-BALL_RADIUS, GROUND_Y-BALL_RADIUS,
             x2+BALL_RADIUS, GROUND_Y+BALL_RADIUS],
            fill="#d62728", outline="black"
        )
        
        # Show updated canvas
        st.image(img, use_column_width=False)

    # --------------------------
    # Draw 3 Real-Time Plots
    # --------------------------
    with plot_placeholder:
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 4))
        
        # Velocity vs Time
        ax1.plot(st.session_state.t_list, st.session_state.v1_list, label="Ball 1", color="#1f77b4", linewidth=2)
        ax1.plot(st.session_state.t_list, st.session_state.v2_list, label="Ball 2", color="#d62728", linewidth=2)
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Velocity (m/s)")
        ax1.set_title("Velocity vs Time")
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_locator(MaxNLocator(5))

        # Kinetic Energy vs Time
        ax2.plot(st.session_state.t_list, st.session_state.ke1_list, label="Ball 1", color="#1f77b4", linewidth=2)
        ax2.plot(st.session_state.t_list, st.session_state.ke2_list, label="Ball 2", color="#d62728", linewidth=2)
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Kinetic Energy (J)")
        ax2.set_title("Kinetic Energy vs Time")
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_locator(MaxNLocator(5))

        # Momentum vs Time
        ax3.plot(st.session_state.t_list, st.session_state.p1_list, label="Ball 1", color="#1f77b4", linewidth=2)
        ax3.plot(st.session_state.t_list, st.session_state.p2_list, label="Ball 2", color="#d62728", linewidth=2)
        ax3.set_xlabel("Time (s)")
        ax3.set_ylabel("Momentum (kg·m/s)")
        ax3.set_title("Momentum vs Time")
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.xaxis.set_major_locator(MaxNLocator(5))

        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)

    # Small delay for smooth animation
    time.sleep(0.01)

# --------------------------
# Static Display When Paused/Reset
# --------------------------
if not st.session_state.running:
    # Static canvas
    with canvas_placeholder:
        img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), "white")
        draw = ImageDraw.Draw(img)
        draw.line([(0, GROUND_Y), (CANVAS_WIDTH, GROUND_Y)], fill="black", width=3)
        draw.ellipse([st.session_state.x1-BALL_RADIUS, GROUND_Y-BALL_RADIUS,
                      st.session_state.x1+BALL_RADIUS, GROUND_Y+BALL_RADIUS],
                     fill="#1f77b4", outline="black")
        draw.ellipse([st.session_state.x2-BALL_RADIUS, GROUND_Y-BALL_RADIUS,
                      st.session_state.x2+BALL_RADIUS, GROUND_Y+BALL_RADIUS],
                     fill="#d62728", outline="black")
        st.image(img, use_column_width=False)

    # Static plots
    with plot_placeholder:
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 4))
        ax1.plot(st.session_state.t_list, st.session_state.v1_list, label="Ball 1", color="#1f77b4", linewidth=2)
        ax1.plot(st.session_state.t_list, st.session_state.v2_list, label="Ball 2", color="#d62728", linewidth=2)
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Velocity (m/s)")
        ax1.set_title("Velocity vs Time")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        ax2.plot(st.session_state.t_list, st.session_state.ke1_list, label="Ball 1", color="#1f77b4", linewidth=2)
        ax2.plot(st.session_state.t_list, st.session_state.ke2_list, label="Ball 2", color="#d62728", linewidth=2)
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Kinetic Energy (J)")
        ax2.set_title("Kinetic Energy vs Time")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        ax3.plot(st.session_state.t_list, st.session_state.p1_list, label="Ball 1", color="#1f77b4", linewidth=2)
        ax3.plot(st.session_state.t_list, st.session_state.p2_list, label="Ball 2", color="#d62728", linewidth=2)
        ax3.set_xlabel("Time (s)")
        ax3.set_ylabel("Momentum (kg·m/s)")
        ax3.set_title("Momentum vs Time")
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
