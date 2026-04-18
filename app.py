import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --------------------------
# 1. 修复字体问题（Streamlit 云端兼容）
# --------------------------
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# --------------------------
# 2. 用 Streamlit 控件替代本地滑块
# --------------------------
st.title("完全弹性碰撞仿真")

# 物理参数初始化（用滑块让用户可调整）
m1_0 = st.slider("物体1初始质量 (kg)", 0.1, 5.0, 1.0, 0.1)
m2_0 = st.slider("物体2初始质量 (kg)", 0.1, 5.0, 2.0, 0.1)
v1_0 = st.slider("物体1初始速度 (m/s)", -5.0, 5.0, 3.0, 0.1)
v2_0 = st.slider("物体2初始速度 (m/s)", -5.0, 5.0, -1.0, 0.1)

# 固定参数
r = 0.3      # 物体半径 (m)
dt = 0.01    # 时间步长 (s)
t_total = 5  # 总仿真时间 (s)

# --------------------------
# 3. 碰撞仿真逻辑
# --------------------------
def simulate_collision(m1, m2, v1, v2, r, dt, t_total):
    steps = int(t_total / dt)
    t_list = np.linspace(0, t_total, steps)
    x1_list = np.zeros(steps)
    x2_list = np.zeros(steps)
    v1_list = np.zeros(steps)
    v2_list = np.zeros(steps)
    
    x1 = 0.0
    x2 = 3.0
    x1_list[0] = x1
    x2_list[0] = x2
    v1_list[0] = v1
    v2_list[0] = v2

    for i in range(1, steps):
        # 位置更新
        x1 += v1 * dt
        x2 += v2 * dt
        
        # 碰撞检测与速度更新（完全弹性碰撞）
        if abs(x1 - x2) <= 2 * r:
            v1_new = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2)
            v2_new = ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2)
            v1, v2 = v1_new, v2_new
        
        x1_list[i] = x1
        x2_list[i] = x2
        v1_list[i] = v1
        v2_list[i] = v2

    return t_list, x1_list, x2_list, v1_list, v2_list

t_list, x1_list, x2_list, v1_list, v2_list = simulate_collision(m1_0, m2_0, v1_0, v2_0, r, dt, t_total)

# --------------------------
# 4. 绘图（用 Streamlit 方式显示）
# --------------------------
fig = plt.figure(figsize=(12, 6))

# 仿真画面
ax_sim = fig.add_subplot(121)
ax_sim.set_xlim(-1, 10)
ax_sim.set_ylim(-1, 1)
ax_sim.set_title("碰撞仿真")
ax_sim.set_xlabel("位置 (m)")
ax_sim.set_ylabel("Y轴")

# 初始绘制物体
obj1, = ax_sim.plot(x1_list[0], 0, 'ro', markersize=10, label='物体1')
obj2, = ax_sim.plot(x2_list[0], 0, 'bo', markersize=10, label='物体2')
ax_sim.legend()

# 速度-时间曲线
ax_plot = fig.add_subplot(122)
ax_plot.plot(t_list, v1_list, 'r-', label='物体1速度')
ax_plot.plot(t_list, v2_list, 'b-', label='物体2速度')
ax_plot.set_title("速度-时间曲线")
ax_plot.set_xlabel("时间 (s)")
ax_plot.set_ylabel("速度 (m/s)")
ax_plot.legend()

# 关键：用 st.pyplot 显示图表，替代本地 plt.show()
st.pyplot(fig)
