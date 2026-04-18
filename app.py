import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

# ========== 解决中文乱码 ==========
plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

# 物理参数初始化
m1_0 = 1.0   # 物体1初始质量 (kg)
m2_0 = 2.0   # 物体2初始质量 (kg)
v1_0 = 3.0   # 物体1初始速度 (m/s)
v2_0 = -1.0  # 物体2初始速度 (m/s)
r = 0.3      # 物体半径 (m)
dt = 0.01    # 时间步长 (s)
t_total = 5  # 总仿真时间 (s)

# 创建画布
fig = plt.figure(figsize=(12, 6))
ax_sim = fig.add_subplot(121)  # 仿真画面
ax_plot = fig.add_subplot(122) # 速度-时间曲线
plt.subplots_adjust(left=0.1, bottom=0.35) # 为滑块预留空间

# 初始位置
x1 = 0.0
x2 = 3.0
# 物体绘制
obj1, = ax_sim.plot([x1], [0], 'ro', markersize=10, label='物体1')
obj2, = ax_sim.plot([x2], [0], 'bo', markersize=10, label='物体2')
# 辅助线
line1 = ax_sim.axhline(y=0, color='k', alpha=0.3)
# 速度曲线
t_list = []
v1_list = []
v2_list = []
v1_line, = ax_plot.plot([], [], 'r-', label='物体1速度')
v2_line, = ax_plot.plot([], [], 'b-', label='物体2速度')

# 仿真画面设置
ax_sim.set_xlim(-1, 6)
ax_sim.set_ylim(-1, 1)
ax_sim.set_title('对心完全弹性碰撞仿真')
ax_sim.set_xlabel('位置 x (m)')
ax_sim.set_yticks([])
ax_sim.grid(True, alpha=0.3)
ax_sim.legend()

# 速度曲线设置
ax_plot.set_xlim(0, t_total)
ax_plot.set_ylim(-5, 5)
ax_plot.set_title('速度-时间曲线')
ax_plot.set_xlabel('时间 t (s)')
ax_plot.set_ylabel('速度 v (m/s)')
ax_plot.legend()
ax_plot.grid(True, alpha=0.3)

# 创建滑块
# 质量1滑块
ax_m1 = plt.axes([0.1, 0.2, 0.35, 0.03])
m1_slider = Slider(
    ax=ax_m1,
    label='m1 (kg)',
    valmin=0.1,
    valmax=5.0,
    valinit=m1_0,
    valstep=0.1
)

# 质量2滑块
ax_m2 = plt.axes([0.1, 0.15, 0.35, 0.03])
m2_slider = Slider(
    ax=ax_m2,
    label='m2 (kg)',
    valmin=0.1,
    valmax=5.0,
    valinit=m2_0,
    valstep=0.1
)

# 初速度1滑块
ax_v1 = plt.axes([0.55, 0.2, 0.35, 0.03])
v1_slider = Slider(
    ax=ax_v1,
    label='v1 (m/s)',
    valmin=-5.0,
    valmax=5.0,
    valinit=v1_0,
    valstep=0.1
)

# 初速度2滑块
ax_v2 = plt.axes([0.55, 0.15, 0.35, 0.03])
v2_slider = Slider(
    ax=ax_v2,
    label='v2 (m/s)',
    valmin=-5.0,
    valmax=5.0,
    valinit=v2_0,
    valstep=0.1
)

# 重置按钮
ax_reset = plt.axes([0.45, 0.05, 0.1, 0.04])
reset_button = Button(ax_reset, '重置仿真')

# 全局变量
sim_running = False
current_t = 0
current_x1 = x1
current_x2 = x2
current_v1 = v1_0
current_v2 = v2_0
t_list = []
v1_list = []
v2_list = []

# 碰撞计算函数
def elastic_collision(m1, m2, v10, v20):
    v1 = ((m1 - m2)*v10 + 2*m2*v20) / (m1 + m2)
    v2 = ((m2 - m1)*v20 + 2*m1*v10) / (m1 + m2)
    return v1, v2

# 更新函数
def update(val):
    global sim_running, current_t, current_x1, current_x2, current_v1, current_v2, t_list, v1_list, v2_list
    if sim_running:
        return
    
    # 重置仿真状态
    m1 = m1_slider.val
    m2 = m2_slider.val
    v10 = v1_slider.val
    v20 = v2_slider.val
    
    current_t = 0
    current_x1 = x1
    current_x2 = x2
    current_v1 = v10
    current_v2 = v20
    t_list = []
    v1_list = []
    v2_list = []
    
    # 更新初始画面
    obj1.set_data([current_x1], [0])
    obj2.set_data([current_x2], [0])
    v1_line.set_data([], [])
    v2_line.set_data([], [])
    fig.canvas.draw_idle()

# 重置函数
def reset_simulation(event):
    global sim_running, current_t, current_x1, current_x2, current_v1, current_v2, t_list, v1_list, v2_list
    sim_running = False
    update(None)
    sim_running = True
    animate()

# 动画循环
def animate():
    global sim_running, current_t, current_x1, current_x2, current_v1, current_v2, t_list, v1_list, v2_list
    m1 = m1_slider.val
    m2 = m2_slider.val
    
    while sim_running and current_t < t_total:
        # 检测碰撞
        if abs(current_x1 - current_x2) <= 2*r and current_v1 > current_v2:
            # 计算碰撞后速度
            v1_new, v2_new = elastic_collision(m1, m2, current_v1, current_v2)
            current_v1 = v1_new
            current_v2 = v2_new
        
        # 更新位置
        current_x1 += current_v1 * dt
        current_x2 += current_v2 * dt
        
        # 边界反弹（防止物体跑出画面）
        if current_x1 < -1 + r:
            current_v1 = abs(current_v1)
            current_x1 = -1 + r
        if current_x2 > 6 - r:
            current_v2 = -abs(current_v2)
            current_x2 = 6 - r
        
        # 记录数据
        t_list.append(current_t)
        v1_list.append(current_v1)
        v2_list.append(current_v2)
        
        # 更新画面
        obj1.set_data([current_x1], [0])
        obj2.set_data([current_x2], [0])
        v1_line.set_data(t_list, v1_list)
        v2_line.set_data(t_list, v2_list)
        
        current_t += dt
        fig.canvas.draw_idle()
        plt.pause(dt)
    
    sim_running = False

# 绑定事件
m1_slider.on_changed(update)
m2_slider.on_changed(update)
v1_slider.on_changed(update)
v2_slider.on_changed(update)
reset_button.on_clicked(reset_simulation)

# 初始化
update(None)
plt.show()
