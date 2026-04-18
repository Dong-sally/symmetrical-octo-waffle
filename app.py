import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 只使用云端自带字体，全程英文，彻底杜绝乱码
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

st.set_page_config(layout="wide", page_title="Elastic Collision Simulation")
st.title("Elastic Collision Simulation")

# 状态初始化
if "frame" not in st.session_state:
    st.session_state.frame = 0
if "running" not in st.session_state:
    st.session_state.running = False
if "data" not in st.session_state:
    st.session_state.data = None

# 1. 参数滑块（和你截图布局一致）
col1, col2 = st.columns(2)
with col1:
    m1 = st.slider("m1 (kg)", 0.1, 5.0, 1.0, 0.1)
with col2:
    m2 = st.slider("m2 (kg)", 0.1, 5.0, 2.0, 0.1)

col3, col4 = st.columns(2)
with col3:
    v1 = st.slider("v1 (m/s)", -3.0, 3.0, 2.0, 0.1)
with col4:
    v2 = st.slider("v2 (m/s)", -3.0, 3.0, -1.0, 0.1)

# 重置按钮
if st.button("Reset Simulation"):
    st.session_state.frame = 0
    st.session_state.running = False
    st.session_state.data = None
    st.rerun()

# 2. 物理仿真（只在参数变化时计算一次，避免重复计算卡顿）
@st.cache_data
def run_simulation(m1, m2, v1, v2):
    r = 0.2
    dt = 0.01
    t_total = 5.0
    steps = int(t_total / dt)
    
    x1, x2 = 4.0, 5.5
    vv1, vv2 = v1, v2
    x1_list = np.zeros(steps)
    x2_list = np.zeros(steps)
    v1_list = np.zeros(steps)
    v2_list = np.zeros(steps)

    for i in range(steps):
        x1_list[i] = x1
        x2_list[i] = x2
        v1_list[i] = vv1
        v2_list[i] = vv2

        x1 += vv1 * dt
        x2 += vv2 * dt

        if abs(x1 - x2) <= 2 * r:
            new_v1 = ((m1 - m2) * vv1 + 2 * m2 * vv2) / (m1 + m2)
            new_v2 = ((m2 - m1) * vv2 + 2 * m1 * vv1) / (m1 + m2)
            vv1, vv2 = new_v1, new_v2

    return x1_list, x2_list, v1_list, v2_list, t_total, steps

# 加载数据
if st.session_state.data is None or st.session_state.data[:4] != (m1, m2, v1, v2):
    x1_arr, x2_arr, v1_arr, v2_arr, t_total, steps = run_simulation(m1, m2, v1, v2)
    st.session_state.data = (m1, m2, v1, v2, x1_arr, x2_arr, v1_arr, v2_arr, t_total, steps)
else:
    _, _, _, _, x1_arr, x2_arr, v1_arr, v2_arr, t_total, steps = st.session_state.data

# 3. 绘图（和你截图布局1:1还原）
fig, (ax_sim, ax_plot) = plt.subplots(1, 2, figsize=(12, 6))

# 左侧碰撞场景
ax_sim.set_title("Collision Scene")
ax_sim.set_xlabel("Position x (m)")
ax_sim.set_xlim(-1, 6)
ax_sim.set_ylim(-1, 1)
ax_sim.grid(True, alpha=0.3)

# 绘制当前帧
f = st.session_state.frame
ax_sim.scatter(x1_arr[f], 0, color="red", s=150, label="Object 1")
ax_sim.scatter(x2_arr[f], 0, color="blue", s=150, label="Object 2")
ax_sim.legend()

# 右侧速度-时间曲线
ax_plot.set_title("Velocity-Time Curve")
ax_plot.set_xlabel("Time t (s)")
ax_plot.set_ylabel("Velocity v (m/s)")
ax_plot.set_xlim(0, t_total)
ax_plot.set_ylim(-4, 4)
ax_plot.grid(True, alpha=0.3)

t_arr = np.linspace(0, t_total, steps)
ax_plot.plot(t_arr, v1_arr, "r-", label="Object 1 Velocity")
ax_plot.plot(t_arr, v2_arr, "b-", label="Object 2 Velocity")
ax_plot.scatter(t_arr[f], v1_arr[f], color="red", s=30)
ax_plot.scatter(t_arr[f], v2_arr[f], color="blue", s=30)
ax_plot.legend()

st.pyplot(fig)

# 播放/暂停控制
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("▶ Play"):
        st.session_state.running = True
with col_btn2:
    if st.button("⏸ Pause"):
        st.session_state.running = False

# 自动播放逻辑（放慢刷新频率，解决掉帧）
if st.session_state.running:
    st.session_state.frame += 1
    if st.session_state.frame >= steps:
        st.session_state.frame = 0
    # 降低刷新频率，减少卡顿
    import time
    time.sleep(0.02)
    st.rerun()
