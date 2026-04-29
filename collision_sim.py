import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import time

# -------------------------- 页面配置 --------------------------
st.set_page_config(page_title="二维弹性碰撞仿真", layout="wide")
st.title("二维完全弹性碰撞仿真（连续动态）")

# -------------------------- 侧边栏参数设置 --------------------------
st.sidebar.header("⚙️ 两球参数设置")
col1, col2 = st.sidebar.columns(2)

# 球1参数
with col1:
    st.subheader("球 1 (蓝色)")
    m1 = st.number_input("质量 m₁ (kg)", min_value=0.1, max_value=5.0, value=0.5, step=0.1)
    v1x = st.number_input("初速度 v₁ₓ (m/s)", min_value=-5.0, max_value=5.0, value=0.45, step=0.1)
    v1y = st.number_input("初速度 v₁ᵧ (m/s)", min_value=-5.0, max_value=5.0, value=0.34, step=0.1)
    x1 = st.number_input("初始位置 x₁ (m)", min_value=-1.0, max_value=1.0, value=-0.13, step=0.01)
    y1 = st.number_input("初始位置 y₁ (m)", min_value=-1.0, max_value=1.0, value=-0.10, step=0.01)

# 球2参数
with col2:
    st.subheader("球 2 (粉色)")
    m2 = st.number_input("质量 m₂ (kg)", min_value=0.1, max_value=5.0, value=1.5, step=0.1)
    v2x = st.number_input("初速度 v₂ₓ (m/s)", min_value=-5.0, max_value=5.0, value=-0.87, step=0.1)
    v2y = st.number_input("初速度 v₂ᵧ (m/s)", min_value=-5.0, max_value=5.0, value=0.04, step=0.1)
    x2 = st.number_input("初始位置 x₂ (m)", min_value=-1.0, max_value=1.0, value=0.61, step=0.01)
    y2 = st.number_input("初始位置 y₂ (m)", min_value=-1.0, max_value=1.0, value=-0.06, step=0.01)

# 仿真控制
st.sidebar.header("🎮 仿真控制")
dt = st.sidebar.slider("时间步长 dt (s)", min_value=0.001, max_value=0.01, value=0.005, step=0.001)
max_time = st.sidebar.slider("仿真总时长 (s)", min_value=5, max_value=30, value=15, step=1)

