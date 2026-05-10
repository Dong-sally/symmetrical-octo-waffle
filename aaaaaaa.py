import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import time
import streamlit.components.v1 as components

# 宽屏页面配置（固定不变）
st.set_page_config(
    page_title="1D Elastic Collision",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 会话状态初始化（固定初始值）
if "running" not in st.session_state:
    st.session_state.running = False
if "t_list" not in st.session_state:
    st.session_state.t_list = [0.0]
if "v1_list" not in st.session_state:
    st.session_state.v1_list = []
if "v2_list" not in st.session_state:
    st.session_state.v2_list = []
if "ke1_list" not in st.session_state:
    st.session_state.ke1_list = []
if "ke2_list" not in st.session_state.ke2_list = []
if "p1_list" not in st.session_state:
    st.session_state.p1_list = []
if "p2_list" not in st.session_state:
    st.session_state.p2_list = []
if "x1" not in st.session_state:
    st.session_state.x1 = 80.0
if "x2" not in st.session_state:
    st.session_state.x2 = 480.0
if "v1" not in st.session_state:
    st.session_state.v1 = 4.0
if "v2" not in st.session_state:
    st.session_state.v2 = -2.0

# 标题与碰撞公式（固定）
st.title("One-Dimensional Collision Simulation")
st.markdown("### Collision Formula")
st.latex(r'''
\begin{align*}
v_1' &= \frac{(m_1 - e m_2)v_1 + (1+e)m_2 v_2}{m_1 + m_2} \\
v_2' &= \frac{(1+e)m_1 v_1 + (m_2 - e m_1)v_2}{m_1 + m_2}
\end{align*}
''')
st.caption("e: Restitution Coefficient  m: Mass  v: Velocity")

# 参数调节面板（固定范围）
st.sidebar.header("Parameters")
m1 = st.sidebar.slider("Mass 1 (m1)", 0.5, 10.0, 2.0, 0.1)
m2 = st.sidebar.slider("Mass 2 (m2)", 0.5, 10.0, 3.0, 0.1)
v1_init = st.sidebar.slider("Initial Velocity 1 (v1)", -10.0, 10.0, 4.0, 0.1)
v2_init = st.sidebar.slider("Initial Velocity 2 (v2)", -10.0, 10.0, -2.0, 0.1)
e = st.sidebar.slider("Restitution (e)", 0.0, 1.0, 1.0, 0.01)
dt = 0.05  # 固定时间步长

# 播放/暂停/重置 按钮
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("▶️ Play"):
        st.session_state.running = True
with c2:
    if st.button("⏸️ Pause"):
        st.session_state.running = False
with c3:
    if st.button("🔄 Reset"):
        st.session_state.running = False
        st.session_state.t_list = [0.0]
        st.session_state.v1_list = []
        st.session_state.v2_list = []
        st.session_state.ke1_list = []
        st.session_state.ke2_list = []
        st.session_state.p1_list = []
        st.session_state.p2_list = []
        st.session_state.x1 = 80.0
        st.session_state.x2 = 480.0
        st.session_state.v1 = v1_init
        st.session_state.v2 = v2_init

# 初始动能显示（固定）
st.subheader("Initial Kinetic Energy")
ke1 = 0.5 * m1 * v1_init**2
ke2 = 0.5 * m2 * v2_init**2
total_ke = ke1 + ke2
col1, col2, col3 = st.columns(3)
col1.metric("Ball 1 KE", f"{ke1:.2f} J")
col2.metric("Ball 2 KE", f"{ke2:.2f} J")
col3.metric("Total KE", f"{total_ke:.2f} J")

# 画布占位符
st.subheader("Animation")
canvas_ph = st.empty()

# 图表占位符
st.subheader("Time History Graphs")
plot_ph = st.empty()

# 碰撞计算函数（固定逻辑）
def collision(m1, m2, v1, v2, e):
    v1f = ((m1 - e*m2)*v1 + (1+e)*m2*v2) / (m1+m2)
    v2f = ((1+e)*m1*v1 + (m2 - e*m1)*v2) / (m1+m2)
    return v1f, v2f

# 主循环
while st.session_state.running:
    x1 = st.session_state.x1
    x2 = st.session_state.x2
    v1 = st.session_state.v1
    v2 = st.session_state.v2

    # 碰撞检测
    if abs(x2 - x1) <= 30:
        v1, v2 = collision(m1, m2, v1, v2, e)

    # 位置更新
    x1 += v1 * dt * 3
    x2 += v2 * dt * 3

    # 边界反弹逻辑（固定）
    if x1 <= 15:
        x1 = 15
        v1 = -v1
    if x1 >= 585:
        x1 = 585
        v1 = -v1
    if x2 <= 15:
        x2 = 15
        v2 = -v2
    if x2 >= 585:
        x2 = 585
        v2 = -v2

    # 保存状态
    st.session_state.x1 = x1
    st.session_state.x2 = x2
    st.session_state.v1 = v1
    st.session_state.v2 = v2

    # 记录数据
    t = st.session_state.t_list[-1] + dt
    st.session_state.t_list.append(t)
    st.session_state.v1_list.append(v1)
    st.session_state.v2_list.append(v2)
    st.session_state.ke1_list.append(0.5*m1*v1**2)
    st.session_state.ke2_list.append(0.5*m2*v2**2)
    st.session_state.p1_list.append(m1*v1)
    st.session_state.p2_list.append(m2*v2)

    # 限制数据长度
    if len(st.session_state.t_list) > 200:
        st.session_state.t_list = st.session_state.t_list[-200:]
        st.session_state.v1_list = st.session_state.v1_list[-200:]
        st.session_state.v2_list = st.session_state.v2_list[-200:]
        st.session_state.ke1_list = st.session_state.ke1_list[-200:]
        st.session_state.ke2_list = st.session_state.ke2_list[-200:]
        st.session_state.p1_list = st.session_state.p1_list[-200:]
        st.session_state.p2_list = st.session_state.p2_list[-200:]

    # 600×150 JS画布（内置x1,x2,v1,v2,t数组）
    with canvas_ph:
        js = f"""
        <canvas id="can" width="600" height="150" style="background:#fff; border:1px solid #ddd;"></canvas>
        <script>
            // 内置时间与位置速度数据记录数组
            const tArr = {st.session_state.t_list};
            const x1Arr = {[st.session_state.x1]};
            const x2Arr = {[st.session_state.x2]};
            const v1Arr = {[st.session_state.v1]};
            const v2Arr = {[st.session_state.v2]};
            
            const canvas = document.getElementById('can');
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0,0,600,150);
            
            // 地面
            ctx.beginPath();
            ctx.moveTo(0,120);
            ctx.lineTo(600,120);
            ctx.lineWidth=3;
            ctx.stroke();
            
            // 红球1
            ctx.beginPath();
            ctx.arc({x1},120,15,0,Math.PI*2);
            ctx.fillStyle="red";
            ctx.fill();
            ctx.stroke();
            
            // 绿球2
            ctx.beginPath();
            ctx.arc({x2},120,15,0,Math.PI*2);
            ctx.fillStyle="lime";
            ctx.fill();
            ctx.stroke();
        </script>
        """
        components.html(js, height=155)

    # 三张英文曲线图（固定颜色/样式）
    with plot_ph:
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 4))
        
        ax1.plot(st.session_state.t_list, st.session_state.v1_list, color='red', label='Ball 1', lw=2)
        ax1.plot(st.session_state.t_list, st.session_state.v2_list, color='lime', label='Ball 2', lw=2)
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Velocity (m/s)")
        ax1.set_title("Velocity vs Time")
        ax1.legend()
        ax1.grid(alpha=0.3)

        ax2.plot(st.session_state.t_list, st.session_state.ke1_list, color='red', label='Ball 1', lw=2)
        ax2.plot(st.session_state.t_list, st.session_state.ke2_list, color='lime', label='Ball 2', lw=2)
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Kinetic Energy (J)")
        ax2.set_title("Kinetic Energy vs Time")
        ax2.legend()
        ax2.grid(alpha=0.3)

        ax3.plot(st.session_state.t_list, st.session_state.p1_list, color='red', label='Ball 1', lw=2)
        ax3.plot(st.session_state.t_list, st.session_state.p2_list, color='lime', label='Ball 2', lw=2)
        ax3.set_xlabel("Time (s)")
        ax3.set_ylabel("Momentum (kg·m/s)")
        ax3.set_title("Momentum vs Time")
        ax3.legend()
        ax3.grid(alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)

    time.sleep(0.01)

