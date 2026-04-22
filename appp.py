import streamlit as st

st.set_page_config(layout="wide", page_title="一维碰撞仿真 | 布局重构版")
st.title("一维对心碰撞仿真（弹性/非弹性/完全非弹性）")

# 顶部参数输入区
col1, col2, col3 = st.columns(3)
with col1:
    m1 = st.number_input("小球1 质量 m1 (kg)", value=1.0, step=0.1)
    x1_0 = st.number_input("小球1 初始位置 x1₀", value=80.0, step=1.0)
    v1_0 = st.number_input("小球1 初始速度 v1₀ (m/s)", value=6.0, step=0.5)
with col2:
    m2 = st.number_input("小球2 质量 m2 (kg)", value=3.0, step=0.1)
    x2_0 = st.number_input("小球2 初始位置 x2₀", value=300.0, step=1.0)
    v2_0 = st.number_input("小球2 初始速度 v2₀ (m/s)", value=-2.0, step=0.5)
with col3:
    e = st.number_input("碰撞恢复系数 e (0~1)", min_value=0.0, max_value=1.0, value=0.8, step=0.05)

# 整体左右分栏：左边动画+三张图，右边全部数据总面板
left_col, right_col = st.columns([2.2, 1])

html_code = f'''
<!DOCTYPE html>
<html>
<head>
<style>
body {{margin:0;padding:0;font-family:sans-serif;background:#f9f9f9;}}
/* 左侧：动画 + 三张图表垂直排列 */
.left-wrap{{width:100%;display:flex;flex-direction:column;gap:15px;}}
/* 右侧：超大整块数据面板 */
.right-data{{
    background:#f0f7ff;
    padding:20px;
    border-radius:10px;
    border:1px solid #cce0f5;
    font-size:15px;
    line-height:2.2;
}}
.ani-box{{width:100%;}}
canvas{{background:#fff;border:1px solid #ddd;border-radius:8px;width:100%;}}
.controls{{margin:10px 0;text-align:center;}}
button{{padding:8px 20px;margin:0 8px;border:none;border-radius:6px;background:#2196F3;color:#fff;cursor:pointer;font-size:15px;}}
h4{{margin:5px 0;color:#1976D2;}}
</style>
</head>
<body>

<div style="display:flex;gap:20px;">
    <!-- 左侧：上动画 + 下依次：速度→动能→动量 三张图 -->
    <div class="left-wrap">
        <div class="controls">
            <button onclick="play()">播放</button>
            <button onclick="pause()">暂停</button>
            <button onclick="reset()">重置</button>
        </div>

        <!-- 1. 一维碰撞动态动画（左上） -->
        <div class="ani-box">
            <canvas id="aniCanvas" height="200"></canvas>
        </div>

        <!-- 2. 速度-时间图像 -->
        <div>
            <canvas id="velCanvas" height="180"></canvas>
        </div>

        <!-- 3. 动能-时间图像 -->
        <div>
            <canvas id="ekCanvas" height="180"></canvas>
        </div>

        <!-- 4. 动量-时间图像 -->
        <div>
            <canvas id="momCanvas" height="180"></canvas>
        </div>
    </div>

    <!-- 右侧：整合所有参数+实时数据大面板 -->
    <div class="right-data">
        <h4>【初始设置参数】</h4>
        小球1 质量 m1 = <span id="side_m1">{m1}</span> kg<br/>
        小球2 质量 m2 = <span id="side_m2">{m2}</span> kg<br/>
        恢复系数 e = <span id="side_e">{e}</span><br/>
        <hr/>

        <h4>【实时运动数据】</h4>
        小球1 位置：<span id="side_x1">0.00</span><br/>
        小球2 位置：<span id="side_x2">0.00</span><br/>
        小球1 速度：<span id="side_v1">0.00</span> m/s<br/>
        小球2 速度：<span id="side_v2">0.00</span> m/s<br/>
        <hr/>

        <h4>【动量 & 动能数据】</h4>
        小球1 动量：<span id="side_p1">0.00</span><br/>
        小球2 动量：<span id="side_p2">0.00</span><br/>
        系统总动量：<span id="side_pt">0.00</span><br/>
        小球1 动能：<span id="side_ek1">0.00</span><br/>
        小球2 动能：<span id="side_ek2">0.00</span><br/>
        系统总动能：<span id="side_ekt">0.00</span>
    </div>
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

// 右侧侧边数据DOM
const side_x1 = document.getElementById("side_x1");
const side_x2 = document.getElementById("side_x2");
const side_v1 = document.getElementById("side_v1");
const side_v2 = document.getElementById("side_v2");
const side_p1 = document.getElementById("side_p1");
const side_p2 = document.getElementById("side_p2");
const side_pt = document.getElementById("side_pt");
const side_ek1 = document.getElementById("side_ek1");
const side_ek2 = document.getElementById("side_ek2");
const side_ekt = document.getElementById("side_ekt");

// 碰撞计算
function collideOneDim(){
    if(Math.abs(x1 - x2) < 2*r){
        let v1New = ((m1 - e*m2)*v1 + (1+e)*m2*v2) / (m1 + m2);
        let v2New = ((m2 - e*m1)*v2 + (1+e)*m1*v1) / (m1 + m2);
        v1 = v1New;
        v2 = v2New;
    }
}

// 边界反弹
function boundaryBounce(){
    if(x1 < r || x1 > aniCvs.width - r) v1 = -v1;
    if(x2 < r || x2 > aniCvs.width - r) v2 = -v2;
}

// 绘制碰撞小球
function drawBall(){
    aniCtx.clearRect(0,0,aniCvs.width,aniCvs.height);
    aniCtx.beginPath();
    aniCtx.arc(x1, aniCvs.height/2, r, 0, Math.PI*2);
    aniCtx.fillStyle="#f44336"; aniCtx.fill();
    aniCtx.beginPath();
    aniCtx.arc(x2, aniCvs.height/2, r, 0, Math.PI*2);
    aniCtx.fillStyle="#2196F3"; aniCtx.fill();
}

// 实时更新右侧全部数据
function updateSideData(){
    let p1 = m1 * v1;
    let p2 = m2 * v2;
    let pTotal = p1 + p2;
    let ek1 = 0.5 * m1 * v1 * v1;
    let ek2 = 0.5 * m2 * v2 * v2;
    let ekTotal = ek1 + ek2;

    side_x1.innerText = x1.toFixed(2);
    side_x2.innerText = x2.toFixed(2);
    side_v1.innerText = v1.toFixed(2);
    side_v2.innerText = v2.toFixed(2);

    side_p1.innerText = p1.toFixed(2);
    side_p2.innerText = p2.toFixed(2);
    side_pt.innerText = pTotal.toFixed(2);

    side_ek1.innerText = ek1.toFixed(2);
    side_ek2.innerText = ek2.toFixed(2);
    side_ekt.innerText = ekTotal.toFixed(2);
}

// 速度-时间图
function drawVelChart(){
    velCtx.clearRect(0,0,velCvs.width,velCvs.height);
    let ox=40, oy=velCvs.height/2;
    velCtx.strokeStyle="#ccc";
    velCtx.beginPath();velCtx.moveTo(ox,15);velCtx.lineTo(ox,velCvs.height-15);velCtx.lineTo(velCvs.width-10,velCvs.height-15);velCtx.stroke();
    
    velCtx.strokeStyle="#f44336";
    velCtx.beginPath();
    for(let i=0;i<tList.length;i++){
        let px = ox + tList[i]*8;
        let py = oy - v1List[i]*5;
        i===0 ? velCtx.moveTo(px,py) : velCtx.lineTo(px,py);
    }
    velCtx.stroke();

    velCtx.strokeStyle="#2196F3";
    velCtx.beginPath();
    for(let i=0;i<tList.length;i++){
        let px = ox + tList[i]*8;
        let py = oy - v2List[i]*5;
        i===0 ? velCtx.moveTo(px,py) : velCtx.lineTo(px,py);
    }
    velCtx.stroke();
    velCtx.fillText("速度 - 时间图像",45,18);
}

// 动能-时间图
function drawEkChart(){
    ekCtx.clearRect(0,0,ekCvs.width,ekCvs.height);
    let ox=40, oy=ekCvs.height-25;
    ekCtx.strokeStyle="#ccc";
    ekCtx.beginPath();ekCtx.moveTo(ox,15);ekCtx.lineTo(ox,oy);ekCtx.lineTo(ekCvs.width-10,oy);ekCtx.stroke();

    ekCtx.strokeStyle="#f44336";
    ekCtx.beginPath();
    for(let i=0;i<tList.length;i++){
        let px = ox + tList[i]*8;
        let py = oy - ek1List[i]*1.5;
        i===0 ? ekCtx.moveTo(px,py) : ekCtx.lineTo(px,py);
    }
    ekCtx.stroke();

    ekCtx.strokeStyle="#2196F3";
    ekCtx.beginPath();
    for(let i=0;i<tList.length;i++){
        let px = ox + tList[i]*8;
        let py = oy - ek2List[i]*1.5;
        i===0 ? ekCtx.moveTo(px,py) : ekCtx.lineTo(px,py);
    }
    ekCtx.stroke();

    ekCtx.strokeStyle="#666";
    ekCtx.setLineDash([4,4]);
    ekCtx.beginPath();
    for(let i=0;i<tList.length;i++){
        let px = ox + tList[i]*8;
        let py = oy - ekSumList[i]*1.5;
        i===0 ? ekCtx.moveTo(px,py) : ekCtx.lineTo(px,py);
    }
    ekCtx.stroke();
    ekCtx.setLineDash([]);
    ekCtx.fillText("动能 - 时间图像",45,18);
}

// 动量-时间图
function drawMomChart(){
    momCtx.clearRect(0,0,momCvs.width,momCvs.height);
    let ox=40, oy=momCvs.height/2;
    momCtx.strokeStyle="#ccc";
    momCtx.beginPath();momCtx.moveTo(ox,15);momCtx.lineTo(ox,momCvs.height-15);momCtx.lineTo(momCvs.width-10,momCvs.height-15);momCtx.stroke();
    
    momCtx.strokeStyle="#f44336";
    momCtx.beginPath();
    for(let i=0;i<tList.length;i++){
        let px = ox + tList[i]*8;
        let py = oy - p1List[i]*2.5;
        i===0 ? momCtx.moveTo(px,py) : momCtx.lineTo(px,py);
    }
    momCtx.stroke();

    momCtx.strokeStyle="#2196F3";
    momCtx.beginPath();
    for(let i=0;i<tList.length;i++){
        let px = ox + tList[i]*8;
        let py = oy - p2List[i]*2.5;
        i===0 ? momCtx.moveTo(px,py) : momCtx.lineTo(px,py);
    }
    momCtx.stroke();

    momCtx.strokeStyle="#444";
    momCtx.setLineDash([4,4]);
    momCtx.beginPath();
    for(let i=0;i<tList.length;i++){
        let px = ox + tList[i]*8;
        let py = oy - pTotalList[i]*2.5;
        i===0 ? momCtx.moveTo(px,py) : momCtx.lineTo(px,py);
    }
    momCtx.stroke();
    momCtx.setLineDash([]);
    momCtx.fillText("动量 - 时间图像",45,18);
}

// 主动画循环
function update(){
    if(playing){
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
        let eks = ek1+ek2;

        tList.push(t);
        v1List.push(v1);v2List.push(v2);
        ek1List.push(ek1);ek2List.push(ek2);ekSumList.push(eks);
        p1List.push(p1);p2List.push(p2);pTotalList.push(pt);

        if(tList.length>600){
            tList.shift();v1List.shift();v2List.shift();
            ek1List.shift();ek2List.shift();ekSumList.shift();
            p1List.shift();p2List.shift();pTotalList.shift();
        }

        updateSideData();
    }

    drawBall();
    drawVelChart();
    drawEkChart();
    drawMomChart();

    requestAnimationFrame(update);
}

// 控制函数
function play(){playing=true;}
function pause(){playing=false;}
function reset(){
    playing=false;
    x1={x1_0};x2={x2_0};
    v1={v1_0};v2={v2_0};
    t=0;
    tList=[];
    v1List=[];v2List=[];
    ek1List=[];ek2List=[];ekSumList=[];
    p1List=[];p2List=[];pTotalList=[];

    updateSideData();
    drawBall();drawVelChart();drawEkChart();drawMomChart();
}

// 初始化
updateSideData();
drawBall();drawVelChart();drawEkChart();drawMomChart();
update();
</script>
</body>
</html>
'''

# 左右放入布局
with left_col:
    st.components.v1.html(html_code, height=950)

with right_col:
    st.empty()
