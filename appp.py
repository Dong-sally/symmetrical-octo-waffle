import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

st.set_page_config(page_title="1D Elastic Collision Dynamic Simulation", layout="wide")
plt.rcParams["axes.unicode_minus"] = False

st.title("🎱 1D Perfectly Elastic Collision Dynamic Simulation")
st.markdown("### Collision Classification by Velocity Direction")

# 左右布局
col_left, col_right = st.columns([2, 1])

# 右侧参数 可点加减号实时调
with col_right:
    st.subheader("⚙️ Parameter Settings")
    m1 = st.number_input("Mass of Ball1 (kg)", 0.1, 100.0, 2.0, 0.1)
    m2 = st.number_input("Mass of Ball2 (kg)", 0.1, 100.0, 5.0, 0.1)
    v1 = st.number_input("Initial Velocity Ball1 (m/s)", -20.0, 20.0, 8.0, 0.5)
    v2 = st.number_input("Initial Velocity Ball2 (m/s)", -20.0, 20.0, 1.0, 0.5)

    # 一维完全弹性碰撞公式
    v1f = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2)
    v2f = ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2)

    st.divider()
    st.success("Post-Collision Velocity")
    st.write(f"Ball1 final: {v1f:.2f} m/s")
    st.write(f"Ball2 final: {v2f:.2f} m/s")

    # 动量 动能
    p1i, p2i = m1 * v1, m2 * v2
    p1f, p2f = m1 * v1f, m2 * v2f
    e1i, e2i = 0.5 * m1 * v1**2, 0.5 * m2 * v2**2
    e1f, e2f = 0.5 * m1 * v1f**2, 0.5 * m2 * v2f**2

    st.info("Momentum & Kinetic Energy")
    st.write(f"Total initial momentum: {(p1i + p2i):.2f}")
    st.write(f"Total final momentum: {(p1f + p2f):.2f}")
    st.write(f"Total initial energy: {(e1i + e2i):.2f} J")
    st.write(f"Total final energy: {(e1f + e2f):.2f} J")

# 左侧：一维动态碰撞动画 + 四张实时曲线
with col_left:
    # -------- 1. 一维动态碰撞动画 --------
    fig_ani, ax_ani = plt.subplots(figsize=(10,2.5))
    ax_ani.set_xlim(0,12)
    ax_ani.set_ylim(0,2)
    ax_ani.set_xticks(np.arange(0,13,1))
    ax_ani.grid(True, alpha=0.3)
    ax_ani.set_title("1D Dynamic Collision Animation")

    ball1 = Circle((2,1), 0.25, color="#ff6b6b", label="Ball1")
    ball2 = Circle((9,1), 0.25, color="#4ecdc4", label="Ball2")
    ax_ani.add_patch(ball1)
    ax_ani.add_patch(ball2)
    ax_ani.legend()

    # 统一时间轴与路径点数量为100
    t = np.linspace(0, 3, 100)
    x1_path = np.zeros(100)
    x2_path = np.zeros(100)
    x1_now, x2_now = 2.0, 9.0
    collide_flag = False

    # 逐帧计算位置
    for i in range(100):
        if not collide_flag:
            x1_now += v1 * 0.03
            x2_now += v2 * 0.03
            if abs(x1_now - x2_now) < 0.6:
                collide_flag = True
        else:
            x1_now += v1f * 0.03
            x2_now += v2f * 0.03
        x1_path[i] = x1_now
        x2_path[i] = x2_now

    # 更新小球最终位置
    ball1.center = (x1_path[-1], 1)
    ball2.center = (x2_path[-1], 1)
    st.pyplot(fig_ani)

    # -------- 2. Position - Time Graph --------
    fig1, ax1 = plt.subplots(figsize=(7,2.8))
    ax1.plot(t, x1_path, label="Ball1", c="#ff6b6b")
    ax1.plot(t, x2_path, label="Ball2", c="#4ecdc4")
    ax1.set_title("Position - Time")
    ax1.set_xlabel("Time(s)")
    ax1.set_ylabel("Position(m)")
    ax1.grid(True)
    ax1.legend()
    st.pyplot(fig1)

    # -------- 3. Velocity - Time Graph --------
    v1_arr = np.where(t < 1.2, v1, v1f)
    v2_arr = np.where(t < 1.2, v2, v2f)
    fig2, ax2 = plt.subplots(figsize=(7,2.8))
    ax2.plot(t, v1_arr, label="Ball1", c="#ff6b6b")
    ax2.plot(t, v2_arr, label="Ball2", c="#4ecdc4")
    ax2.set_title("Velocity - Time")
    ax2.grid(True)
    ax2.legend()
    st.pyplot(fig2)

    # -------- 4. Momentum - Time Graph --------
    fig3, ax3 = plt.subplots(figsize=(7,2.8))
    ax3.plot(t, m1 * v1_arr, label="Ball1", c="#ff6b6b")
    ax3.plot(t, m2 * v2_arr, label="Ball2", c="#4ecdc4")
    ax3.set_title("Momentum - Time")
    ax3.grid(True)
    ax3.legend()
    st.pyplot(fig3)

    # -------- 5. Kinetic Energy - Time Graph --------
    fig4, ax4 = plt.subplots(figsize=(7,2.8))
    ax4.plot(t, 0.5 * m1 * v1_arr**2, label="Ball1", c="#ff6b6b")
    ax4.plot(t, 0.5 * m2 * v2_arr**2, label="Ball2", c="#4ecdc4")
    ax4.set_title("Kinetic Energy - Time")
    ax4.grid(True)
    ax4.legend()
    st.pyplot(fig4)

# 底部碰撞分类说明
st.divider()
st.subheader("Collision Classification (By Velocity Direction)")
st.markdown("""
1. Central Collision(Head-on):
1D motion, velocity along the line of sphere centers

2. Non-central Collision(Oblique):
2D deflection, velocity not on the center connecting line
""")
