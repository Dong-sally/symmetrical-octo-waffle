import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --------------------------
# 1. 固定中文乱码问题（Streamlit云端兼容）
# --------------------------
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False

# --------------------------
# 2. 初始化会话状态（解决只动一下的问题）
# --------------------------
if "frame" not in st.session_state:
    st.session_state.frame = 0
if "is_playing" not in st.session_state:
    st.session_state.is_playing = False

# --------------------------
# 3. 页面布局与参数设置
# --------------------------
st.set_page_config(page_title="弹性碰撞仿真", layout="wide")
st.title("完全弹性碰撞仿真实验")

col_params = st.columns(4)
with col_params[0]:
    m1 = st.slider("物体1质量(kg)", 0.1, 5.0, 1.0, 0.1)
with col_params[1]:
    v1 = st.slider("物体1初速度(m/s)", -5.0, 5.0, 3.0, 0.1)
with col_params[2]:
    m2 = st.slider("物体2质量(kg)", 0.1, 5.0, 2.0, 0.1)
with col_params[3]:
    v2 = st.slider("物体2初速度(m/s)", -5.0, 5.0, -1.0, 0.1)

# 固定物理参数
r = 0.3
dt = 0.05
t_total = 6
steps = int(t_total / dt)

# --------------------------
# 4. 预计算碰撞全过程数据（云端性能友好）
# --------------------------
@st.cache_data
def simulate(m1, m2, v1, v2, r, dt, steps):
    x1, x2 = 0.0, 3.2
    x1_list = np.zeros(steps)
    x2_list = np.zeros(steps)
    v1_list = np.zeros(steps)
    v2_list = np.zeros(steps)

    x1_list[0] = x1
    x2_list[0] = x2
    v1_list[0] = v1
    v2_list[0] = v2

    for i in range(1, steps):
        x1 += v1 * dt
        x2 += v2 * dt

        # 完全弹性碰撞公式
        if abs(x1 - x2) <= 2 * r:
            nv1 = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2)
            nv2 = ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2)
            v1, v2 = nv1, nv2

        x1_list[i] = x1
        x2_list[i] = x2
        v1_list[i] = v1
        v2_list[i] = v2

    return x1_list, x2_list, v1_list, v2_list

x1_arr, x2_arr, v1_arr, v2_arr = simulate(m1, m2, v1, v2, r, dt, steps)
t_arr = np.linspace(0, t_total, steps)

# --------------------------
# 5. 控制按钮（播放/暂停/重置）
# --------------------------
col_btn = st.columns(3)
with col_btn[0]:
    if st.button("▶ 播放", use_container_width=True):
        st.session_state.is_playing = True
with col_btn[1]:
    if st.button("⏸ 暂停", use_container_width=True):
        st.session_state.is_playing = False
with col_btn[2]:
    if st.button("🔄 重置", use_container_width=True):
        st.session_state.is_playing = False
        st.session_state.frame = 0

# 自动更新帧数（播放状态下）
if st.session_state.is_playing:
    st.session_state.frame += 1
    if st.session_state.frame >= steps:
        st.session_state.frame = 0

# --------------------------
# 6. 绘制当前帧（全中文显示）
# --------------------------
current_frame = st.session_state.frame

fig, (ax_sim, ax_plot) = plt.subplots(1, 2, figsize=(12, 5))

# 碰撞仿真场景
ax_sim.set_xlim(-1, 10)
ax_sim.set_ylim(-1, 1)
ax_sim.set_title("碰撞过程仿真", fontsize=14)
ax_sim.set_xlabel("位置（米）")
ax_sim.set_ylabel("竖直方向")
ax_sim.scatter(x1_arr[current_frame], 0, color="red", s=150, label="物体1")
ax_sim.scatter(x2_arr[current_frame], 0, color="blue", s=150, label="物体2")
ax_sim.legend()
ax_sim.grid(True, alpha=0.3)

# 速度-时间曲线
ax_plot.set_title("速度-时间变化曲线", fontsize=14)
ax_plot.set_xlabel("时间（秒）")
ax_plot.set_ylabel("速度（m/s）")
ax_plot.plot(t_arr, v1_arr, "r-", label="物体1速度")
ax_plot.plot(t_arr, v2_arr, "b-", label="物体2速度")
ax_plot.scatter(t_arr[current_frame], v1_arr[current_frame], color="red", s=30)
ax_plot.scatter(t_arr[current_frame], v2_arr[current_frame], color="blue", s=30)
ax_plot.legend()
ax_plot.grid(True, alpha=0.3)

st.pyplot(fig, use_container_width=True)

# 播放状态下自动刷新（官方推荐方式）
if st.session_state.is_playing:
    st.rerun()
