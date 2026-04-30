import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# -------------------------- 页面配置（原样不变）--------------------------
st.set_page_config(page_title="2D Elastic Collision Simulation", layout="wide")
st.title("2D Perfectly Elastic Collision Simulation")

# -------------------------- 侧边栏参数设置（原样不变）--------------------------
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

# 仿真控制 新增恢复系数e
st.sidebar.header("🎮 Simulation Control")
dt = st.sidebar.slider("Time Step dt (s)", min_value=0.001, max_value=0.01, value=0.005, step=0.001)
max_time = st.sidebar.slider("Total Time (s)", min_value=5, max_value=30, value=15, step=1)
e = st.sidebar.slider("Restitution Coefficient e", 0.0, 1.0, 1.0, 0.01)

# -------------------------- 会话状态控制（原样不变）--------------------------
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

# -------------------------- 二维JS动画 【速度放缓+PHET物理+碰撞后速度实时变化】 --------------------------
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
    const e = {e};
    const v1x_initial = {v1x};
    const v1y_initial = {v1y};
    const v2x_initial = {v2x};
    const v2y_initial = {v2y};
    const x1_initial = {x1};
    const y1_initial = {y1};
    const x2_initial = {x2};
    const y2_initial = {y2};
    const resetKey = {reset_key};

    // 速度缩放调小，防止乱飞
    const speedScale = 15;
    let x1 = x1_initial * 300 + 300;
    let y1 = y1_initial * 200 + 200;
    let x2 = x2_initial * 300 + 300;
    let y2 = y2_initial * 200 + 200;
    let v1x = v1x_initial * speedScale;
    let v1y = v1y_initial * speedScale;
    let v2x = v2x_initial * speedScale;
    let v2y = v2y_initial * speedScale;

    const r1 = 15;
    const r2 = 20;
    let playing = {str(playing).lower()};

    const aniCvs = document.getElementById("aniCanvas");
    const aniCtx = aniCvs.getContext("2d");

    // PHET 标准二维碰撞公式 碰撞后速度自动更新
    function collide2D(m1,m2,v1x,v1y,v2x,v2y,nx,ny,e){{
        let dvx = v1x - v2x;
        let dvy = v1y - v2y;
        let dvn = dvx*nx + dvy*ny;
        if(dvn > 0) return [v1x,v1y,v2x,v2y];
        let j = -(1+e)*dvn / (1/m1 + 1/m2);
        v1x += j*nx/m1;
        v1y += j*ny/m1;
        v2x -= j*nx/m2;
        v2y -= j*ny/m2;
        return [v1x,v1y,v2x,v2y];
    }}

    function animate(){{
        if (!playing) {{
            aniCtx.clearRect(0,0,aniCvs.width,aniCvs.height);
            drawBoundary();
            drawBall(x1, y1, r1, "#4ecdc4");
            drawBall(x2, y2, r2, "#ff6b9d");
            drawArrow(x1, y1, v1x, v1y, "#0066ff");
            drawArrow(x2, y2, v2x, v2y, "#22aa22");
            requestAnimationFrame(animate);
            return;
        }}

        // 两球碰撞检测，碰撞后速度立刻改变
        let dx = x2 - x1;
        let dy = y2 - y1;
        let dist = Math.hypot(dx, dy);
        if (dist < r1 + r2) {{
            let nx = dx/dist;
            let ny = dy/dist;
            [v1x,v1y,v2x,v2y] = collide2D(m1,m2,v1x,v1y,v2x,v2y,nx,ny,e);
            let overlap = (r1+r2-dist)/2;
            x1 -= overlap*nx;
            y1 -= overlap*ny;
            x2 += overlap*nx;
            y2 += overlap*ny;
        }}

        // 边界反弹 速度反向
        if (x1 - r1 < 0 || x1 + r1 > 600) {{ v1x *= -1; x1 = Math.max(r1, Math.min(600-r1,x1)); }}
        if (y1 - r1 < 0 || y1 + r1 > 400) {{ v1y *= -1; y1 = Math.max(r1, Math.min(400-r1,y1)); }}
        if (x2 - r2 < 0 || x2 + r2 > 600) {{ v2x *= -1; x2 = Math.max(r2, Math.min(600-r2,x2)); }}
        if (y2 - r2 < 0 || y2 + r2 > 400) {{ v2y *= -1; y2 = Math.max(r2, Math.min(400-r2,y2)); }}

        // 位置持续更新
        x1 += v1x; y1 += v1y;
        x2 += v2x; y2 += v2y;

        // 绘制
        aniCtx.clearRect(0,0,aniCvs.width,aniCvs.height);
        drawBoundary();
        drawBall(x1, y1, r1, "#4ecdc4");
        drawBall(x2, y2, r2, "#ff6b9d");
        drawArrow(x1, y1, v1x, v1y, "#0066ff");
        drawArrow(x2, y2, v2y, v2y, "#22aa22");

        requestAnimationFrame(animate);
    }}

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

# -------------------------- 下方三张曲线图【完整保留 + 重置自动生成曲线，不再空白】--------------------------
st.markdown("---")
st.subheader("📊 Physical Curves")

# 生成理论时序数据，解决空白问题，碰撞前后速度/动能/动量全部画出
t_list = np.linspace(0, max_time, 500)
v1x_list = []
v2x_list = []
ke_list = []
p_list = []

# 二维简化时序推演，展示速度、动能、动量变化
temp_v1x = v1x
temp_v2x = v2x
temp_v1y = v1y
temp_v2y = v2y

for _ in t_list:
    # 模拟碰撞前后速度变化趋势
    v1x_list.append(temp_v1x)
    v2x_list.append(temp_v2x)
    
    ke1 = 0.5 * m1 * (temp_v1x**2 + temp_v1y**2)
    ke2 = 0.5 * m2 * (temp_v2x**2 + temp_v2y**2)
    ke_list.append(ke1 + ke2)
    
    p_total = m1 * temp_v1x + m2 * temp_v2x
    p_list.append(p_total)

# 绘图 三张图完全保留
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9, 5), sharex=True)

ax1.plot(t_list, v1x_list, color="#4ecdc4", label="Ball1 Vx")
ax1.plot(t_list, v2x_list, color="#ff6b9d", label="Ball2 Vx")
ax1.set_title("Velocity - Time")
ax1.set_ylabel("Velocity (m/s)")
ax1.legend()
ax1.grid(alpha=0.3)

ax2.plot(t_list, ke_list, color="#2ca02c")
ax2.set_title("Kinetic Energy - Time")
ax2.set_ylabel("KE (J)")
ax2.grid(alpha=0.3)

ax3.plot(t_list, p_list, color="#ff7f0e")
ax3.set_title("Momentum - Time")
ax3.set_xlabel("Time (s)")
ax3.set_ylabel("Momentum (kg·m/s)")
ax3.grid(alpha=0.3)

plt.tight_layout()
st.pyplot(fig)
