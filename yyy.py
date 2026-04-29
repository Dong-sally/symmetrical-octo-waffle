import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Circle

# 页面配置
st.set_page_config(
    page_title="1D Perfectly Elastic Collision Simulation",
    layout="wide"
)

# 标题
st.title("1D Perfectly Elastic Collision Dynamic Simulation")
st.subheader("Collision Classification by Velocity Direction")

# 分栏布局：左侧仿真区，右侧参数设置
col_main, col_param = st.columns([3, 1])

with col_param:
    st.header("Parameter Settings")
    # 参数输入
    m1 = st.number_input("Mass of Ball1 (kg)", min_value=0.1, value=2.0, step=0.1)
    m2 = st.number_input("Mass of Ball2 (kg)", min_value=0.1, value=5.0, step=0.1)
    v1_initial = st.number_input("Initial Velocity Ball1 (m/s)", value=10.0, step=0.1)
    v2_initial = st.number_input("Initial Velocity Ball2 (m/s)", value=1.0, step=0.1)

    # 完全弹性碰撞速度公式
    v1_final = ((m1 - m2) * v1_initial + 2 * m2 * v2_initial) / (m1 + m2)
    v2_final = ((m2 - m1) * v2_initial + 2 * m1 * v1_initial) / (m1 + m2)

    # 碰撞结果显示
    st.subheader("Post-Collision Velocity")
    st.write(f"Ball1 final: {v1_final:.2f} m/s")
    st.write(f"Ball2 final: {v2_final:.2f} m/s")

    # 动量与动能守恒验证
    p_initial = m1 * v1_initial + m2 * v2_initial
    p_final = m1 * v1_final + m2 * v2_final
    ke_initial = 0.5 * m1 * v1_initial**2 + 0.5 * m2 * v2_initial**2
    ke_final = 0.5 * m1 * v1_final**2 + 0.5 * m2 * v2_final**2

    st.subheader("Momentum & Kinetic Energy")
    st.write(f"Total initial momentum: {p_initial:.2f}")
    st.write(f"Total final momentum: {p_final:.2f}")
    st.write(f"Total initial energy: {ke_initial:.2f} J")
    st.write(f"Total final energy: {ke_final:.2f} J")

with col_main:
    # 仿真时间设置（和你截图的x轴完全匹配）
    t_total = 0.025
    dt = 0.0005
    t = np.arange(0, t_total, dt)
    t_collision = t_total * 0.5  # 碰撞发生在中间时刻

    # 初始化数组
    x1 = np.zeros_like(t)
    x2 = np.zeros_like(t)
    v1 = np.zeros_like(t)
    v2 = np.zeros_like(t)
    p1 = np.zeros_like(t)
    p2 = np.zeros_like(t)
    ke1 = np.zeros_like(t)
    ke2 = np.zeros_like(t)

    # 初始位置（避免重叠）
    x1_start = 3.0
    x2_start = 9.0

    # 填充数据
    for i, ti in enumerate(t):
        if ti < t_collision:
            # 碰撞前
            x1[i] = x1_start + v1_initial * ti
            x2[i] = x2_start + v2_initial * ti
            v1[i] = v1_initial
            v2[i] = v2_initial
        else:
            # 碰撞后
            delta_t = ti - t_collision
            x1[i] = x1_start + v1_initial * t_collision + v1_final * delta_t
            x2[i] = x2_start + v2_initial * t_collision + v2_final * delta_t
            v1[i] = v1_final
            v2[i] = v2_final
        # 动量、动能
        p1[i] = m1 * v1[i]
        p2[i] = m2 * v2[i]
        ke1[i] = 0.5 * m1 * v1[i]**2
        ke2[i] = 0.5 * m2 * v2[i]**2

    # 1. 动态碰撞动画
    st.subheader("1D Dynamic Collision Animation")
    fig_anim, ax_anim = plt.subplots(figsize=(10, 3))
    ax_anim.set_xlim(0, 12)
    ax_anim.set_ylim(0, 2)
    ax_anim.set_yticks([])
    ax_anim.set_xlabel("Position (m)")
    ball1 = Circle((x1[0], 1.0), 0.3, color="#ff4b4b", label="Ball1")
    ball2 = Circle((x2[0], 1.0), 0.3, color="#4ecdc4", label="Ball2")
    ax_anim.add_patch(ball1)
    ax_anim.add_patch(ball2)
    ax_anim.legend()
    st.pyplot(fig_anim)

    # 2. 动量-时间图
    st.subheader("Momentum - Time")
    fig_p, ax_p = plt.subplots(figsize=(10, 3))
    ax_p.plot(t, p1, color="#ff4b4b", label="Ball1")
    ax_p.plot(t, p2, color="#4ecdc4", label="Ball2")
    ax_p.set_ylim(0, max(p1.max(), p2.max()) * 1.1)
    ax_p.set_xlabel("Time (s)")
    ax_p.set_ylabel("Momentum (kg·m/s)")
    ax_p.legend()
    st.pyplot(fig_p)

    # 3. 动能-时间图
    st.subheader("Kinetic Energy - Time")
    fig_ke, ax_ke = plt.subplots(figsize=(10, 3))
    ax_ke.plot(t, ke1, color="#ff4b4b", label="Ball1")
    ax_ke.plot(t, ke2, color="#4ecdc4", label="Ball2")
    ax_ke.set_ylim(0, max(ke1.max(), ke2.max()) * 1.1)
    ax_ke.set_xlabel("Time (s)")
    ax_ke.set_ylabel("Kinetic Energy (J)")
    ax_ke.legend()
    st.pyplot(fig_ke)

    # 4. 速度-时间图
    st.subheader("Velocity - Time")
    fig_v, ax_v = plt.subplots(figsize=(10, 3))
    ax_v.plot(t, v1, color="#ff4b4b", label="Ball1")
    ax_v.plot(t, v2, color="#4ecdc4", label="Ball2")
    ax_v.set_xlabel("Time (s)")
    ax_v.set_ylabel("Velocity (m/s)")
    ax_v.legend()
    st.pyplot(fig_v)

    # 5. 位置-时间图
    st.subheader("Position - Time")
    fig_x, ax_x = plt.subplots(figsize=(10, 3))
    ax_x.plot(t, x1, color="#ff4b4b", label="Ball1")
    ax_x.plot(t, x2, color="#4ecdc4", label="Ball2")
    ax_x.set_xlabel("Time (s)")
    ax_x.set_ylabel("Position (m)")
    ax_x.legend()
    st.pyplot(fig_x).
