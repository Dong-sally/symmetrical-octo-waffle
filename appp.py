import streamlit as st

st.set_page_config(layout="wide", page_title="一维碰撞仿真 | PhET风格布局")
st.title("一维对心碰撞仿真（弹性/非弹性/完全非弹性）")

# 顶部参数输入区
col1, col2, col3 = st.columns(3)
with col1:
    m1 = st.number_input("小球1 质量 m1 (kg)", value=0.5, step=0.1)
    x1_0 = st.number_input("小球1 初始位置 x1₀", value=80.0, step=1.0)
    v1_0 = st.number_input("小球1 初始速度 v1₀ (m/s)", value=6.0, step=0.5)
with col2:
    m2 = st.number_input("小球2 质量 m2 (kg)", value=1.5, step=0.1)
    x2_0 = st.number_input("小球2 初始位置 x2₀", value=300.0, step=1.0)
    v2_0 = st.number_input("小球2 初始速度 v2₀ (m/s)", value=-2.0, step=0.5)
with col3:
    e = st.number_input("碰撞恢复系数 e (0~1)", min_value=0.0, max_value=1.0, value=0.8, step=0.05)

# 整体布局：上动画+下三图，右侧数据
left_main, right_data = st.columns([2.5, 1])

html_code = f'''
<!DOCTYPE html>
<html>
<head>
<style>
body {{margin:0;padding:0;font-family:sans-serif;background:#f9f9f9;}}
/* 整体布局 */
.top-row{{display:flex;gap:20px;padding:10px;}}
.ani-wrap{{flex:2.5;}}
.data-wrap{{flex:1;background:#fff;border:1px solid #ddd;border-radius:8px;padding:15px;}}
.bottom-charts{{padding:10px;display:flex;flex-direction:column;gap:15px;}}
/* 数据面板样式，和PhET一致 */
.data-row{{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #eee;}}
.data-label{{color:#555;}}
.data-value{{font-weight:bold;color:#222;}}
.controls{{margin:10px 0;text-align:center;}}
button{{padding:8px 20px;margin:0 8px;border:none;border-radius:6px;background:#2196F3;color:#fff;cursor:pointer;font-size:15px;}}
canvas{{background:#fff;border:1px solid #ddd;border-radius:8px;width:100%;}}
</style>
</head>
<body>

<!-- 上半部分：动画 + 右侧数据 -->
<div class="top-row">
    <div class="ani-wrap">
        <div class="controls">
            <button onclick="play()">播放</button>
            <button onclick="pause()">暂停</button>
            <button onclick="reset()">重置</button>
        </div>
        <canvas id="aniCanvas" height="220"></canvas>
    </div>

    <!-- 右侧逐条数据面板 -->
    <div class="data-wrap">
        <h4 style="margin-top:0;">实时数据面板</h4>
        <div class="data-row">
            <span class="data-label">小球1 质量 (kg)</span>
            <span class="data-value" id="m1_val">{m1}</span>
        </div>
        <div class="data-row">
            <span class="data-label">小球2 质量 (kg)</span>
            <span class="data-value" id="m2_val">{m2}</span>
        </div>
        <div class="data-row">
            <span class="data-label">恢复系数 e</span>
            <span class="data-value" id="e_val">{e}</span>
        </div>
        <hr>
        <div class="data-row">
            <span class="data-label">小球1 位置 (m)</span>
            <span class="data-value" id="x1_val">0.00</span>
        </div>
        <div class="data-row">
            <span class="data-label">小球2 位置 (m)</span>
            <span class="data-value" id="x2_val">0.00</span>
        </div>
        <div class="data-row">
            <span class="data-label">小球1 速度 (m/s)</span>
            <span class="data-value" id="v1_val">0.00</span>
        </div>
        <div class="data-row">
            <span class="data-label">小球2 速度 (m/s)</span>
            <span class="data-value" id="v2_val">0.00</span>
        </div>
        <hr>
        <div class="data-row">
            <span class="data-label">小球1 动量 (kg·m/s)</span>
            <span class="data-value" id="p1_val">0.00</span>
        </div>
        <div class="data-row">
            <span class="data-label">小球2 动量 (kg·m/s)</span>
            <span class="data-value" id="p2_val">0.00</span>
        </div>
        <div class="data-row">
            <span class="data-label">系统总动量</span>
            <span class="data-value" id="pt_val">0.00</span>
        </div>
        <hr>
        <div class="data-row">
            <span class="data-label">小球1 动能 (J)</span>
            <span class="data-value" id="ek1_val">0.00</span>
        </div>
        <div class="data-row">
            <span class="data-label">小球2 动能 (J)</span>
            <span class="data-value" id="ek2_val">0.00</span>
        </div>
        <div class="data-row">
            <span class="data-label">系统总动能</span>
            <span class="data-value" id="ekt_val">0.00</span>
        </div>
    </div>
</div>

<!-- 下半部分：三张曲线图 -->
<div class="bottom-charts">
    <canvas id="velCanvas" height="160"></canvas>
    <canvas id="ekCanvas" height="160"></canvas>
    <canvas id="momCanvas" height="160"></canvas>
</div>

<script>
// 物理参数
const m1 = {m1};
const m2 = {m2};
const e  = {e};

let x1  = {x1_0};
let x2  = {x2_0};
let v1  = {v1_0};
let v2  = {v2_0};
const r = 26;

let playing = true;
const dt = 0.05;

// 绘图数据记录
let t = 0;
let tList = [];
let v1List=[],v2List=[];
let ek1List=[],ek2List=[],ekSumList=[];
let p1List=[],p2List=[],pTotalList=[];

// 画布DOM
const aniCvs = document.getElementById("aniCanvas");
const aniCtx = aniCvs.getContext("2d");

const velCvs = document.getElementById("velCanvas");
const velCtx = velCvs.getContext("2d");

const ekCvs = document.getElementById("ekCanvas");
const ekCtx = ekCvs.getContext("2d");

const momCvs = document.getElementById("momCanvas");
const momCtx = momCvs.getContext("2d");

// 数据DOM
const x1Val = document.getElementById("x1_val");
const x2Val = document.getElementById("x2_val");
const v1Val = document.getElementById("v1_val");
const v2Val = document.getElementById("v2_val");
const p1Val = document.getElementById("p1_val");
const p2Val = document.getElementById("p2_val");
const ptVal = document.getElementById("pt_val");
const ek1Val = document.getElementById("ek1_val");
const ek2Val = document.getElementById("ek2_val");
const ektVal = document.getElementById("ekt_val");

// 防抖刷新数据（解决闪屏）
let lastUpdate = 0;
function updateData(){{
    const now = Date.now();
    if (now - lastUpdate < 100) return; // 100ms刷新一次，不闪
    lastUpdate = now;

    let p1 = m1 * v1;
    let p2 = m2 * v2;
    let pt = p1 + p2;
    let ek1 = 0.5 * m1 * v1 * v1;
    let ek2 = 0.5 * m2 * v2 * v2;
    let ekt = ek1 + ek2;

    x1Val.innerText = x1.toFixed(2);
    x2Val.innerText = x2.toFixed(2);
    v1Val.innerText = v1.toFixed(2);
    v2Val.innerText = v2.toFixed(2);
    p1Val.innerText = p1.toFixed(2);
    p2Val.innerText = p2.toFixed(2);
    ptVal.innerText = pt.toFixed(2);
    ek1Val.innerText = ek1.toFixed(2);
    ek2Val.innerText = ek2.toFixed(2);
    ektVal.innerText = ekt.toFixed(2);
}}

// 碰撞计算
function collideOneDim(){{
    if(Math.abs(x1 - x2) < 2*r){{
        let v1New = ((m1 - e*m2)*v1 + (1+e)*m2*v2) / (m1 + m2);
        let v2New = ((m2 - e*m1)*v2 + (1+e)*m1*v1) / (m1 + m2);
        v1 = v1New;
        v2 = v2New;
    }}
}}

// 边界反弹
function boundaryBounce(){{
    if(x1 < r || x1 > aniCvs.width - r) v1 = -v1;
    if(x2 < r || x2 > aniCvs.width - r) v2 = -v2;
}}

// 绘制小球
function drawBall(){{
    aniCtx.clearRect(0,0,aniCvs.width,aniCvs.height);
    aniCtx.beginPath();
    aniCtx.moveTo(0, aniCvs.height/2);
    aniCtx.lineTo(aniCvs.width, aniCvs.height/2);
    aniCtx.strokeStyle="#ccc";
    aniCtx.stroke();
    aniCtx.beginPath();
    aniCtx.arc(x1, aniCvs.height/2, r, 0, Math.PI*2);
    aniCtx.fillStyle="#f44336"; aniCtx.fill();
    aniCtx.beginPath();
    aniCtx.arc(x2, aniCvs.height/2, r, 0, Math.PI*2);
    aniCtx.fillStyle="#2196F3"; aniCtx.fill();
}}

// 带坐标轴刻度的通用绘图函数
function drawAxis(ctx, cvs, title, isZeroCenter=false){{
    const w = cvs.width, h = cvs.height;
    const ox = 40, oy = isZeroCenter ? h/2 : h-25;
    ctx.clearRect(0,0,w,h);
    ctx.strokeStyle="#ccc";
    ctx.beginPath();
    ctx.moveTo(ox,15); ctx.lineTo(ox,h-15); ctx.moveTo(ox,oy); ctx.lineTo(w-10,oy);
    ctx.stroke();
    ctx.fillStyle="#555";
    ctx.fillText(title, 45, 18);
}}

// 速度-时间图
function drawVelChart(){{
    drawAxis(velCtx, velCvs, "速度-时间 (m/s)", true);
    velCtx.strokeStyle="#f44336";
    velCtx.beginPath();
    for(let i=0;i<tList.length;i++){{
        let px = 40 + tList[i]*8;
        let py = velCvs.height/2 - v1List[i]*5;
        i===0 ? velCtx.moveTo(px,py) : velCtx.lineTo(px,py);
    }}
    velCtx.stroke();

    velCtx.strokeStyle="#2196F3";
    velCtx.beginPath();
    for(let i=0;i<tList.length;i++){{
        let px = 40 + tList[i]*8;
        let py = velCvs.height/2 - v2List[i]*5;
        i===0 ? velCtx.moveTo(px,py) : velCtx.lineTo(px,py);
    }}
    velCtx.stroke();
}}

// 动能-时间图
function drawEkChart(){{
    drawAxis(ekCtx, ekCvs, "动能-时间 (J)", false);
    ekCtx.strokeStyle="#f44336";
    ekCtx.beginPath();
    for(let i=0;i<tList.length;i++){{
        let px = 40 + tList[i]*8;
        let py = ekCvs.height-25 - ek1List[i]*1.5;
        i===0 ? ekCtx.moveTo(px,py) : ekCtx.lineTo(px,py);
    }}
    ekCtx.stroke();

    ekCtx.strokeStyle="#2196F3";
    ekCtx.beginPath();
    for(let i=0;i<tList.length;i++){{
        let px = 40 + tList[i]*8;
        let py = ekCvs.height-25 - ek2List[i]*1.5;
        i===0 ? ekCtx.moveTo(px,py) : ekCtx.lineTo(px,py);
    }}
    ekCtx.stroke();

    ekCtx.strokeStyle="#666";
    ekCtx.setLineDash([4,4]);
    ekCtx.beginPath();
    for(let i=0;i<tList.length;i++){{
        let px = 40 + tList[i]*8;
        let py = ekCvs.height-25 - ekSumList[i]*1.5;
        i===0 ? ekCtx.moveTo(px,py) : ekCtx.lineTo(px,py);
    }}
    ekCtx.stroke();
    ekCtx.setLineDash([]);
}}

// 动量-时间图
function drawMomChart(){{
    drawAxis(momCtx, momCvs, "动量-时间 (kg·m/s)", true);
    momCtx.strokeStyle="#f44336";
    momCtx.beginPath();
    for(let i=0;i<tList.length;i++){{
        let px = 40 + tList[i]*8;
        let py = momCvs.height/2 - p1List[i]*2.5;
        i===0 ? momCtx.moveTo(px,py) : momCtx.lineTo(px,py);
    }}
    momCtx.stroke();

    momCtx.strokeStyle="#2196F3";
    momCtx.beginPath();
    for(let i=0;i<tList.length;i++){{
        let px = 40 + tList[i]*8;
        let py = momCvs.height/2 - p2List[i]*2.5;
        i===0 ? momCtx.moveTo(px,py) : momCtx.lineTo(px,py);
    }}
    momCtx.stroke();

    momCtx.strokeStyle="#444";
    momCtx.setLineDash([4,4]);
    momCtx.beginPath();
    for(let i=0;i<tList.length;i++){{
        let px = 40 + tList[i]*8;
        let py = momCvs.height/2 - pTotalList[i]*2.5;
        i===0 ? momCtx.moveTo(px,py) : momCtx.lineTo(px,py);
    }}
    momCtx.stroke();
    momCtx.setLineDash([]);
}}

// 主动画循环
function update(){{
    if(playing){{
        x1 += v1 * dt * 2;
        x2 += v2 * dt * 2;

        collideOneDim();
        boundaryBounce();

        t += dt;
        let p1 = m1*v1;
        let p2 = m2*v2;
        let pt = p1+p2;
        let ek1 = 0.5*m1*v1*v1;
        let ek2 = 0.5*m2*v2*v2;
        let ekt = ek1+ek2;

        tList.push(t);
        v1List.push(v1);v2List.push(v2);
        ek1List.push(ek1);ek2List.push(ek2);ekSumList.push(ekt);
        p1List.push(p1);p2List.push(p2);pTotalList.push(pt);

        if(tList.length>600){{
            tList.shift();v1List.shift();v2List.shift();
            ek1List.shift();ek2List.shift();ekSumList.shift();
            p1List.shift();p2List.shift();pTotalList.shift();
        }}

        updateData();
    }}

    drawBall();
    drawVelChart();
    drawEkChart();
    drawMomChart();

    requestAnimationFrame(update);
}}

// 控制函数
function play(){{playing=true;}}
function pause(){{playing=false;}}
function reset(){{
    playing=false;
    x1={x1_0};x2={x2_0};
    v1={v1_0};v2={v2_0};
    t=0;
    tList=[];
    v1List=[];v2List=[];
    ek1List=[];ek2List=[];ekSumList=[];
    p1List=[];p2List=[];pTotalList=[];

    updateData();
    drawBall();drawVelChart();drawEkChart();drawMomChart();
}}

// 初始化
updateData();
drawBall();drawVelChart();drawEkChart();drawMomChart();
update();
</script>
</body>
</html>
'''

with left_main:
    st.components.v1.html(html_code, height=850)

with right_data:
    st.empty()