# 暂停/重置静态显示
with canvas_ph:
    js_static = f"""
    <canvas id="can" width="600" height="150" style="background:#fff; border:1px solid #ddd;"></canvas>
    <script>
        const ctx = document.getElementById('can').getContext('2d');
        ctx.clearRect(0,0,600,150);
        ctx.beginPath(); ctx.moveTo(0,120); ctx.lineTo(600,120); ctx.lineWidth=3; ctx.stroke();
        ctx.beginPath(); ctx.arc({st.session_state.x1},120,15,0,Math.PI*2); ctx.fillStyle='red'; ctx.fill(); ctx.stroke();
        ctx.beginPath(); ctx.arc({st.session_state.x2},120,15,0,Math.PI*2); ctx.fillStyle='lime'; ctx.fill(); ctx.stroke();
    </script>
    """
    components.html(js_static, height=155)

with plot_ph:
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 4))
    ax1.plot(st.session_state.t_list, st.session_state.v1_list, color='red', label='Ball 1', lw=2)
    ax1.plot(st.session_state.t_list, st.session_state.v2_list, color='lime', label='Ball 2', lw=2)
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Velocity (m/s)")
    ax1.set_title("Velocity vs Time")
    ax1.legend()
    ax1.grid(alpha=0.3)

    ax2.plot(st.session_state.t_list, st.session_state.ke1_list, color='red', label='Ball 1', lw=2)
    ax2.plot(st.session_state.t_list, st.session_state.ke2_list, color='lime', label='Ball 2', lw=2)
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Kinetic Energy (J)")
    ax2.set_title("Kinetic Energy vs Time")
    ax2.legend()
    ax2.grid(alpha=0.3)

    ax3.plot(st.session_state.t_list, st.session_state.p1_list, color='red', label='Ball 1', lw=2)
    ax3.plot(st.session_state.t_list, st.session_state.p2_list, color='lime', label='Ball 2', lw=2)
    ax3.set_xlabel("Time (s)")
    ax3.set_ylabel("Momentum (kg·m/s)")
    ax3.set_title("Momentum vs Time")
    ax3.legend()
    ax3.grid(alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