# -------------------------- 物理仿真核心类 --------------------------
class CollisionSimulation:
    def __init__(self, m1, m2, x1, y1, v1x, v1y, x2, y2, v2x, v2y, dt):
        self.m1 = m1
        self.m2 = m2
        self.x1 = x1
        self.y1 = y1
        self.v1x = v1x
        self.v1y = v1y
        self.x2 = x2
        self.y2 = y2
        self.v2x = v2x
        self.v2y = v2y
        self.dt = dt
        
        # 记录历史数据
        self.time_history = []
        self.v1x_history = []
        self.v1y_history = []
        self.v2x_history = []
        self.v2y_history = []
        self.ke_history = []
        self.px_history = []
        self.py_history = []
        
        # 边界参数
        self.boundary = 1.0
        self.r1 = 0.05
        self.r2 = 0.08

    def update(self):
        # 检测球-球碰撞
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        dist = np.sqrt(dx**2 + dy**2)
        if dist < self.r1 + self.r2:
            # 二维完全弹性碰撞
            nx = dx / dist
            ny = dy / dist
            
            # 相对速度
            dvx = self.v1x - self.v2x
            dvy = self.v1y - self.v2y
            dvn = dvx * nx + dvy * ny
            
            # 如果物体正在远离，不处理碰撞
            if dvn > 0:
                pass
            else:
                # 冲量计算
                j = 2 * dvn / (1/self.m1 + 1/self.m2)
                self.v1x -= j * nx / self.m1
                self.v1y -= j * ny / self.m1
                self.v2x += j * nx / self.m2
                self.v2y += j * ny / self.m2
        
        # 边界碰撞检测（反弹）
        # 球1
        if self.x1 - self.r1 < -self.boundary or self.x1 + self.r1 > self.boundary:
            self.v1x *= -1
            self.x1 = np.clip(self.x1, -self.boundary + self.r1, self.boundary - self.r1)
        if self.y1 - self.r1 < -self.boundary or self.y1 + self.r1 > self.boundary:
            self.v1y *= -1
            self.y1 = np.clip(self.y1, -self.boundary + self.r1, self.boundary - self.r1)
        
        # 球2
        if self.x2 - self.r2 < -self.boundary or self.x2 + self.r2 > self.boundary:
            self.v2x *= -1
            self.x2 = np.clip(self.x2, -self.boundary + self.r2, self.boundary - self.r2)
        if self.y2 - self.r2 < -self.boundary or self.y2 + self.r2 > self.boundary:
            self.v2y *= -1
            self.y2 = np.clip(self.y2, -self.boundary + self.r2, self.boundary - self.r2)
        
        # 更新位置
        self.x1 += self.v1x * self.dt
        self.y1 += self.v1y * self.dt
        self.x2 += self.v2x * self.dt
        self.y2 += self.v2y * self.dt
        
        # 记录数据
        self.time_history.append(len(self.time_history) * self.dt)
        self.v1x_history.append(self.v1x)
        self.v1y_history.append(self.v1y)
        self.v2x_history.append(self.v2x)
        self.v2y_history.append(self.v2y)
        
        # 动能
        ke1 = 0.5 * self.m1 * (self.v1x**2 + self.v1y**2)
        ke2 = 0.5 * self.m2 * (self.v2x**2 + self.v2y**2)
        self.ke_history.append(ke1 + ke2)
        
        # 动量
        px = self.m1 * self.v1x + self.m2 * self.v2x
        py = self.m1 * self.v1y + self.m2 * self.v2y
        self.px_history.append(px)
        self.py_history.append(py)

# -------------------------- 初始化仿真 --------------------------
if 'sim' not in st.session_state:
    st.session_state.sim = CollisionSimulation(m1, m2, x1, y1, v1x, v1y, x2, y2, v2x, v2y, dt)
    st.session_state.running = False

sim = st.session_state.sim

# -------------------------- 控制按钮 --------------------------
col_play, col_pause, col_reset = st.columns(3)
with col_play:
    if st.button("▶️ 播放", use_container_width=True):
        st.session_state.running = True
with col_pause:
    if st.button("⏸️ 暂停", use_container_width=True):
        st.session_state.running = False
with col_reset:
    if st.button("🔄 重置仿真", use_container_width=True):
        st.session_state.sim = CollisionSimulation(m1, m2, x1, y1, v1x, v1y, x2, y2, v2x, v2y, dt)
        sim = st.session_state.sim
        st.session_state.running = False

# -------------------------- 主显示区域 --------------------------
col_main, col_plots = st.columns([1, 1.2])

with col_main:
    st.subheader("🟢 二维碰撞场景")
    fig_scene, ax_scene = plt.subplots(figsize=(5, 5))
    ax_scene.set_xlim(-1.1, 1.1)
    ax_scene.set_ylim(-1.1, 1.1)
    ax_scene.set_aspect('equal')
    ax_scene.set_title("二维连续动态碰撞", fontsize=12)
    ax_scene.set_xlabel("x (m)")
    ax_scene.set_ylabel("y (m)")
    ax_scene.grid(True, alpha=0.3)
    
    # 绘制边界
    ax_scene.plot([-1, 1, 1, -1, -1], [-1, -1, 1, 1, -1], 'k-', linewidth=2)
    
    # 初始绘制球
    circle1 = Circle((sim.x1, sim.y1), sim.r1, color='cyan', alpha=0.7, label=f"m1={sim.m1}kg")
    circle2 = Circle((sim.x2, sim.y2), sim.r2, color='magenta', alpha=0.7, label=f"m2={sim.m2}kg")
    ax_scene.add_patch(circle1)
    ax_scene.add_patch(circle2)
    ax_scene.legend()
    
    # 速度箭头
    quiv1 = ax_scene.quiver(sim.x1, sim.y1, sim.v1x, sim.v1y, angles='xy', scale_units='xy', scale=3, color='blue', width=0.005)
    quiv2 = ax_scene.quiver(sim.x2, sim.y2, sim.v2x, sim.v2y, angles='xy', scale_units='xy', scale=3, color='green', width=0.005)
    
    scene_placeholder = st.pyplot(fig_scene)

