import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="1D Head-On Collision Simulation")

# Session State Init
def reset_all():
    st.session_state.run = False
    st.session_state.t_list = [0.0]
    st.session_state.v1_data = []
    st.session_state.v2_data = []
    st.session_state.ke1_data = []
    st.session_state.ke2_data = []
    st.session_state.ke_total = []
    st.session_state.p1_data = []
    st.session_state.p2_data = []
    st.session_state.p_total = []
    st.session_state.pos1 = 100
    st.session_state.pos2 = 300

if "run" not in st.session_state:
    reset_all()

# Sidebar Parameter
with st.sidebar:
    st.header("Simulation Parameters")
    m1 = st.slider("Mass m1 (kg)", 0.5, 5.0, 1.0, 0.1)
    m2 = st.slider("Mass m2 (kg)", 0.5, 5.0, 1.0, 0.1)
    v1_init = st.slider("Initial Velocity v1 (m/s)", -5.0, 5.0, 3.0, 0.1)
    v2_init = st.slider("Initial Velocity v2 (m/s)", -5.0, 5.0, -1.0, 0.1)
    e = st.slider("Coefficient of Restitution e", 0.0, 1.0, 1.0, 0.01)
    dt = 0.02

# Top Control Button
col_btn1, col_btn2, col_btn3, col_info = st.columns([1,1,1,4])
with col_btn1:
    play = st.button("Play")
with col_btn2:
    pause = st.button("Pause")
with col_btn3:
    reset = st.button("Reset")

if play:
    st.session_state.run = True
if pause:
    st.session_state.run = False
if reset:
    reset_all()

# Initial Physical Data
ke1_0 = 0.5 * m1 * v1_init ** 2
ke2_0 = 0.5 * m2 * v2_init ** 2
total_ke0 = ke1_0 + ke2_0
p1_0 = m1 * v1_init
p2_0 = m2 * v2_init
total_p0 = p1_0 + p2_0

with col_info:
    st.info(f"Initial Total KE: {total_ke0:.2f} J | Initial Total Momentum: {total_p0:.2f} kg·m/s")

# Canvas Animation HTML
ball_html = """
<style>
.box{width:700px;height:120px;background:#f5f5f5;border:1px solid #ccc;position:relative;border-radius:8px;}
.ball1{width:40px;height:40px;border-radius:50%;background:#ff4444;position:absolute;top:40px;}
.ball2{width:40px;height:40px;border-radius:50%;background:#00cccc;position:absolute;top:40px;}
</style>
<div class="box">
    <div class="ball1" id="b1"></div>
    <div class="ball2" id="b2"></div>
</div>
<script>
let p1=%d,p2=%d;
document.getElementById("b1").style.left=p1+"px";
document.getElementById("b2").style.left=p2+"px";
</script>
"""
st.components.v1.html(ball_html % (st.session_state.pos1, st.session_state.pos2), height=150)

# Collision Calculation Function
def collision_calc(v1, v2, m1, m2, e):
    v1_new = ((m1 - e*m2)*v1 + (1+e)*m2*v2) / (m1 + m2)
    v2_new = ((m2 - e*m1)*v2 + (1+e)*m1*v1) / (m1 + m2)
    return v1_new, v2_new

# Simulation Logic
if st.session_state.run:
    v1, v2 = v1_init, v2_init
    pos1 = st.session_state.pos1
    pos2 = st.session_state.pos2

    # Collision judge
    if abs(pos1 - pos2) <= 40:
        v1, v2 = collision_calc(v1, v2, m1, m2, e)
        if pos1 > pos2:
            pos1 += 2
        else:
            pos2 -= 2

    # Boundary rebound
    if pos1 <= 0 or pos1 >= 660:
        v1 = -v1
    if pos2 <= 0 or pos2 >= 660:
        v2 = -v2

    pos1 += v1 * dt * 80
    pos2 += v2 * dt * 80

    st.session_state.pos1 = pos1
    st.session_state.pos2 = pos2

    # Record data
    now_t = st.session_state.t_list[-1] + dt
    st.session_state.t_list.append(now_t)
    st.session_state.v1_data.append(v1)
    st.session_state.v2_data.append(v2)

    ke1 = 0.5*m1*v1**2
    ke2 = 0.5*m2*v2**2
    st.session_state.ke1_data.append(ke1)
    st.session_state.ke2_data.append(ke2)
    st.session_state.ke_total.append(ke1+ke2)

    st.session_state.p1_data.append(m1*v1)
    st.session_state.p2_data.append(m2*v2)
    st.session_state.p_total.append(m1*v1+m2*v2)
    st.rerun()

# Draw Three Standard Charts with Scale
if len(st.session_state.t_list) > 2:
    c1, c2, c3 = st.columns(3)
    t = st.session_state.t_list

    # Velocity-Time
    with c1:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=t,y=st.session_state.v1_data,name="Ball1 Velocity",line=dict(color="red")))
        fig1.add_trace(go.Scatter(x=t,y=st.session_state.v2_data,name="Ball2 Velocity",line=dict(color="cyan")))
        fig1.update_layout(title="Velocity - Time Curve",xaxis_title="Time(s)",yaxis_title="Velocity(m/s)",xaxis=dict(showgrid=True),yaxis=dict(showgrid=True))
        st.plotly_chart(fig1,use_container_width=True)

    # Kinetic Energy-Time
    with c2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=t,y=st.session_state.ke1_data,name="Ball1 KE",line=dict(color="red")))
        fig2.add_trace(go.Scatter(x=t,y=st.session_state.ke2_data,name="Ball2 KE",line=dict(color="cyan")))
        fig2.add_trace(go.Scatter(x=t,y=st.session_state.ke_total,name="Total KE",line=dict(color="black",dash="dash")))
        fig2.update_layout(title="Kinetic Energy - Time Curve",xaxis_title="Time(s)",yaxis_title="Energy(J)",xaxis=dict(showgrid=True),yaxis=dict(showgrid=True))
        st.plotly_chart(fig2,use_container_width=True)

    # Momentum-Time
    with c3:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=t,y=st.session_state.p1_data,name="Ball1 Momentum",line=dict(color="red")))
        fig3.add_trace(go.Scatter(x=t,y=st.session_state.p2_data,name="Ball2 Momentum",line=dict(color="cyan")))
        fig3.add_trace(go.Scatter(x=t,y=st.session_state.p_total,name="Total Momentum",line=dict(color="black",dash="dash")))
        fig3.update_layout(title="Momentum - Time Curve",xaxis_title="Time(s)",yaxis_title="Momentum(kg·m/s)",xaxis=dict(showgrid=True),yaxis=dict(showgrid=True))
        st.plotly_chart(fig3,use_container_width=True)
