import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

# 页面配置
st.set_page_config(
    page_title="1D Perfectly Elastic Collision Simulation",
    layout="wide"
)

# 会话状态初始化
if "running" not in st.session_state:
    st.session_state.running = False
if "reset_flag" not in st.session_state:
    st.session_state.reset_flag = True
if "current_step" not in st.session_state:
    st.session_state.current_step = 0

# 标题
st.title("1D Perfectly Elastic Collision Dynamic Simulation")
st.subheader("Collision Classification by Velocity Direction")

# ========== 播放 / 暂停 / 重置 按钮 置顶 ==========
col_play, col_pause, col_reset = st.columns(3)
with col_play:
    btn_play = st.button("▶️ 播放", use_container_width=True)
with col_pause:
    btn_pause = st.button("⏸️ 暂停", use_container_width=True)
with col_reset:
    btn_reset = st.button("🔄 重置", use_container_width=True)

if btn_play:
    st.session_state.running = True
if btn_pause:
    st.session_state.running = False
if btn_reset:
    st.session_state.running = False
    st.session_state.reset_flag = True
    st.session_state.current_step = 0
    st.rerun()

# ========== 左侧展示区  右侧参数区 ==========
col_main, col_param = st.columns([3, 1])

with col_param:
    st.header("Parameter Settings")
    m1 = st.number_input("Mass of Ball1 (kg)", min_value=0.1, value=2.0, step=0.1)
    m2 = st.number_input("Mass of Ball2 (kg)", min_value=0.1, value=5.0, step=0.1)
    v1_initial = st.number_input("Initial Velocity Ball1 (m/s)", value=10.0, step=0.1)
    v2_initial = st.number_input("Initial Velocity Ball2 (m/s)", value=1.0, step=0.1)

# 碰撞公式 无缩进错误
v1_final = ((m1 - m2) * v1_initial + 2 * m2 * v2_initial) / (m1 + m2)
v2_final = ((m2 - m1) * v2_initial + 2 * m1 * v1_initial) / (m1 + m2)

with col_param:
    st.subheader("Post-Collision Velocity")
    st.write(f"Ball1 final: {v1_final:.2f} m/s")
    st.write(f"Ball2 final: {v2_final:.2f} m/s")

    p_initial = m1 * v1_initial + m2 * v2_initial
    p_final = m1 * v1_final + m2 * v2_final
    ke_initial = 0.5 * m1 * v1_initial**2 + 0.5 * m2 * v2_initial**2
    ke_final = 0.5 * m1 * v1_final**2 + 0.5 * m2 * v2_final**2

    st.subheader("Momentum & Kinetic Energy")
    st.write(f"Total initial momentum: {p_initial:.2f}")
    st.write(f"Total final momentum: {p_final:.2f}")
    st.write(f"Total initial energy: {ke_initial:.2f} J")
    st.write(f"Total final energy: {ke_final:.2f} J")

# ========== 仿真基础参数 ==========
t_total = 0.025
dt = 0.0005
t = np.arange(0, t_total, dt)
t_collision = t_total * 0.5

x1_start = 3.0
x2_start = 9.0

# 重置 / 改参数 重新生成全部数据
if st.session_state.reset_flag:
    x1 = np.zeros_like(t)
    x2 = np.zeros_like(t)
    v1 = np.zeros_like(t)
    v2 = np.zeros_like(t)
    p1 = np.zeros_like(t)
    p2 = np.zeros_like(t)
    ke1 = np.zeros_like(t)
    ke2 = np.zeros_like(t)

    for i, ti in enumerate(t):
        if ti < t_collision:
            x1[i] = x1_start + v1_initial * ti
            x2[i] = x2_start + v2_initial * ti
            v1[i] = v1_initial
            v2[i] = v2_initial
        else:
            delta_t = ti - t_collision
            x1[i] = x1_start + v1_initial * t_collision + v1_final * delta_t
            x2[i] = x2_start + v2_initial * t_collision + v2_final * delta_t
            v1[i] = v1_final
            v2[i] = v2_final

        p1[i] = m1 * v1[i]
        p2[i] = m2 * v2[i]
        ke1[i] = 0.5 * m1 * v1[i]**2
        ke2[i] = 0.5 * m2 * v2[i]**2

    st.session_state.x1 = x1
    st.session_state.x2 = x2
    st.session_state.v1 = v1
    st.session_state.v2 = v2
    st.session_state.p1 = p1
    st.session_state.p2 = p2
    st.session_state.ke1 = ke1
    st.session_state.ke2 = ke2
    st.session_state.t = t
    st.session_state.current_step = 0
    st.session_state.reset_flag = False

