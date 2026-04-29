import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------- 页面配置 --------------------------
st.set_page_config(
    page_title="1D Perfectly Elastic Collision (Smooth)",
    layout="wide"
)

# -------------------------- 标题与控制按钮 --------------------------
st.title("一维完全弹性碰撞 流畅仿真")

col_play, col_pause, col_reset = st.columns(3)
with col_play:
    st.button("▶️ 播放", use_container_width=True, key="play")
with col_pause:
    st.button("⏸️ 暂停", use_container_width=True, key="pause")
with col_reset:
    st.button("🔄 重置", use_container_width=True, key="reset")

# -------------------------- 右侧参数面板 --------------------------
col_ani, col_param = st.columns([3, 1])
with col_param:
    st.header("参数设置")
    m1 = st.number_input("小球1 质量 (kg)", min_value=0.1, max_value=10.0, value=2.0, step=0.1)
    m2 = st.number_input("小球2 质量 (kg)", min_value=0.1, max_value=10.0, value=5.0, step=0.1)
    v1_initial = st.number_input("小球1 初速度 (m/s)", value=8.0, step=0.1)
    v2_initial = st.number_input("小球2 初速度 (m/s)", value=1.0, step=0.1)
    e = st.slider("恢复系数", min_value=0.0, max_value=1.0, value=1.0, step=0.01)

# -------------------------- 嵌入你截图里的JS流畅动画 --------------------------
with col_ani:
    st.subheader("流畅碰撞动画")
    html_code = f'''
    <div style="display:flex;justify-content:center;">
        <canvas id="aniCanvas" width="600" height="150" style="border:1px solid #eee;"></canvas>
    </div>
    <script>
        // 外部传入参数
        const m1 = {m1};
        const m2 = {m2};
        const e = {e};
        let x1 = 100;
        let x2 = 400;
        let v1 = {v1_initial};
        let v2 = {v2_initial};

        const r = 26;
        let playing = true;
        const dt = 0.05;

        // 获取画布
        const aniCvs = document.getElementById("aniCanvas");
        const aniCtx = aniCvs.getContext("2d");

        // 动画循环
        function animate() {{
            if (!playing) {{
                requestAnimationFrame(animate);
                return;
            }}

            // 碰撞检测与计算
            if (x1 + r > x2 - r) {{
                // 一维弹性碰撞公式
                let v1_new = ((m1 - e*m2)*v1 + (1+e)*m2*v2) / (m1 + m2);
                let v2_new = ((m2 - e*m1)*v2 + (1+e)*m1*v1) / (m1 + m2);
                v1 = v1_new;
                v2 = v2_new;
                // 防止重叠
                x1 = x2 - 2*r - 1;
            }}

            // 边界反弹
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

            // 更新位置
            x1 += v1 * dt * 10;
            x2 += v2 * dt * 10;

            // 绘制
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

# -------------------------- 生成数据并绘制三张曲线 --------------------------
# 一维完全弹性碰撞公式
v1_final = ((m1 - m2) * v1_initial + 2 * m2 * v2_initial) / (m1 + m2)
v2_final = ((m2 - m1) * v2_initial + 2 * m1 * v1_initial) / (m1 + m2)

# 生成时间序列数据
t_total = 0.03
dt_data = 0.0003
t = np.arange(0, t_total, dt_data)
t_collision = t_total * 0.5

# 计算速度、动能、动量
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

# 绘制三张曲线
st.markdown("---")
st.subheader("实时物理曲线")
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

# 1. 速度-时间图
ax1.plot(t, v1_list, color="#ff4b4b", label="小球1 速度")
ax1.plot(t, v2_list, color="#4ecdc4", label="小球2 速度")
ax1.set_title("速度 — 时间 图像")
ax1.set_ylabel("速度 (m/s)")
ax1.legend()
ax1.grid(alpha=0.3)

# 2. 动能-时间图
ax2.plot(t, ke_list, color="#2ca02c")
ax2.set_title("动能 — 时间 图像")
ax2.set_ylabel("动能 (J)")
ax2.grid(alpha=0.3)

# 3. 动量-时间图
ax3.plot(t, p_list, color="#ff7f0e")
ax3.set_title("动量 — 时间 图像")
ax3.set_xlabel("时间 (s)")
ax3.set_ylabel("动量 (kg·m/s)")
ax3.grid(alpha=0.3)

plt.tight_layout()
st.pyplot(fig)
