import streamlit as st

st.set_page_config(layout="wide", page_title="一维碰撞仿真 | 恢复系数e可调")
st.title("一维对心碰撞仿真（弹性/非弹性/完全非弹性）")

# ========== 参数改为【数字输入框】，自由输入不受滑块限制 ==========
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
    # 自动计算初始动量
    p1_0 = m1 * v1_0
    p2_0 = m2 * v2_0
    st.info(f"""
    初始动量：\n
    小球1 动量 p1 = {p1_0:.2f} kg·m/s\n
    小球2 动量 p2 = {p2_0:.2f} kg·m/s
    """)

# ========== 前端JS动画 + 三曲线图：位置、速度、动量 ==========
html_code = f'''
<!DOCTYPE html>
<html>
<head>
<style>
body {{margin:0;padding:10px;font-family:sans-serif;background:#f9f9f9;}}
.box-wrap{{display:flex;gap:12px;justify-content:center;align-items:flex-start;flex-wrap:wrap;}}
canvas{{background:#fff;border:1px solid #ddd;border-radius:8px;}}
.controls{{text-align:center;margin:15px 0;}}
button{{padding:8px 22px;margin:0 10px;font-size:16px;border:none;border-radius:6px;background:#2196F3;color:#fff;cursor:pointer;}}
</style>
</head>
<body>

<div class="controls">
    <button onclick="play()">播放</button>
    <button onclick="pause()">暂停</button>
    <button onclick="reset()">重置</button>
    <span style="margin-left:20px;color:#666;">恢复系数 e = {e}</span>
</div>

<div class="box-wrap">
    <!-- 碰撞动画画布 -->
    <canvas id="aniCanvas" width="600" height="220"></canvas>
    <!-- 位置-时间 -->
    <canvas id="posCanvas" width="320" height="220"></canvas>
    <!-- 速度-时间 -->
    <canvas id="velCanvas" width="320" height="220"></canvas>
    <!-- 动量-时间 -->
    <canvas id="momCanvas" width="320" height="220"></canvas>
</div>

<script>
// 外部传入参数
const m1 = {m1};
const m2 = {m2};
const e  = {e};
let x1  = {x1_0};
let x2  = {x2_0};
let v1  = {v1_0};
let v2  = {v2_0};

const r = 26;
let playing = true;
// 提速：时间步长加大，运动更快
const dt = 0.05;

// 数据记录
let t = 0;
let tList = [];
let x1List=[],x2List=[];
let v1List=[],v2List=[];
let p1List=[],p2List=[];

// 获取画布
const aniCvs = document.getElementById("aniCanvas");
const aniCtx = aniCvs.getContext("2d");

const posCvs = document.getElementById("posCanvas");
const posCtx = posCvs.getContext("2d");

const velCvs = document.getElementById("velCanvas");
const velCtx = velCvs.getContext("2d");

const momCvs = document.getElementById("momCanvas");
const momCtx = momCvs.getContext("2d");

// 【一维碰撞公式 支持恢复系数e】
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
    aniCtx.arc(x1, aniCvs.height/2, r, 0, Math.PI*2);
    aniCtx.fillStyle="#f44336"; aniCtx.fill();

    aniCtx.beginPath();
    aniCtx.arc(x2, aniCvs.height/2, r, 0, Math.PI*2);
    aniCtx.fillStyle="#2196F3"; aniCtx.fill();
}}

// 位置-时间曲线
function drawPosChart(){{
    posCtx.clearRect(0,0,posCvs.width,posCvs.height);
    let ox=40, oy=posCvs.height/2;
    posCtx.strokeStyle="#ccc";
    posCtx.beginPath();posCtx.moveTo(ox,20);posCtx.lineTo(ox,posCvs.height-20);posCtx.lineTo(posCvs.width-10,posCvs.height-20);posCtx.stroke();

    posCtx.strokeStyle="#f44336";
    posCtx.beginPath();
    for(let i=0;i<tList.length;i++){{
        let px = ox + tList[i]*8;
        let py = posCvs.height - 30 - x1List[i]*0.25;
        i===0 ? posCtx.moveTo(px,py) : posCtx.lineTo(px,py);
    }}
    posCtx.stroke();

    posCtx.strokeStyle="#2196F3";
    posCtx.beginPath();
    for(let i=0;i<tList.length;i++){{
        let px = ox + tList[i]*8;
        let py = posCvs.height - 30 - x2List[i]*0.25;
        i===0 ? posCtx.moveTo(px,py) : posCtx.lineTo(px,py);
    }}
    posCtx.stroke();
    posCtx.fillText("位置-时间",45,18);
}}

// 速度-时间曲线
function drawVelChart(){{
    velCtx.clearRect(0,0,velCvs.width,velCvs.height);
    let ox=40, oy=velCvs.height/2;
    velCtx.strokeStyle="#ccc";
    velCtx.beginPath();velCtx.moveTo(ox,20);velCtx.lineTo(ox,velCvs.height-20);velCtx.lineTo(velCvs.width-10,velCvs.height-20);velCtx.stroke();

    velCtx.strokeStyle="#f44336";
    velCtx.beginPath();
    for(let i=0;i<tList.length;i++){{
        let px = ox + tList[i]*8;
        let py = oy - v1List[i]*6;
        i===0 ? velCtx.moveTo(px,py) : velCtx.lineTo(px,py);
    }}
    velCtx.stroke();

    velCtx.strokeStyle="#2196F3";
    velCtx.beginPath();
    for(let i=0;i<tList.length;i++){{
        let px = ox + tList[i]*8;
        let py = oy - v2List[i]*6;
        i===0 ? velCtx.moveTo(px,py) : velCtx.lineTo(px,py);
    }}
    velCtx.stroke();
    velCtx.fillText("速度-时间",45,18);
}}

// 动量-时间曲线
function drawMomChart(){{
    momCtx.clearRect(0,0,momCvs.width,momCvs.height);
    let ox=40, oy=momCvs.height/2;
    momCtx.strokeStyle="#ccc";
    momCtx.beginPath();momCtx.moveTo(ox,20);momCtx.lineTo(ox,momCvs.height-20);momCtx.lineTo(momCvs.width-10,momCvs.height-20);momCtx.stroke();

    momCtx.strokeStyle="#f44336";
    momCtx.beginPath();
    for(let i=0;i<tList.length;i++){{
        let px = ox + tList[i]*8;
        let py = oy - p1List[i]*3;
        i===0 ? momCtx.moveTo(px,py) : momCtx.lineTo(px,py);
    }}
    momCtx.stroke();

    momCtx.strokeStyle="#2196F3";
    momCtx.beginPath();
    for(let i=0;i<tList.length;i++){{
        let px = ox + tList[i]*8;
        let py = oy - p2List[i]*3;
        i===0 ? momCtx.moveTo(px,py) : momCtx.lineTo(px,py);
    }}
    momCtx.stroke();
    momCtx.fillText("动量-时间",45,18);
}}

// 主循环
function update(){{
    if(playing){{
        // 更新位置 + 提速
        x1 += v1 * dt * 2;
        x2 += v2 * dt * 2;

        // 碰撞+边界
        collideOneDim();
        boundaryBounce();

        // 记录数据
        t += dt;
        tList.push(t);
        x1List.push(x1);x2List.push(x2);
        v1List.push(v1);v2List.push(v2);
        p1List.push(m1*v1);p2List.push(m2*v2);

        // 限制数据长度防卡顿
        if(tList.length>600){{
            tList.shift();x1List.shift();x2List.shift();
            v1List.shift();v2List.shift();
            p1List.shift();p2List.shift();
        }}
    }}
    drawBall();
    drawPosChart();
    drawVelChart();
    drawMomChart();
    requestAnimationFrame(update);
}}

// 控制
function play(){{playing=true;}}
function pause(){{playing=false;}}
function reset(){{
    playing=false;
    x1={x1_0};x2={x2_0};
    v1={v1_0};v2={v2_0};
    t=0;
    tList=[];x1List=[];x2List=[];
    v1List=[];v2List=[];p1List=[];p2List=[];
    drawBall();drawPosChart();drawVelChart();drawMomChart();
}}

// 初始化启动
drawBall();
drawPosChart();
drawVelChart();
drawMomChart();
update();
</script>
</body>
</html>
'''

st.components.v1.html(html_code, height=520)
