import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# -------------------------- 页面配置 --------------------------
st.set_page_config(page_title="2D Elastic Collision Simulation", layout="wide")
st.title("2D Perfectly Elastic Collision Simulation")

# -------------------------- 侧边栏参数设置 --------------------------
st.sidebar.header("⚙️ Ball Parameters")
col1, col2 = st.sidebar.columns(2)

# 球1参数
with col1:
    st.subheader("Ball 1 (Blue)")
    m1 = st.number_input("Mass m₁ (kg)", min_value=0.1, max_value=5.0, value=0.5, step=0.1)
    v1x = st.number_input("Velocity v₁ₓ (m/s)", min_value=-5.0, max_value=5.0, value=0.45, step=0.1)
    v1y = st.number_input("Velocity v₁ᵧ (m/s)", min_value=-5.0, max_value=5.0, value=0.34, step=0.1)
    x1 = st.number_input("Position x₁ (m)", min_value=-1.0, max_value=1.0, value=-0.13, step=0.01)
    y1 = st.number_input("Position y₁ (m)", min_value=-1.0, max_value=1.0, value=-0.10, step=0.01)

# 球2参数
with col2:
    st.subheader("Ball 2 (Pink)")
    m2 = st.number_input("Mass m₂ (kg)", min_value=0.1, max_value=5.0, value=1.5, step=0.1)
    v2x = st.number_input("Velocity v₂ₓ (m/s)", min_value=-5.0, max_value=5.0, value=-0.87, step=0.1)
    v2y = st.number_input("Velocity v₂ᵧ (m/s)", min_value=-5.0, max_value=5.0, value=0.04, step=0.1)
    x2 = st.number_input("Position x₂ (m)", min_value=-1.0, max_value=1.0, value=0.61, step=0.01)
    y2 = st.number_input("Position y₂ (m)", min_value=-1.0, max_value=1.0, value=-0.06, step=0.01)

# 仿真控制
st.sidebar.header("🎮 Simulation Control")
dt = st.sidebar.slider("Time Step dt (s)", min_value=0.001, max_value=0.01, value=0.005, step=0.001)
max_time = st.sidebar.slider("Total Time (s)", min_value=5, max_value=30, value=15, step=1)

# -------------------------- 会话状态控制 --------------------------
if "is_playing" not in st.session_state:
    st.session_state.is_playing = True
if "reset_count" not in st.session_state:
    st.session_state.reset_count = 0

col_play, col_pause, col_reset = st.columns(3)
with col_play:
    if st.button("▶️ Play", use_container_width=True):
        st.session_state.is_playing = True
with col_pause:
    if st.button("⏸️ Pause", use_container_width=True):
        st.session_state.is_playing = False
with col_reset:
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.reset_count += 1
        st.session_state.is_playing = True

# -------------------------- 嵌入二维JS Canvas流畅动画 --------------------------
st.subheader("🟢 2D Continuous Collision Animation")
playing = st.session_state.is_playing
reset_key = st.session_state.reset_count