with col_plots:
    st.subheader("📊 实时物理曲线图")
    fig_plots, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(7, 8), sharex=True)
    
    # 速度时间图
    ax1.set_title("速度-时间图像", fontsize=10)
    ax1.set_ylabel("速度 (m/s)")
    ax1.grid(True, alpha=0.3)
    line_v1x, = ax1.plot([], [], 'b-', label='v1x')
    line_v1y, = ax1.plot([], [], 'c--', label='v1y')
    line_v2x, = ax1.plot([], [], 'r-', label='v2x')
    line_v2y, = ax1.plot([], [], 'm--', label='v2y')
    ax1.legend(loc='upper right', fontsize=8)
    
    # 动能时间图
    ax2.set_title("动能-时间图像", fontsize=10)
    ax2.set_ylabel("动能 (J)")
    ax2.grid(True, alpha=0.3)
    line_ke, = ax2.plot([], [], 'g-', linewidth=2)
    
    # 动量时间图
    ax3.set_title("动量-时间图像", fontsize=10)
    ax3.set_xlabel("时间 (s)")
    ax3.set_ylabel("动量 (kg·m/s)")
    ax3.grid(True, alpha=0.3)
    line_px, = ax3.plot([], [], 'orange', label='总Px')
    line_py, = ax3.plot([], [], 'purple', label='总Py')
    ax3.legend(loc='upper right', fontsize=8)
    
    plt.tight_layout()
    plots_placeholder = st.pyplot(fig_plots)

# -------------------------- 仿真循环 --------------------------
if st.session_state.running:
    while st.session_state.running and len(sim.time_history) * sim.dt < max_time:
        sim.update()
        
        # 更新场景图
        circle1.center = (sim.x1, sim.y1)
        circle2.center = (sim.x2, sim.y2)
        quiv1.set_offsets([sim.x1, sim.y1])
        quiv1.set_UVC(sim.v1x, sim.v1y)
        quiv2.set_offsets([sim.x2, sim.y2])
        quiv2.set_UVC(sim.v2x, sim.v2y)
        
        scene_placeholder.pyplot(fig_scene)
        
        # 更新曲线图
        t = np.array(sim.time_history)
        line_v1x.set_data(t, sim.v1x_history)
        line_v1y.set_data(t, sim.v1y_history)
        line_v2x.set_data(t, sim.v2x_history)
        line_v2y.set_data(t, sim.v2y_history)
        line_ke.set_data(t, sim.ke_history)
        line_px.set_data(t, sim.px_history)
        line_py.set_data(t, sim.py_history)
        
        # 调整坐标轴范围
        ax1.set_xlim(0, max(t) + 0.5)
        ax1.relim()
        ax1.autoscale_view(scalex=False, scaley=True)
        ax2.relim()
        ax2.autoscale_view(scalex=False, scaley=True)
        ax3.relim()
        ax3.autoscale_view(scalex=False, scaley=True)
        
        plots_placeholder.pyplot(fig_plots)
        
        # 控制帧率
        time.sleep(0.05)
        
        # 刷新页面
        st.rerun()

st.info("💡 提示：点击「播放」开始仿真，「暂停」暂停仿真，「重置」恢复初始状态。右侧可修改两球质量、初速度和初始位置参数。")
