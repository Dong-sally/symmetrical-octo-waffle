import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

# 页面配置
st.set_page_config(page_title="1D Elastic Collision Dynamic Simulation", layout="wide")
plt.rcParams["axes.unicode_minus"] = False

# 状态记忆：播放、暂停、重置
if "is_play" not in st.session_state:
    st.session_state.is_play = False
if "frame_idx" not in st.session_state:
    st.session_state.frame_idx = 0

st.title("🎱 1D Perfectly Elastic Collision Dynamic Simulation")
st.markdown("### Collision Classification by Velocity Direction")

# 左右布局【完全保留你原来排版，不改动】
col_left, col_right = st.columns([2, 1])

# 右侧 参数 + 按钮
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
    # 播放 暂停 重置 三个按钮
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("▶️ Play"):
            st.session_state.is_play = True
    with b2:
        if st.button("⏸️ Pause"):
            st.session_state.is_play = False
    with b3:
        if st.button("🔄 Reset"):
            st.session_state.is_play = False
            st.session_state.frame_idx = 0

    st.divider()
    st.success("Post-Collision Velocity")
    st.write(f"Ball1 final: {v1f:.2f} m/s")
    st.write(f"Ball2 final: {v2f:.2f} m/s")

    # 动量、动能
    p1i, p2i = m1 * v1, m2 * v2
    p1f, p2f = m1 * v1f, m2 * v2f
    e1i, e2i = 0.5 * m1 * v1**2, 0.5 * m2 * v2**2
    e1f, e2f = 0.5 * m1 * v1f**2, 0.5 * m2 * v2f**2

    st.info("Momentum & Kinetic Energy")
    st.write(f"Total initial momentum: {(p1i + p2i):.2f}")
    st.write(f"Total final momentum: {(p1f + p2f):.2f}")
    st.write(f"Total initial energy: {(e1i + e2i):.2f} J")
    st.write(f"Total final energy: {(e1f + e2f):.2f} J")

# 左侧：一维动态动画 + 四张曲线图【排版原样不动】
with col_left:
    # 时间总长、总帧数
    total_frame = 120
    t_arr = np.linspace(0, 4, total_frame)

    # 预计算小球全程位置
    x1_list = np.zeros(total_frame)
    x2_list = np.zeros(total_frame)
    x1, x2 = 2.0, 9.0
    hit = False

    for i in range(total_frame):
        if not hit:
            x1 += v1 * 0.03
            x2 += v2 * 0.03
            if abs(x1 - x2) < 0.55:
                hit = True
        else:
            x1 += v1f * 0.03
            x2 += v2f * 0.03
        x1_list[i] = x1
        x2_list[i] = x2

    # 动态帧索引递增实现动画
    if st.session_state.is_play:
        st.session_state.frame_idx += 1
    if st.session_state.frame_idx >= total_frame:
        st.session_state.frame_idx = total_frame - 1

    cur_idx = st.session_state.frame_idx

    # 1. 一维碰撞动态画面
    fig_ani, ax_ani = plt.subplots(figsize=(10, 2.5))
    ax_ani.set_xlim(0, 12)
    ax_ani.set_ylim(0, 2)
    ax_ani.set_xticks(np.arange(0, 13, 1))
    ax_ani.grid(True, alpha=0.3)
    ax_ani.set_title("1D Dynamic Collision Animation")

    ball1 = Circle((x1_list[cur_idx], 1), 0.25, color="#ff6b6b", label="Ball1")
    ball2 = Circle((x2_list[cur_idx], 1), 0.25, color="#4ecdc4", label="Ball2")
    ax_ani.add_patch(ball1)
    ax_ani.add_patch(ball2)
    ax_ani.legend()
    st.pyplot(fig_ani)

    # 2. 位置-时间
    fig1, ax1 = plt.subplots(figsize=(7, 2.8))
    ax1.plot(t_arr[:cur_idx+1], x1_list[:cur_idx+1], c="#ff6b6b", label="Ball1")
    ax1.plot(t_arr[:cur_idx+1], x2_list[:cur_idx+1], c="#4ecdc4", label="Ball2")
    ax1.set_title("Position - Time")
    ax1.grid(True)
    ax1.legend()
    st.pyplot(fig1)

    # 3. 速度-时间
    v1_line = np.where(t_arr < 1.3, v1, v1f)
    v2_line = np.where(t_arr < 1.3, v2, v2f)
    fig2, ax2 = plt.subplots(figsize=(7, 2.8))
    ax2.plot(t_arr[:cur_idx+1], v1_line[:cur_idx+1], c="#ff6b6b", label="Ball1")
    ax2.plot(t_arr[:cur_idx+1], v2_line[:cur_idx+1], c="#4ecdc4", label="Ball2")
    ax2.set_title("Velocity - Time")
    ax2.grid(True)
    ax2.legend()
    st.pyplot(fig2)

    # 4. 动量-时间
    fig3, ax3 = plt.subplots(figsize=(7, 2.8))
    ax3.plot(t_arr[:cur_idx+1], m1*v1_line[:cur_idx+1], c="#ff6b6b", label="Ball1")
    ax3.plot(t_arr[:cur_idx+1], m2*v2_line[:cur_idx+1], c="#4ecdc4", label="Ball2")
    ax3.set_title("Momentum - Time")
    ax3.grid(True)
    ax3.legend()
    st.pyplot(fig3)

    # 5. 动能-时间
    fig4, ax4 = plt.subplots(figsize=(7, 2.8))
    ax4.plot(t_arr[:cur_idx+1], 0.5*m1*v1_line[:cur_idx+1]**2, c="#ff6b6b", label="Ball1")
    ax4.plot(t_arr[:cur_idx+1], 0.5*m2*v2_line[:cur_idx+1]**2, c="#4ecdc4", label="Ball2")
    ax4.set_title("Kinetic Energy - Time")
    ax4.grid(True)
    ax4.legend()
    st.pyplot(fig4)

# 底部碰撞分类
st.divider()
st.subheader("Collision Classification (By Velocity Direction)")
st.markdown("""
1. Central Collision(Head-on):
1D motion, velocity along the line of sphere centers

2. Non-central Collision(Oblique):
2D deflection, velocity not on the center connecting line
""")