html_code = f'''
<div style="display:flex;justify-content:center;">
    <canvas id="aniCanvas" width="600" height="400" style="border:1px solid #eee;"></canvas>
</div>
<script>
    // 外部传入参数
    const m1 = {m1};
    const m2 = {m2};
    const v1x_initial = {v1x};
    const v1y_initial = {v1y};
    const v2x_initial = {v2x};
    const v2y_initial = {v2y};
    const x1_initial = {x1};
    const y1_initial = {y1};
    const x2_initial = {x2};
    const y2_initial = {y2};
    const resetKey = {reset_key};

    // 物理参数
    let x1 = x1_initial * 300 + 300;
    let y1 = y1_initial * 200 + 200;
    let x2 = x2_initial * 300 + 300;
    let y2 = y2_initial * 200 + 200;
    let v1x = v1x_initial * 30;
    let v1y = v1y_initial * 30;
    let v2x = v2x_initial * 30;
    let v2y = v2y_initial * 30;
    const r1 = 15;
    const r2 = 20;
    let playing = {str(playing).lower()};
    const boundary = 1.0;

    // 获取画布
    const aniCvs = document.getElementById("aniCanvas");
    const aniCtx = aniCvs.getContext("2d");

    // 动画循环
    function animate() {{
        if (!playing) {{
            // 暂停时只重绘当前帧
            aniCtx.clearRect(0,0,aniCvs.width,aniCvs.height);
            drawBoundary();
            drawBall(x1, y1, r1, "#4ecdc4");
            drawBall(x2, y2, r2, "#ff6b9d");
            drawArrow(x1, y1, v1x, v1y, "#0066ff");
            drawArrow(x2, y2, v2x, v2y, "#22aa22");
            requestAnimationFrame(animate);
            return;
        }}

        // 1. 球-球碰撞检测与处理
        const dx = x2 - x1;
        const dy = y2 - y1;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < r1 + r2) {{
            const nx = dx / dist;
            const ny = dy / dist;
            const dvx = v1x - v2x;
            const dvy = v1y - v2y;
            const dvn = dvx * nx + dvy * ny;

            if (dvn <= 0) {{
                const j = 2 * dvn / (1/m1 + 1/m2);
                v1x -= j * nx / m1;
                v1y -= j * ny / m1;
                v2x += j * nx / m2;
                v2y += j * ny / m2;
                // 防止重叠
                const overlap = (r1 + r2 - dist) / 2;
                x1 -= overlap * nx;
                y1 -= overlap * ny;
                x2 += overlap * nx;
                y2 += overlap * ny;
            }}
        }}

        // 2. 边界反弹
        // 球1
        if (x1 - r1 < 0 || x1 + r1 > 600) {{
            v1x *= -1;
            x1 = Math.max(r1, Math.min(600 - r1, x1));
        }}
        if (y1 - r1 < 0 || y1 + r1 > 400) {{
            v1y *= -1;
            y1 = Math.max(r1, Math.min(400 - r1, y1));
        }}
        // 球2
        if (x2 - r2 < 0 || x2 + r2 > 600) {{
            v2x *= -1;
            x2 = Math.max(r2, Math.min(600 - r2, x2));
        }}
        if (y2 - r2 < 0 || y2 + r2 > 400) {{
            v2y *= -1;
            y2 = Math.max(r2, Math.min(400 - r2, y2));
        }}

        // 3. 更新位置
        x1 += v1x;
        y1 += v1y;
        x2 += v2x;
        y2 += v2y;

        // 4. 绘制
        aniCtx.clearRect(0,0,aniCvs.width,aniCvs.height);
        drawBoundary();
        drawBall(x1, y1, r1, "#4ecdc4");
        drawBall(x2, y2, r2, "#ff6b9d");
        drawArrow(x1, y1, v1x, v1y, "#0066ff");
        drawArrow(x2, y2, v2x, v2y, "#22aa22");

        requestAnimationFrame(animate);
    }}

    // 辅助绘制函数
    function drawBoundary() {{
        aniCtx.strokeStyle = "#333";
        aniCtx.lineWidth = 2;
        aniCtx.strokeRect(0, 0, 600, 400);
    }}
    function drawBall(x, y, r, color) {{
        aniCtx.beginPath();
        aniCtx.arc(x, y, r, 0, Math.PI*2);
        aniCtx.fillStyle = color;
        aniCtx.fill();
        aniCtx.strokeStyle = "#fff";
        aniCtx.lineWidth = 1;
        aniCtx.stroke();
    }}
    function drawArrow(x, y, vx, vy, color) {{
        const scale = 5;
        aniCtx.beginPath();
        aniCtx.moveTo(x, y);
        aniCtx.lineTo(x + vx*scale, y + vy*scale);
        aniCtx.strokeStyle = color;
        aniCtx.lineWidth = 2;
        aniCtx.stroke();
    }}

    animate();
</script>
'''
st.components.v1.html(html_code, height=450)

# -------------------------- 保留你原来的物理曲线图（Python端生成） --------------------------
st.markdown("---")
st.subheader("📊 Physical Curves")

# 计算理论曲线数据
v1_final = ((m1 - m2) * v1x + 2 * m2 * v2x) / (m1 + m2)
v2_final = ((m2 - m1) * v2x + 2 * m1 * v1x) / (m1 + m2)

t_total = 0.03
dt_data = 0.0003
t = np.arange(0, t_total, dt_data)
t_collision = t_total * 0.5

v1_list = []
v2_list = []
ke_list = []
p_list = []

for ti in t:
    if ti < t_collision:
        cv1 = v1x
        cv2 = v2x
    else:
        cv1 = v1_final
        cv2 = v2_final
    
    ke = 0.5 * m1 * cv1**2 + 0.5 * m2 * cv2**2
    p = m1 * cv1 + m2 * cv2
    
    v1_list.append(cv1)
    v2_list.append(cv2)
    ke_list.append(ke)
    p_list.append(p)

# 绘制三张曲线
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9, 5), sharex=True)

ax1.plot(t, v1_list, color="#4ecdc4", label="Ball1 vx")
ax1.plot(t, v2_list, color="#ff6b9d", label="Ball2 vx")
ax1.set_title("Velocity - Time")
ax1.set_ylabel("Velocity (m/s)")
ax1.legend()
ax1.grid(alpha=0.3)

ax2.plot(t, ke_list, color="#2ca02c")
ax2.set_title("Kinetic Energy - Time")
ax2.set_ylabel("KE (J)")
ax2.grid(alpha=0.3)

ax3.plot(t, p_list, color="#ff7f0e")
ax3.set_title("Momentum - Time")
ax3.set_xlabel("Time (s)")
ax3.set_ylabel("Momentum (kg·m/s)")
ax3.grid(alpha=0.3)

plt.tight_layout()
st.pyplot(fig)
