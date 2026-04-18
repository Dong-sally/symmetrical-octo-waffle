import streamlit as st

st.set_page_config(page_title="完全弹性碰撞仿真", layout="wide")
st.title("完全弹性碰撞仿真 | 动画 + 实时速度时间曲线（带坐标刻度）")

m1 = st.slider("物体1 质量(kg)", 0.1, 5.0, 1.0, 0.1)
m2 = st.slider("物体2 质量(kg)", 0.1, 5.0, 2.0, 0.1)
v1_init = st.slider("物体1 初速度(m/s)", -3.0, 3.0, 2.0, 0.1)
v2_init = st.slider("物体2 初速度(m/s)", -3.0, 3.0, -1.0, 0.1)

html = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
body{{background:#f6f6f6;text-align:center;margin:0;padding:10px;}}
.box{{display:flex;gap:20px;justify-content:center;align-items:center;}}
#ani{{width:62%;height:360px;background:#fff;border-radius:6px;border:1px solid #ccc;}}
#line{{width:35%;height:360px;background:#fff;border-radius:6px;border:1px solid #ccc;}}
.btns{{margin-top:16px;}}
button{{padding:8px 24px;margin:0 8px;font-size:16px;border:none;border-radius:5px;background:#2185d0;color:#fff;cursor:pointer;}}
</style>
</head>
<body>

<div class="box">
<canvas id="ani"></canvas>
<canvas id="line"></canvas>
</div>

<div class="btns">
<button onclick="play()">播放</button>
<button onclick="pause()">暂停</button>
<button onclick="reset()">重置</button>
</div>

<script>
// 物理参数
const m1 = {m1}, m2 = {m2};
let v1 = {v1_init}, v2 = {v2_init};
const r = 28;

// 画布
const cvsA = document.getElementById("ani");
const ctxA = cvsA.getContext("2d");
const cvsL = document.getElementById("line");
const ctxL = cvsL.getContext("2d");

cvsA.width = cvsA.offsetWidth;
cvsA.height = cvsA.offsetHeight;
cvsL.width = cvsL.offsetWidth;
cvsL.height = cvsL.offsetHeight;

// 状态
let x1 = 80;
let x2 = cvsA.width / 2;
let playing = true;

// 曲线数据
let t = 0;
let arrT = [];
let arrV1 = [];
let arrV2 = [];

// 完全弹性碰撞
function collide(){
    if(Math.abs(x1 - x2) < 2*r){
        let nv1 = ((m1-m2)*v1 + 2*m2*v2)/(m1+m2);
        let nv2 = ((m2-m1)*v2 + 2*m1*v1)/(m1+m2);
        v1 = nv1; v2 = nv2;
    }
}

// 绘制小球动画
function drawBall(){
    ctxA.clearRect(0,0,cvsA.width,cvsA.height);
    ctxA.beginPath();
    ctxA.arc(x1, cvsA.height/2, r, 0, Math.PI*2);
    ctxA.fillStyle="#f43f3b"; ctxA.fill();

    ctxA.beginPath();
    ctxA.arc(x2, cvsA.height/2, r, 0, Math.PI*2);
    ctxA.fillStyle="#366ed8"; ctxA.fill();
}

// 绘制【带坐标刻度+数字】的速度-时间图
function drawLineChart(){
    ctxL.clearRect(0,0,cvsL.width,cvsL.height);
    let W = cvsL.width;
    let H = cvsL.height;
    let ox = 45;
    let oy = H/2;

    // 坐标轴
    ctxL.strokeStyle="#666";
    ctxL.lineWidth=1;
    ctxL.beginPath();
    ctxL.moveTo(ox,20);
    ctxL.lineTo(ox,H-30);
    ctxL.lineTo(W-20,H-30);
    ctxL.stroke();

    // Y轴速度刻度数字
    ctxL.font="12px sans-serif";
    ctxL.fillStyle="#444";
    for(let i=-2;i<=2;i++){
        let y = oy - i*40;
        ctxL.fillText(i.toString(),15,y+4);
    }
    // X轴时间刻度
    for(let i=0;i<=5;i++){
        let x = ox + i*60;
        ctxL.fillText(i.toString(),x-8,H-15);
    }

    // 实时速度曲线
    ctxL.strokeStyle="#f43f3b";
    ctxL.beginPath();
    for(let i=0;i<arrT.length;i++){
        let px = ox + arrT[i]*8;
        let py = oy - arrV1[i]*40;
        if(i===0) ctxL.moveTo(px,py);
        else ctxL.lineTo(px,py);
    }
    ctxL.stroke();

    ctxL.strokeStyle="#366ed8";
    ctxL.beginPath();
    for(let i=0;i<arrT.length;i++){
        let px = ox + arrT[i]*8;
        let py = oy - arrV2[i]*40;
        if(i===0) ctxL.moveTo(px,py);
        else ctxL.lineTo(px,py);
    }
    ctxL.stroke();
}

function update(){
    if(playing){
        x1 += v1;
        x2 += v2;
        collide();

        // 边界回弹
        if(x1<r||x1>cvsA.width-r) v1=-v1;
        if(x2<r||x2>cvsA.width-r) v2=-v2;

        // 实时记录数据
        t += 0.025;
        arrT.push(t);
        arrV1.push(v1);
        arrV2.push(v2);

        // 限制长度防止溢出
        if(arrT.length>450){
            arrT.shift();arrV1.shift();arrV2.shift();
        }
    }

    drawBall();
    drawLineChart();
    requestAnimationFrame(update);
}

// 控制
function play(){playing=true;}
function pause(){playing=false;}
function reset(){
    playing=false;
    x1=80;x2=cvsA.width/2;
    v1={v1_init};v2={v2_init};
    t=0;arrT=[];arrV1=[];arrV2=[];
    drawBall();drawLineChart();
}

drawBall();
drawLineChart();
update();
</script>
</body>
</html>
'''

st.components.v1.html(html, height=430)
