import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 【关键】放弃中文，直接英文，永久解决乱码
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 初始化状态
if "frame" not in st.session_state:
    st.session_state.frame = 0
if "run" not in st.session_state:
    st.session_state.run = False

st.title("Perfectly Elastic Collision Simulation")

# 参数
m1 = st.slider("Mass 1 (kg)", 0.1, 5.0, 1.0, 0.1)
m2 = st.slider("Mass 2 (kg)", 0.1, 5.0, 2.0, 0.1)
v1 = st.slider("Velocity 1 (m/s)", -5.0, 5.0, 3.0, 0.1)
v2 = st.slider("Velocity 2 (m/s)", -5.0, 5.0, -1.0, 0.1)

r = 0.3
dt = 0.06
t_total = 6
steps = int(t_total / dt)

# 预计算轨迹
def calc_data():
    x1, x2 = 0.0, 3.2
    X1, X2, V1, V2 = np.zeros(steps), np.zeros(steps), np.zeros(steps), np.zeros(steps)
    for i in range(steps):
        X1[i] = x1
        X2[i] = x2
        V1[i] = v1
        V2[i] = v2

        x1 += v1 * dt
        x2 += v2 * dt

        if abs(x1 - x2) <= 2*r:
            nv1 = ((m1-m2)*v1 + 2*m2*v2)/(m1+m2)
            nv2 = ((m2-m1)*v2 + 2*m1*v1)/(m1+m2)
            v1, v2 = nv1, nv2
    return X1,X2,V1,V2

x1_arr,x2_arr,v1_arr,v2_arr = calc_data()
t_arr = np.linspace(0,t_total,steps)

# 按钮
c1,c2,c3 = st.columns(3)
with c1:
    if st.button("Play"):
        st.session_state.run = True
with c2:
    if st.button("Pause"):
        st.session_state.run = False
with c3:
    if st.button("Reset"):
        st.session_state.run = False
        st.session_state.frame = 0

# 帧数递进
if st.session_state.run:
    st.session_state.frame += 1
    if st.session_state.frame >= steps:
        st.session_state.frame = 0

f = st.session_state.frame

# 绘图（全部英文，绝不乱码）
fig,(ax1,ax2) = plt.subplots(1,2,figsize=(12,5))

ax1.set_xlim(-1,10)
ax1.set_ylim(-1,1)
ax1.set_title("Collision Process")
ax1.set_xlabel("Position (m)")
ax1.set_ylabel("Y")
ax1.scatter(x1_arr[f],0,c="red",s=160,label="Object 1")
ax1.scatter(x2_arr[f],0,c="blue",s=160,label="Object 2")
ax1.legend()
ax1.grid(alpha=0.3)

ax2.set_title("Velocity - Time Curve")
ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Velocity (m/s)")
ax2.plot(t_arr,v1_arr,"r-",label="Object1 velocity")
ax2.plot(t_arr,v2_arr,"b-",label="Object2 velocity")
ax2.scatter(t_arr[f],v1_arr[f],c="red",s=30)
ax2.scatter(t_arr[f],v2_arr[f],c="blue",s=30)
ax2.legend()
ax2.grid(alpha=0.3)

st.pyplot(fig)

# 放慢刷新频率，解决卡顿、一顿一顿
if st.session_state.run:
    import time
    time.sleep(0.08)
    st.rerun()
