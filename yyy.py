import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

# 页面配置
st.set_page_config(
    page_title="一维完全弹性碰撞仿真",
    layout="wide"
)

# ===================== 状态初始化 =====================
if "run" not in st.session_state:
    st.session_state.run = False
if "idx" not in st.session_state:
    st.session_state.idx = 0
if "param_change" not in st.session_state:
    st.session_state.param_change = True

# ===================== 标题 + 顶部控制按钮（置顶！）=====================
st.title("一维完全弹性碰撞 连续动态仿真")

# 按钮放在标题正下方，不再靠下
c1, c2, c3 = st.columns(3)
with c1:
    play_btn = st.button("▶️ 播放", use_container_width=True)
with c2:
    pause_btn = st.button("⏸️ 暂停", use_container_width=True)
with c3:
    reset_btn = st.button("🔄 重置", use_container_width=True)

# 按钮逻辑
if play_btn:
    st.session_state.run = True
if pause_btn:
    st.session_state.run = False
if reset_btn:
    st.session_state.run = False
    st.session_state.idx = 0
    st.session_state.param_change = True

# ===================== 布局：左动画 | 右参数 =====================
col_ani, col_cfg = st.columns([2, 1])

with col_cfg:
    st.header("⚙️ 两球参数设置")
    m1 = st.number_input("小球1 质量(kg)", min_value=0.1, max_value=10.0, value=2.0, step=0.1)
    m2 = st.number_input("小球2 质量(kg)", min_value=0.1, max_value=10.0, value=5.0, step=0.1)
    v1_0 = st.number_input("小球1 初速度(m/s)", value=8.0, step=0.1)
    v2_0 = st.number_input("小球2 初速度(m/s)", value=1.0, step=0.1)

    # 一维完全弹性碰撞公式
       v1_end = ((m1 - m2) * v1_0 + 2 * m2 * v2_0) / (m1 + m2)
    v2_end = ((m2 - m1) * v2_0 + 2 * m1 * v1_0) / (m1 + m2)

    st.markdown("### 碰撞后速度")
    st.write(f"球1 末速度：{v1_end:.2f} m/s")
    st.write(f"球2 末速度：{v2_end:.2f} m/s")

# ===================== 仿真数据生成 =====================
t_total = 0.03
dt = 0.0003
t_arr = np.arange(0, t_total, dt)
t_cross = t_total / 2

# 参数变动/重置 重新生成数据
if st.session_state.param_change:
    x1_list = []
    x2_list = []
    v1_list = []
    v2_list = []
    ek_list = []
    px_list = []

    x1_s = 2.0
    x2_s = 7.0

    for ti in t_arr:
        if ti < t_cross:
            x1 = x1_s + v1_0 * ti
            x2 = x2_s + v2_0 * ti
            cv1 = v1_0
            cv2 = v2_0
        else:
            dt_ = ti - t_cross
            x1 = x1_s + v1_0*t_cross + v1_end*dt_
            x2 = x2_s + v2_0*t_cross + v2_end*dt_
            cv1 = v1_end
            cv2 = v2_end

        # 动能
        ek = 0.5*m1*cv1**2 + 0.5*m2*cv2**2
        # 总动量
        px = m1*cv1 + m2*cv2

        x1_list.append(x1)
        x2_list.append(x2)
        v1_list.append(cv1)
        v2_list.append(cv2)
        ek_list.append(ek)
        px_list.append(px)

    # 存入会话
    st.session_state.x1_list = x1_list
    st.session_state.x2_list = x2_list
    st.session_state.v1_list = v1_list
    st.session_state.v2_list = v2_list
    st.session_state.ek_list = ek_list
    st.session_state.px_list = px_list
    st.session_state.t_arr = t_arr
    st.session_state.idx = 0
    st.session_state.param_change = False

# 取出数据
x1_list = st.session_state.x1_list
x2_list = st.session_state.x2_list
v1_list = st.session_state.v1_list
v2_list = st.session_state.v2_list
ek_list = st.session_state.ek_list
px_list = st.session_state.px_list
t_arr = st.session_state.t_arr
idx = st.session_state.idx

# ===================== 左侧一维动画 =====================
with col_ani:
    st.subheader("🎬 一维碰撞动态动画")
    fig_ani, ax_ani = plt.subplots(figsize=(10,2.5))
    ax_ani.set_xlim(0, 12)
    ax_ani.set_ylim(0, 1.5)
    ax_ani.set_yticks([])
    ax_ani.set_xlabel("位置 X (m)")

    b1 = Circle((x1_list[idx], 0.75), 0.25, color="#ff4b4b", label="小球1")
    b2 = Circle((x2_list[idx], 0.75), 0.25, color="#4ecdc4", label="小球2")
    ax_ani.add_patch(b1)
    ax_ani.add_patch(b2)
    ax_ani.legend(loc="upper right")

    ani_place = st.pyplot(fig_ani)

# ===================== 下方三张图：速度-时间 / 动能-时间 / 动量-时间 =====================
st.markdown("---")
st.subheader("📊 实时物理曲线")
fig_all, (ax_v, ax_ek, ax_p) = plt.subplots(3,1, figsize=(9,8), sharex=True)

# 1. 速度-时间图像
ax_v.set_title("速度 — 时间 图像")
ax_v.plot(t_arr[:idx+1], v1_list[:idx+1], color="red", label="球1 速度")
ax_v.plot(t_arr[:idx+1], v2_list[:idx+1], color="teal", label="球2 速度")
ax_v.grid(alpha=0.3)
ax_v.legend()
ax_v.set_ylabel("速度 m/s")

# 2. 动能-时间图像
ax_ek.set_title("动能 — 时间 图像")
ax_ek.plot(t_arr[:idx+1], ek_list[:idx+1], color="green")
ax_ek.grid(alpha=0.3)
ax_ek.set_ylabel("动能 J")

# 3. 动量-时间图像
ax_p.set_title("动量 — 时间 图像")
ax_p.plot(t_arr[:idx+1], px_list[:idx+1], color="orange")
ax_p.grid(alpha=0.3)
ax_p.set_ylabel("动量 kg·m/s")
ax_p.set_xlabel("时间 s")

plt.tight_layout()
plot_place = st.pyplot(fig_all)

# ===================== 流畅动画更新（解决卡顿）=====================
if st.session_state.run:
    if idx < len(t_arr)-1:
        st.session_state.idx += 1
        st.rerun()
    else:
        st.session_state.run = False
        st.info("仿真播放完毕，请点击重置重新运行")
