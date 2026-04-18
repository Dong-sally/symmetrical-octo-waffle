import streamlit as st

# 页面基础设置
st.set_page_config(page_title="对心完全弹性碰撞仿真", layout="wide")
st.title("对心完全弹性碰撞 物理仿真动画")

# 获取用户参数
m1 = st.slider("物体1 质量(kg)", 0.1, 5.0, 1.0, 0.1)
m2 = st.slider("物体2 质量(kg)", 0.1, 5.0, 2.0, 0.1)
v1 = st.slider("物体1 初速度(m/s)", -3.0, 3.0, 2.0, 0.1)
v2 = st.slider("物体2 初速度(m/s)", -3.0, 3.0, -1.0, 0.1)

# HTML+JS 原生动画，丝滑不卡顿、支持中文、自带播放暂停重置
html_code = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
body {{text-align:center;background:#f5f5f5;}}
canvas {{background:white;border:1px solid #ccc;margin:10px auto;}}
.btn {{padding:8px 20px;margin:5px;font-size:16px;cursor:pointer;border:none;border-radius:6px;background:#409eff;color:white;}}
</style>
</head>
<body>
<canvas id="canvas" width="800" height="300"></canvas>
<div>
<button class="btn" onclick="play()">播放</button>
<button class="btn" onclick="pause()">暂停</button>
<button class="btn" onclick="reset()">重置</button>
</div>

<script>
const m1 = {m1};
const m2 = {m2};
let v1 = {v1};
let v2 = {v2};
const r = 30;

const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

let x1 = 150;
let x2 = 450;
let playing = true;

// 完全弹性碰撞公式
function collide(){{
    if(Math.abs(x1 - x2) < 2*r){{
        let nv1 = ((m1 - m2)*v1 + 2*m2*v2)/(m1 + m2);
        let nv2 = ((m2 - m1)*v2 + 2*m1*v1)/(m1 + m2);
        v1 = nv1;
        v2 = nv2;
    }}
}}

function draw(){{
    ctx.clearRect(0,0,canvas.width,canvas.height);
    // 物体1 红色
    ctx.beginPath();
    ctx.arc(x1, 150, r, 0, Math.PI*2);
    ctx.fillStyle="red"; ctx.fill();
    // 物体2 蓝色
    ctx.beginPath();
    ctx.arc(x2, 150, r, 0, Math.PI*2);
    ctx.fillStyle="blue"; ctx.fill();
}}

function update(){{
    if(!playing) return;
    x1 += v1;
    x2 += v2;
    collide();

    // 边界回弹
    if(x1<r||x1>canvas.width-r) v1=-v1;
    if(x2<r||x2>canvas.width-r) v2=-v2;

    draw();
    requestAnimationFrame(update);
}}

function play(){{playing=true;}}
function pause(){{playing=false;}}
function reset(){{
    x1=150;x2=450;
    v1={v1};v2={v2};
    draw();
}}

draw();
update();
</script>
</body>
</html>
'''

# 嵌入网页动画
st.components.v1.html(html_code, height=420)

st.markdown("""
### 说明
- 支持 **播放 / 暂停 / 重置**
- 小球碰撞遵循【完全弹性碰撞】物理公式
- 中文全部正常显示，无乱码
- 动画原生JS渲染，丝滑不卡顿
- 生成链接手机、电脑直接打开使用
""")
