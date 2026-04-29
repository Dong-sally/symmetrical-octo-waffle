import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------- 页面配置 --------------------------
st.set_page_config(
    page_title="1D Perfectly Elastic Collision (Smooth)",
    layout="wide"
)

# -------------------------- 会话状态：保存按钮状态 --------------------------
if "is_playing" not in st.session_state:
    st.session_state.is_playing = True
if "reset_count" not in st.session_state:
    st.session_state.reset_count = 0

# -------------------------- 标题与控制按钮 --------------------------
st.title("1D Perfectly Elastic Collision Dynamic Simulation")

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

# -------------------------- 右侧参数面板 + 动能数据框 --------------------------
col_ani, col_param = st.columns([3, 1])
with col_param:
    st.header("Parameter Settings")
    m1 = st.number_input("Mass of Ball1 (kg)", min_value=0.1, max_value=10.0, value=2.0, step=0.1, key="m1")
    m2 = st.number_input("Mass of Ball2 (kg)", min_value=0.1, max_value=10.0, value=5.0, step=0.1, key="m2")
    v1_initial = st.number_input("Initial Velocity Ball1 (m/s)", value=8.0, step=0.1, key="v1")
    v2_initial = st.number_input("Initial Velocity Ball2 (m/s)", value=1.0, step=0.1, key="v2")
    e = st.slider("Coefficient of Restitution", min_value=0.0, max_value=1.0, value=1.0, step=0.01, key="e")

    # 动能数据框（英文显示，避免乱码）
    st.markdown("### Kinetic Energy Data")
    ke1_ini = 0.5 * m1 * v1_initial ** 2
    ke2_ini = 0.5 * m2 * v2_initial ** 2
    ke_total_ini = ke1_ini + ke2_ini
    st.info(f"""
Ball1 KE : {ke1_ini:.2f} J  
Ball2 KE : {ke2_ini:.2f} J  
Total KE : {ke_total_ini:.2f} J
""")

# -------------------------- 嵌入带控制的JS流畅动画 --------------------------
with col_ani:
    st.subheader("1D Dynamic Collision Animation")
    playing = st.session_state.is_playing
    reset_key = st.session_state.reset_count

    html_code = f'''
    <div style="display:flex;justify-content:center;">
        <canvas id="aniCanvas" width="600" height="150" style="border:1px solid #eee;"></canvas>
    </div>
    <script>
        const m1 = {m1};
        const m2 = {m2};
        const e = {e};
        const v1_initial = {v1_initial};
        const v2_initial = {v2_initial};
        const resetKey = {reset_key};

        let x1 = 100;
        let x2 = 400;
        let v1 = v1_initial;
        let v2 = v2_initial;
        const r = 26;
        let playing = {str(playing).lower()};
        const dt = 0.05;

        const aniCvs = document.getElementById("aniCanvas");
        const aniCtx = aniCvs.getContext("2d");

        function animate() {{
            if (!playing) {{
                aniCtx.clearRect(0,0,aniCvs.width,aniCvs.height);
                aniCtx.beginPath();
                aniCtx.arc(x1, 75, r, 0, Math.PI*2);
                aniCtx.fillStyle = "#ff4b4b";
                aniCtx.fill();
                aniCtx.beginPath();
                aniCtx.arc(x2, 75, r, 0, Math.PI*2);
                aniCtx.fillStyle = "#4ecdc4";
                aniCtx.fill();
                requestAnimationFrame(animate);
                return;
            }}

            if (x1 + r > x2 - r) {{
                let v1_new = ((m1 - e*m2)*v1 + (1+e)*m2*v2) / (m1 + m2);
                let v2_new = ((m2 - e*m1)*v2 + (1+e)*m1*v1) / (m1 + m2);
                v1 = v1_new;
                v2 = v2_new;
                x1 = x2 - 2*r - 1;
            }}

            if (x1 - r < 0) {{
                v1 = Math.abs(v1);
                x1 = r;
            }}
            if (x1 + r > aniCvs.width) {{
                v1 = -Math.abs(v1);
                x1 = aniCvs.width - r;
            }}
            if (x2 - r < 0) {{
                v2 = Math.abs(v2);
                x2 = r;
            }}
            if (x2 + r > aniCvs.width) {{
                v2 = -Math.abs(v2);
                x2 = aniCvs.width - r;
            }}

            x1 += v1 * dt * 10;
            x2 += v2 * dt * 10;

            aniCtx.clearRect(0,0,aniCvs.width,aniCvs.height);
            aniCtx.beginPath();
            aniCtx.arc(x1, 75, r, 0, Math.PI*2);
            aniCtx.fillStyle = "#ff4b4b";
            aniCtx.fill();
            aniCtx.beginPath();
            aniCtx.arc(x2, 75, r, 0, Math.PI*2);
            aniCtx.fillStyle = "#4ecdc4";
            aniCtx.fill();

            requestAnimationFrame(animate);
        }}
        animate();
    </script>
    '''
    st.components.v1.html(html_code, height=200)

# -------------------------- 生成数据并绘制三张曲线（全部英文，无乱码） --------------------------
v1_final = ((m1 - m2) * v1_initial + 2 * m2 * v2_initial) / (m1 + m2)
v2_final = ((m2 - m1) * v2_initial + 2 * m1 * v1_initial) / (m1 + m2)

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
        cv1 = v1_initial
        cv2 = v2_initial
    else:
        cv1 = v1_final
        cv2 = v2_final
    
    ke = 0.5 * m1 * cv1**2 + 0.5 * m2 * cv2**2
    p = m1 * cv1 + m2 * cv2
    
    v1_list.append(cv1)
    v2_list.append(cv2)
    ke_list.append(ke)
    p_list.append(p)

# 三张图：全部英文标题、标签、图例，无任何中文
st.markdown("---")
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9, 5), sharex=True)

# 1. Velocity - Time
ax1.plot(t, v1_list, color="#ff4b4b", label="Ball1")
ax1.plot(t, v2_list, color="#4ecdc4", label="Ball2")
ax1.set_title("Velocity - Time")
ax1.set_ylabel("Velocity (m/s)")
ax1.legend()
ax1.grid(alpha=0.3)

# 2. Kinetic Energy - Time
ax2.plot(t, ke_list, color="#2ca02c")
ax2.set_title("Kinetic Energy - Time")
ax2.set_ylabel("KE (J)")
ax2.grid(alpha=0.3)

# 3. Momentum - Time
ax3.plot(t, p_list, color="#ff7f0e")
ax3.set_title("Momentum - Time")
ax3.set_xlabel("Time (s)")
ax3.set_ylabel("Momentum (kg·m/s)")
ax3.grid(alpha=0.3)

plt.tight_layout()
st.pyplot(fig)
