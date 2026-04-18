import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import io

# 配置中文字体（解决乱码）
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(layout="wide", page_title="对心完全弹性碰撞仿真")
st.title("对心完全弹性碰撞仿真")

# 1. 初始化会话状态
if "frame" not in st.session_state:
    st.session_state.frame = 0
if "running" not in st.session_state:
    st.session_state.running = False
if "last_params" not in st.session_state:
    st.session_state.last_params = (1.0, 2.0, 2.0, -1.0)

# 2. 参数滑块（和截图完全一致）
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

# 3. 重置按钮
if st.button("重置仿真"):
    st.session_state.frame = 0
    st.session_state.running = False
    st.session_state.last_params = (m1, m2, v1, v2)
    st.rerun()

# 4. 物理仿真计算
r = 0.2  # 物体半径
dt = 0.01  # 时间步长
t_total = 5.0  # 总仿真时间
steps = int(t_total / dt)

def simulate(m1, m2, v1, v2):
    x1, x2 = 4.0, 5.5  # 初始位置
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

        # 完全弹性碰撞
        if abs(x1 - x2) <= 2 * r:
            new_v1 = ((m1 - m2) * vv1 + 2 * m2 * vv2) / (m1 + m2)
            new_v2 = ((m2 - m1) * vv2 + 2 * m1 * vv1) / (m1 + m2)
            vv1, vv2 = new_v1, new_v2

    return x1_list, x2_list, v1_list, v2_list

# 仅当参数变化或重置时重新计算数据
current_params = (m1, m2, v1, v2)
if current_params != st.session_state.last_params:
    st.session_state.last_params = current_params
    st.session_state.frame = 0
    st.session_state.x1, st.session_state.x2, st.session_state.v1_arr, st.session_state.v2_arr = simulate(m1, m2, v1, v2)
else:
    if "x1" not in st.session_state:
        st.session_state.x1, st.session_state.x2, st.session_state.v1_arr, st.session_state.v2_arr = simulate(m1, m2, v1, v2)

# 5. 绘制图像（和截图完全一致）
fig, (ax_sim, ax_plot) = plt.subplots(1, 2, figsize=(12, 6))

# 左侧：碰撞仿真场景
ax_sim.set_title("对心完全弹性碰撞仿真")
ax_sim.set_xlabel("位置 x (m)")
ax_sim.set_xlim(-1, 6)
ax_sim.set_ylim(-1, 1)
ax_sim.grid(True, alpha=0.3)

# 绘制当前帧物体
f = st.session_state.frame
ax_sim.scatter(st.session_state.x1[f], 0, color="red", s=150, label="物体1")
ax_sim.scatter(st.session_state.x2[f], 0, color="blue", s=150, label="物体2")
ax_sim.legend()

# 右侧：速度-时间曲线
ax_plot.set_title("速度-时间曲线")
ax_plot.set_xlabel("时间 t (s)")
ax_plot.set_ylabel("速度 v (m/s)")
ax_plot.set_xlim(0, t_total)
ax_plot.set_ylim(-4, 4)
ax_plot.grid(True, alpha=0.3)

t_arr = np.linspace(0, t_total, steps)
ax_plot.plot(t_arr, st.session_state.v1_arr, "r-", label="物体1速度")
ax_plot.plot(t_arr, st.session_state.v2_arr, "b-", label="物体2速度")
ax_plot.scatter(t_arr[f], st.session_state.v1_arr[f], color="red", s=30)
ax_plot.scatter(t_arr[f], st.session_state.v2_arr[f], color="blue", s=30)
ax_plot.legend()

# 显示图像
st.pyplot(fig)

# 自动播放控制
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("▶ 播放"):
        st.session_state.running = True
with col_btn2:
    if st.button("⏸ 暂停"):
        st.session_state.running = False

if st.session_state.running:
    st.session_state.frame += 1
    if st.session_state.frame >= steps:
        st.session_state.frame = 0
    st.rerun()
