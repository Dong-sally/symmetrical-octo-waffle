import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ============ 解决Streamlit中文显示 + 负号 ============
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False

# ============ 初始化会话状态（存放播放/暂停/帧数） ============
if "frame" not in st.session_state:
    st.session_state.frame = 0
if "play" not in st.session_state:
    st.session_state.play = False

# ============ 页面标题 + 参数滑块 ============
st.title("完全弹性碰撞仿真实验")

m1 = st.slider("物体1 质量(kg)", 0.1, 5.0, 1.0, 0.1)
m2 = st.slider("物体2 质量(kg)", 0.1, 5.0, 2.0, 0.1)
v1 = st.slider("物体1 初速度(m/s)", -5.0, 5.0, 3.0, 0.1)
v2 = st.slider("物体2 初速度(m/s)", -5.0, 5.0, -1.0, 0.1)

# 固定物理参数
r = 0.3
dt = 0.05
t_total = 6
steps = int(t_total / dt)

# ============ 预计算整个碰撞全过程数据 ============
def get_data(m1,m2,v1,v2):
    x1, x2 = 0.0, 3.2
    x1_list = np.zeros(steps)
    x2_list = np.zeros(steps)
    v1_list = np.zeros(steps)
    v2_list = np.zeros(steps)

    x1_list[0] = x1
    x2_list[0] = x2
    v1_list[0] = v1
    v2_list[0] = v2

    for i in range(1, steps):
        x1 += v1 * dt
        x2 += v2 * dt

        # 完全弹性碰撞判定+速度交换
        if abs(x1 - x2) <= 2*r:
            nv1 = ((m1-m2)*v1 + 2*m2*v2)/(m1+m2)
            nv2 = ((m2-m1)*v2 + 2*m1*v1)/(m1+m2)
            v1, v2 = nv1, nv2

        x1_list[i] = x1
        x2_list[i] = x2
        v1_list[i] = v1
        v2_list[i] = v2

    return x1_list, x2_list, v1_list, v2_list

x1_arr, x2_arr, v1_arr, v2_arr = get_data(m1,m2,v1,v2)
t_arr = np.linspace(0, t_total, steps)

# ============ 按钮区：播放 / 暂停 / 重置 ============
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("▶ 播放"):
        st.session_state.play = True
with col2:
    if st.button("⏸ 暂停"):
        st.session_state.play = False
with col3:
    if st.button("🔄 重置"):
        st.session_state.play = False
        st.session_state.frame = 0

# 自动递增帧数（播放状态才动）
if st.session_state.play:
    st.session_state.frame += 1
    if st.session_state.frame >= steps:
        st.session_state.frame = 0

# ============ 绘制当前帧图像（全中文） ============
now = st.session_state.frame

fig, (ax1, ax2) = plt.subplots(1,2,figsize=(12,5))

# 左图：碰撞动画场景
ax1.set_xlim(-1,10)
ax1.set_ylim(-1,1)
ax1.set_title("碰撞过程仿真", fontsize=14)
ax1.set_xlabel("位置（米）")
ax1.set_ylabel("竖直方向")
ax1.scatter(x1_arr[now], 0, color="red", s=150, label="物体1")
ax1.scatter(x2_arr[now], 0, color="blue", s=150, label="物体2")
ax1.legend()
ax1.grid(True,alpha=0.3)

# 右图：速度时间曲线
ax2.set_title("速度-时间变化曲线", fontsize=14)
ax2.set_xlabel("时间（秒）")
ax2.set_ylabel("速度（m/s）")
ax2.plot(t_arr, v1_arr, "r-", label="物体1速度")
ax2.plot(t_arr, v2_arr, "b-", label="物体2速度")
ax2.scatter(t_arr[now], v1_arr[now], c="red",s=30)
ax2.scatter(t_arr[now], v2_arr[now], c="blue",s=30)
ax2.legend()
ax2.grid(True,alpha=0.3)

st.pyplot(fig)

# 页面自动刷新，实现动画连贯
if st.session_state.play:
    st.experimental_rerun()
