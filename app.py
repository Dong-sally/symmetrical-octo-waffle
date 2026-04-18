import streamlit as st

st.set_page_config(page_title="完全弹性碰撞仿真", layout="wide")
st.title("完全弹性碰撞 · 物理仿真 + 实时速度曲线")

# 可调参数
m1 = st.slider("物体1 质量(kg)", 0.1, 5.0, 1.0, 0.1)
m2 = st.slider("物体2 质量(kg)", 0.1, 5.0, 2.0, 0.1)
v1_init = st.slider("物体1 初速度(m/s)", -3.0, 3.0, 2.0, 0.1)
v2_init = st.slider("物体2 初速度(m/s)", -3.0, 3.0, -1.0, 0.1)

# 【重点】一边碰撞动画 + 一边实时速度时间曲线，双联动、丝滑不卡顿
html_code = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
body{{background:#f8f9fa;text-align:center;margin:0;padding:10px;}}
#container{{display:flex;justify-content:center;align-items:center;gap:20px;}}
canvas{{background:#fff;border:1px solid #ccc;border-radius:8px;}}
.btn{{padding:8px 22px;margin:6px;font-size:16px;border:none;border-radius:6px;background:#1677ff;color:#fff;cursor:pointer;}}
</style>
</head>
<body>

<div id="container">
    <!-- 左侧：碰撞仿真动画 -->
    <canvas id="aniCanvas" width="700" height="320"></canvas>
    <!-- 右侧：速度-时间图像 -->
    <canvas id="lineCanvas" width="700" height="320"></canvas>
</div>

<div style="margin-top:15px;">
<button class="btn" onclick="play()">▶ 播放</button>
<button class="btn" onclick="pause()">⏸ 暂停</button>
<button class="btn" onclick="reset()">🔄 重置</button>
</div>

<script>
// 物理参数
const m1 = {m1};
const m2 = {m2};
let v1 = {v1_init};
let v2 = {v2_init};
const r = 30;

// 画布
const aniCvs = document.getElementById("aniCanvas");
const aniCtx = aniCvs.getContext("2d");
const lineCvs = document.getElementById("lineCanvas");
const lineCtx = lineCvs.getContext("2d");

let x1 = 120;
let x2 = 380;
let playing = true;

// 速度曲线数据
let tList = [];
let v1List = [];
let v2List = [];
let timeCnt = 0;

// 完全弹性碰撞公式
function collision(){{
    if(Math.abs(x1 - x2) < 2 * r){{
        let nv1 = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2);
        let nv2 = ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2);
        v1 = nv1;
        v2 = nv2;
    }}
}}

// 绘制小球动画
function drawBall(){{
    aniCtx.clearRect(0,0,aniCvs.width,aniCvs.height);
    
    aniCtx.beginPath();
    aniCtx.arc(x1, 160, r, 0, Math.PI*2);
    aniCtx.fillStyle = "#f5222d";
    aniCtx.fill();
    
    aniCtx.beginPath();
    aniCtx.arc(x2, 160, r, 0, Math.PI*2);
    aniCtx.fillStyle = "#2378dd";
    aniCtx.fill();
}}

// 绘制实时速度曲线（中文坐标轴）
function drawLine(){{
    lineCtx.clearRect(0,0,lineCvs.width,lineCvs.height);

    // 坐标轴
    lineCtx.strokeStyle="#999";
    lineCtx.beginPath();
    lineCtx.moveTo(60,30);
    lineCtx.lineTo(60,290);
    lineCtx.lineTo(680,290);
    lineCtx.stroke();

    // 文字标注
    lineCtx.font="14px sans-serif";
    lineCtx.fillStyle="#333";
    lineCtx.fillText("时间",650,310);
    lineCtx.fillText("速度",20,50);

    // 画物体1速度曲线
    lineCtx.strokeStyle="#f5222d";
    lineCtx.beginPath();
    for(let i=0;i<tList.length;i++){{
        let px = 60 + tList[i];
        let py = 160 - v1List[i] * 25;
        if(i===0) lineCtx.moveTo(px,py);
        else lineCtx.lineTo(px,py);
    }}
    lineCtx.stroke();

    // 画物体2速度曲线
    lineCtx.strokeStyle="#2378dd";
    lineCtx.beginPath();
    for(let i=0;i<tList.length;i++){{
        let px = 60 + tList[i];
        let py = 160 - v2List[i] * 25;
        if(i===0) lineCtx.moveTo(px,py);
        else lineCtx.lineTo(px,py);
    }}
    lineCtx.stroke();
}}

// 主更新
function update(){{
    if(!playing){{
        requestAnimationFrame(update);
        return;
    }}

    // 更新位置
    x1 += v1;
    x2 += v2;
    collision();

    // 边界反弹
    if(x1<r||x1>aniCvs.width-r) v1 = -v1;
    if(x2<r||x2>aniCvs.width-r) v2 = -v2;

    // 记录速度数据
    timeCnt += 0.8;
    tList.push(timeCnt);
    v1List.push(v1);
    v2List.push(v2);

    // 限制曲线长度，不溢出
    if(tList.length>700){{
        tList.shift();
        v1List.shift();
        v2List.shift();
    }}

    drawBall();
    drawLine();
    requestAnimationFrame(update);
}}

// 控制函数
function play(){{playing = true;}}
function pause(){{playing = false;}}
function reset(){{
    playing = false;
    x1 = 120;
    x2 = 380;
    v1 = {v1_init};
    v2 = {v2_init};
    tList = [];
    v1List = [];
    v2List = [];
    timeCnt = 0;
    drawBall();
    drawLine();
}}

// 初始化启动
drawBall();
drawLine();
update();
</script>
</body>
</html>
'''

st.components.v1.html(html_code, height=400)
