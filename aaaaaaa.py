import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import streamlit.components.v1 as components

# 宽屏布局（固定）
st.set_page_config(
    page_title="1D Elastic Collision",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 会话状态（固定）
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
if "ke2_list" not in st.session_state:
    st.session_state.ke2_list = []
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

# 标题与公式
st.title("One-Dimensional Collision Simulation")
st.markdown("### Collision Formula")
st.latex(r'''
\begin{align*}
v_1' &= \frac{(m_1 - e m_2)v_1 + (1+e)m_2 v_2}{m_1 + m_2} \\
v_2' &= \frac{(1+e)m_1 v_1 + (m_2 - e m_1)v_2}{m_1 + m_2}
\end{align*}
''')

# 参数面板
st.sidebar.header("Parameters")
m1 = st.sidebar.slider("Mass 1 (m1)", 0.5, 10.0, 2.0, 0.1)
m2 = st.sidebar.slider("Mass 2 (m2)", 0.5, 10.0, 3.0, 0.1)
v1_init = st.sidebar.slider("Initial Velocity 1 (v1)", -10.0, 10.0, 4.0, 0.1)
v2_init = st.sidebar.slider("Initial Velocity 2 (v2)", -10.0, 10.0, -2.0, 0.1)
e = st.sidebar.slider("Restitution (e)", 0.0, 1.0, 1.0, 0.01)
dt = 0.05

# 三按钮
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

# 初始动能
st.subheader("Initial Kinetic Energy")
ke1_i = 0.5 * m1 * v1_init**2
ke2_i = 0.5 * m2 * v2_init**2
total_ke_i = ke1_i + ke2_i
col1, col2, col3 = st.columns(3)
col1.metric("Ball 1 KE", f"{ke1_i:.2f} J")
col2.metric("Ball 2 KE", f"{ke2_i:.2f} J")
col3.metric("Total KE", f"{total_ke_i:.2f} J")

# 画布 + 图表占位
st.subheader("Animation")
canvas_ph = st.empty()
st.subheader("Time History Graphs")
plot_ph = st.empty()

# 碰撞函数
def collision(m1, m2, v1, v2, e):
    v1f = ((m1-e*m2)*v1 + (1+e)*m2*v2) / (m1+m2)
    v2f = ((1+e)*m1*v1 + (m2-e*m1)*v2) / (m1+m2)
    return v1f, v2f

# 主循环
while st.session_state.running:
    x1 = st.session_state.x1
    x2 = st.session_state.x2
    v1 = st.session_state.v1
    v2 = st.session_state.v2

    # 碰撞
    if abs(x2-x1) <= 30:
        v1, v2 = collision(m1, m2, v1, v2, e)

    # 更新位置
    x1 += v1 * dt * 3
    x2 += v2 * dt * 3

    # 边界反弹
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

    # 限长
    if len(st.session_state.t_list) > 200:
        st.session_state.t_list = st.session_state.t_list[-200:]
        st.session_state.v1_list = st.session_state.v1_list[-200:]
        st.session_state.v2_list = st.session_state.v2_list[-200:]
        st.session_state.ke1_list = st.session_state.ke1_list[-200:]
        st.session_state.ke2_list = st.session_state.ke2_list[-200:]
        st.session_state.p1_list = st.session_state.p1_list[-200:]
        st.session_state.p2_list = st.session_state.p2_list[-200:]

    # ====================== JS 核心动画（严格固定变量名）======================
    with canvas_ph:
        js_code = """
        <canvas id='aniCvs' width='600' height='150' style='background:white; border:1px solid #ccc;'></canvas>
        <script>
            // 严格固定变量名：x1, x2, v1, v2, r, playing, dt, aniCvs, aniCtx
            let x1 = """ + str(x1) + """;
            let x2 = """ + str(x2) + """;
            let v1 = """ + str(v1) + """;
            let v2 = """ + str(v2) + """;
            const r = 15;
            const dt = 0.05;
            let playing = true;

            const aniCvs = document.getElementById('aniCvs');
            const aniCtx = aniCvs.getContext('2d');

            // 时间数据记录数组
            let x1Array = [];
            let x2Array = [];
            let v1Array = [];
            let v2Array = [];
            let tArray = [];

            // 绘制函数
            function draw() {
                aniCtx.clearRect(0,0,600,150);
                aniCtx.beginPath();
                aniCtx.moveTo(0,120);
                aniCtx.lineTo(600,120);
                aniCtx.lineWidth=3;
                aniCtx.stroke();

                // 红球
                aniCtx.beginPath();
                aniCtx.arc(x1,120,r,0,Math.PI*2);
                aniCtx.fillStyle='red';
                aniCtx.fill();
                aniCtx.stroke();

                // 绿球
                aniCtx.beginPath();
                aniCtx.arc(x2,120,r,0,Math.PI*2);
                aniCtx.fillStyle='lime';
                aniCtx.fill();
                aniCtx.stroke();
            }

            draw();
        </script>
        """
        components.html(js_code, height=155)

    # 图表
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

# 静态画面
with canvas_ph:
    components.html("""
    <canvas id='aniCvs' width='600' height='150' style='background:white; border:1px solid #ccc;'></canvas>
    <script>
        const aniCvs = document.getElementById('aniCvs');
        const aniCtx = aniCvs.getContext('2d');
        aniCtx.clearRect(0,0,600,150);
        aniCtx.beginPath(); aniCtx.moveTo(0,120); aniCtx.lineTo(600,120); aniCtx.lineWidth=3; aniCtx.stroke();
        aniCtx.beginPath(); aniCtx.arc("""+str(st.session_state.x1)+""",120,15,0,Math.PI*2); aniCtx.fillStyle='red'; aniCtx.fill(); aniCtx.stroke();
        aniCtx.beginPath(); aniCtx.arc("""+str(st.session_state.x2)+""",120,15,0,Math.PI*2); aniCtx.fillStyle='lime'; aniCtx.fill(); aniCtx.stroke();
    </script>
    """, height=155)

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
