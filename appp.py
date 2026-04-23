import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle

# 设置中文字体
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False

st.title("🎱 对心完全弹性碰撞仿真系统")
st.markdown("### 按照碰撞速度方向分类 · 物理动态仿真")

# =========== 左右布局：左侧仿真+图像，右侧参数控制面板 ===========
col_left, col_right = st.columns([2, 1])

with col_right:
    st.subheader("⚙️ 参数设置")
    m1 = st.slider("小球1质量 m1 (kg)", 1.0, 10.0, 2.0, 0.5)
    m2 = st.slider("小球2质量 m2 (kg)", 1.0, 10.0, 5.0, 0.5)
    v1 = st.slider("小球1初速度 v1 (m/s)", 1.0, 20.0, 10.0, 1.0)
    v2 = st.slider("小球2初速度 v2 (m/s)", -10.0, 10.0, 2.0, 1.0)

    # 完全弹性碰撞公式
    v1_final = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2)
    v2_final = ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2)

    st.divider()
    st.success("📌 碰撞后速度结果")
    st.write(f"小球1末速度：**{v1_final:.2f} m/s**")
    st.write(f"小球2末速度：**{v2_final:.2f} m/s**")

    # 动量、动能计算
    p1 = m1 * v1
    p2 = m2 * v2
    p_total = p1 + p2

    Ek1 = 0.5 * m1 * v1 **2
    Ek2 = 0.5 * m2 * v2** 2
    Ek_total = Ek1 + Ek2

    st.info("📊 初始物理量")
    st.write(f"系统总动量：**{p_total:.2f} kg·m/s**")
    st.write(f"系统总动能：**{Ek_total:.2f} J**")

# =========== 左侧：动画 + 四张带刻度物理图像 ===========
with col_left:
    # 1. 碰撞过程动画
    fig_ani, ax_ani = plt.subplots(figsize=(10, 3))
    ax_ani.set_xlim(0, 10)
    ax_ani.set_ylim(0, 2)
    ax_ani.set_xticks(np.arange(0, 11, 1))   # X轴刻度
    ax_ani.set_yticks(np.arange(0, 3, 0.5))  # Y轴刻度
    ax_ani.grid(True, alpha=0.3)
    ax_ani.set_title("小球对心完全弹性碰撞过程", fontsize=12)

    ball1 = Circle((2, 1), 0.3, color="#ff6b6b", label="小球1")
    ball2 = Circle((7, 1), 0.3, color="#4ecdc4", label="小球2")
    ax_ani.add_patch(ball1)
    ax_ani.add_patch(ball2)
    ax_ani.legend()

    st.pyplot(fig_ani)

    # 2. 位置-时间图像（带刻度+网格）
    fig1, ax1 = plt.subplots(figsize=(8, 3))
    t = np.linspace(0, 5, 100)
    x1 = v1 * t
    x2 = 7 + v2 * t
    ax1.plot(t, x1, label="小球1位置", c="#ff6b6b")
    ax1.plot(t, x2, label="小球2位置", c="#4ecdc4")
    ax1.set_title("位置 — 时间 图像")
    ax1.set_xlabel("时间 t (s)")
    ax1.set_ylabel("位置 x (m)")
    ax1.set_xticks(np.arange(0, 6, 0.5))
    ax1.set_yticks(np.arange(-20, 30, 5))
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    st.pyplot(fig1)

    # 3. 速度-时间图像
    fig2, ax2 = plt.subplots(figsize=(8, 3))
    v1_list = np.full_like(t, v1_final)
    v2_list = np.full_like(t, v2_final)
    ax2.plot(t, v1_list, label="小球1速度", c="#ff6b6b")
    ax2.plot(t, v2_list, label="小球2速度", c="#4ecdc4")
    ax2.set_title("速度 — 时间 图像")
    ax2.set_xlabel("时间 t (s)")
    ax2.set_ylabel("速度 v (m/s)")
    ax2.set_xticks(np.arange(0, 6, 0.5))
    ax2.set_yticks(np.arange(-10, 25, 2))
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    st.pyplot(fig2)

    # 4. 动量-时间图像
    fig3, ax3 = plt.subplots(figsize=(8, 3))
    p1_line = np.full_like(t, m1 * v1_final)
    p2_line = np.full_like(t, m2 * v2_final)
    ax3.plot(t, p1_line, label="小球1动量", c="#ff6b6b")
    ax3.plot(t, p2_line, label="小球2动量", c="#4ecdc4")
    ax3.set_title("动量 — 时间 图像")
    ax3.set_xlabel("时间 t (s)")
    ax3.set_ylabel("动量 p (kg·m/s)")
    ax3.set_xticks(np.arange(0, 6, 0.5))
    ax3.set_yticks(np.arange(-50, 60, 10))
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    st.pyplot(fig3)

    # 5. 动能-时间图像
    fig4, ax4 = plt.subplots(figsize=(8, 3))
    ek1_line = np.full_like(t, 0.5*m1*v1_final**2)
    ek2_line = np.full_like(t, 0.5*m2*v2_final**2)
    ax4.plot(t, ek1_line, label="小球1动能", c="#ff6b6b")
    ax4.plot(t, ek2_line, label="小球2动能", c="#4ecdc4")
    ax4.set_title("动能 — 时间 图像")
    ax4.set_xlabel("时间 t (s)")
    ax4.set_ylabel("动能 Ek (J)")
    ax4.set_xticks(np.arange(0, 6, 0.5))
    ax4.set_yticks(np.arange(0, 60, 5))
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    st.pyplot(fig4)

# =========== 碰撞分类说明：按速度方向划分 ===========
st.divider()
st.subheader("📚 碰撞两大分类体系（按速度方向划分）")
st.markdown("""
1. **对心碰撞（正碰）**
- 两球速度方向在两球球心连线上
- 碰撞后速度仍在同一直线，一维运动

2. **非对心碰撞（斜碰）**
- 初速度不在球心连线上
- 碰撞后速度发生偏转，二维平面运动

> 本仿真演示：**一维 · 对心完全弹性碰撞**
""")
