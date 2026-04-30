import streamlit as st
import numpy as np

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
    v1x = st.number_input("Velocity v₁ₓ (m/s)", min_value=-5.0, max_value=5.0, value=0.2, step=0.1)
    v1y = st.number_input("Velocity v₁ᵧ (m/s)", min_value=-5.0, max_value=5.0, value=0.15, step=0.1)
    x1 = st.number_input("Position x₁ (m)", min_value=-1.0, max_value=1.0, value=-0.13, step=0.01)
    y1 = st.number_input("Position y₁ (m)", min_value=-1.0, max_value=1.0, value=-0.10, step=0.01)

# 球2参数
with col2:
    st.subheader("Ball 2 (Pink)")
    m2 = st.number_input("Mass m₂ (kg)", min_value=0.1, max_value=5.0, value=1.5, step=0.1)
    v2x = st.number_input("Velocity v₂ₓ (m/s)", min_value=-5.0, max_value=5.0, value=-0.3, step=0.1)
    v2y = st.number_input("Velocity v₂ᵧ (m/s)", min_value=-5.0, max_value=5.0, value=0.05, step=0.1)
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

# -------------------------- 二维JS流畅动画 优化版：速度放缓+实时数据显示+PHET碰撞 布局完全不变 --------------------------
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

    // 坐标映射 + 【速度缩放调小，解决乱飞太快】
    const speedScale = 12;
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

    // PHET 标准二维碰撞公式
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

    // 计算动能
    function getKineticEnergy(m,vx,vy){{
        return 0.5 * m * (vx*vx + vy*vy);
    }}

    function animate(){{
        aniCtx.clearRect(0,0,aniCvs.width,aniCvs.height);
        drawBoundary();

        if (playing) {{
            // 球-球碰撞
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

            // 边界反弹
            if (x1 - r1 < 0 || x1 + r1 > 600) {{ v1x *= -1; x1 = Math.max(r1, Math.min(600-r1,x1)); }}
            if (y1 - r1 < 0 || y1 + r1 > 400) {{ v1y *= -1; y1 = Math.max(r1, Math.min(400-r1,y1)); }}
            if (x2 - r2 < 0 || x2 + r2 > 600) {{ v2x *= -1; x2 = Math.max(r2, Math.min(600-r2,x2)); }}
            if (y2 - r2 < 0 || y2 + r2 > 400) {{ v2y *= -1; y2 = Math.max(r2, Math.min(400-r2,y2)); }}

            // 更新位置
            x1 += v1x; y1 += v1y;
            x2 += v2x; y2 += v2y;
        }}

        // 绘制小球、箭头
        drawBall(x1, y1, r1, "#4ecdc4");
        drawBall(x2, y2, r2, "#ff6b9d");
        drawArrow(x1, y1, v1x, v1y, "#0066ff");
        drawArrow(x2, y2, v2x, v2y, "#22aa22");

        // ========== 动画内实时显示数据（和运动完全同步）==========
        let ke1 = getKineticEnergy(m1, v1x/speedScale, v1y/speedScale).toFixed(2);
        let ke2 = getKineticEnergy(m2, v2x/speedScale, v2y/speedScale).toFixed(2);
        let keTotal = (parseFloat(ke1) + parseFloat(ke2)).toFixed(2);
        let pTotalX = (m1*(v1x/speedScale) + m2*(v2x/speedScale)).toFixed(2);

        aniCtx.font = "14px Arial";
        aniCtx.fillStyle = "#333";
        aniCtx.fillText("Ball1 KE: "+ke1, 420, 30);
        aniCtx.fillText("Ball2 KE: "+ke2, 420, 55);
        aniCtx.fillText("Total KE: "+keTotal, 420, 80);
        aniCtx.fillText("Total Px: "+pTotalX, 420, 105);
        aniCtx.fillText("e = {e}", 420, 130);

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
        const scale = 4;
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

# 下面原来空白不动的三张曲线图 直接删掉，页面干净不乱