# 读取数据
x1 = st.session_state.x1
x2 = st.session_state.x2
v1 = st.session_state.v1
v2 = st.session_state.v2
p1 = st.session_state.p1
p2 = st.session_state.p2
ke1 = st.session_state.ke1
ke2 = st.session_state.ke2
t = st.session_state.t
current_step = st.session_state.current_step

# ========== 左侧画面 完全沿用你原来尺寸 ==========
with col_main:
    # 动画
    st.subheader("1D Dynamic Collision Animation")
    fig_anim, ax_anim = plt.subplots(figsize=(10, 3))
    ax_anim.set_xlim(0, 12)
    ax_anim.set_ylim(0, 2)
    ax_anim.set_yticks([])
    ax_anim.set_xlabel("Position (m)")
    ball1 = Circle((x1[current_step], 1.0), 0.3, color="#ff4b4b", label="Ball1")
    ball2 = Circle((x2[current_step], 1.0), 0.3, color="#4ecdc4", label="Ball2")
    ax_anim.add_patch(ball1)
    ax_anim.add_patch(ball2)
    ax_anim.legend()
    anim_placeholder = st.pyplot(fig_anim)

    # 动量-时间
    st.subheader("Momentum - Time")
    fig_p, ax_p = plt.subplots(figsize=(10, 3))
    ax_p.plot(t[:current_step+1], p1[:current_step+1], color="#ff4b4b", label="Ball1")
    ax_p.plot(t[:current_step+1], p2[:current_step+1], color="#4ecdc4", label="Ball2")
    ax_p.set_ylim(0, max(p1.max(), p2.max()) * 1.1)
    ax_p.set_xlabel("Time (s)")
    ax_p.set_ylabel("Momentum (kg·m/s)")
    ax_p.legend()
    p_placeholder = st.pyplot(fig_p)

    # 动能-时间
    st.subheader("Kinetic Energy - Time")
    fig_ke, ax_ke = plt.subplots(figsize=(10, 3))
    ax_ke.plot(t[:current_step+1], ke1[:current_step+1], color="#ff4b4b", label="Ball1")
    ax_ke.plot(t[:current_step+1], ke2[:current_step+1], color="#4ecdc4", label="Ball2")
    ax_ke.set_ylim(0, max(ke1.max(), ke2.max()) * 1.1)
    ax_ke.set_xlabel("Time (s)")
    ax_ke.set_ylabel("Kinetic Energy (J)")
    ax_ke.legend()
    ke_placeholder = st.pyplot(fig_ke)

    # 速度-时间
    st.subheader("Velocity - Time")
    fig_v, ax_v = plt.subplots(figsize=(10, 3))
    ax_v.plot(t[:current_step+1], v1[:current_step+1], color="#ff4b4b", label="Ball1")
    ax_v.plot(t[:current_step+1], v2[:current_step+1], color="#4ecdc4", label="Ball2")
    ax_v.set_xlabel("Time (s)")
    ax_v.set_ylabel("Velocity (m/s)")
    ax_v.legend()
    v_placeholder = st.pyplot(fig_v)

# ========== 流畅步进动画 不卡顿 ==========
if st.session_state.running:
    if current_step < len(t) - 1:
        st.session_state.current_step += 1
        st.rerun()
    else:
        st.session_state.running = False
