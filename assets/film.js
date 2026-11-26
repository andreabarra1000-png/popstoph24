/* Giochi «POP al cinema» – Pop Stop h24
   5 mini giochi ispirati ai generi del cinema, con POP protagonista.
   La pagina indica il gioco con <div class="corri film" id="corri" data-film="squalo|dino|spazio|laser|fantasmi"> */
(function(){
  "use strict";
  var $=function(s){return document.querySelector(s)};
  var root=$("#corri"); if(!root||!root.dataset.film) return;
  var QUALE=root.dataset.film;
  document.body.classList.add("giocando");
  var can=$("#c-can"),ctx=can.getContext("2d");
  var el={start:$("#c-start"),end:$("#c-end"),cuori:$("#c-cuori"),punti:$("#c-punti"),extra:$("#c-extra"),
    banner:$("#c-banner"),fin:$("#c-fin"),rec:$("#c-record"),best:$("#c-best"),share:$("#c-share"),audio:$("#c-audio"),tit:$("#c-tit")};

  /* ---- POP ---- */
  var base=(document.currentScript&&document.currentScript.src)||"";
  base=base.replace(/film\.js.*$/,"");
  var POP=new Image();POP.src=base+"pop.svg";
  function pop(x,y,h,rot,alpha){ // x,y = centro dei piedi
    var w=h*200/260;ctx.save();ctx.translate(x,y);if(rot)ctx.rotate(rot);if(alpha!=null)ctx.globalAlpha=alpha;
    if(POP.complete&&POP.naturalWidth)ctx.drawImage(POP,-w/2,-h,w,h);
    else{ctx.fillStyle="#05848A";ctx.strokeStyle="#061219";ctx.lineWidth=3;rr(-w/2,-h,w,h*.9,8);ctx.fill();ctx.stroke()}
    ctx.restore();
  }

  /* ---- dimensioni ---- */
  var H=360,W=640,scala=1,dpr=1;
  function misura(){
    var r=can.parentNode.getBoundingClientRect();
    var cw=r.width, ch;
    if(document.body.classList.contains("gfull")){ch=Math.min(window.innerHeight,cw*H/360)}else ch=Math.max(cw*0.62,Math.min(cw*0.95,window.innerHeight*0.66));
    can.style.width=cw+"px";can.style.height=ch+"px";
    dpr=Math.min(window.devicePixelRatio||1,((navigator.deviceMemory&&navigator.deviceMemory<=2)||(navigator.hardwareConcurrency&&navigator.hardwareConcurrency<=2))?1:2);
    can.width=Math.round(cw*dpr);can.height=Math.round(ch*dpr);
    scala=ch/H; W=Math.max(360,Math.min(1000,cw/scala));
  }
  window.addEventListener("resize",function(){misura();if(S&&S.fine!==false)disegna()});

  /* ---- suoni ---- */
  var muto=false,actx=null,best=0,KEY="pop-film-"+QUALE;
  try{best=+localStorage.getItem(KEY)||0;muto=localStorage.getItem("pop-gioco-muto")==="1"}catch(e){}
  function bip(f,d,t,v,f2){if(muto||(S&&S.demo))return;try{actx=actx||new (window.AudioContext||window.webkitAudioContext)();var o=actx.createOscillator(),g=actx.createGain();o.type=t||"square";o.frequency.setValueAtTime(f,actx.currentTime);o.frequency.exponentialRampToValueAtTime(f2||f*1.5,actx.currentTime+d);g.gain.setValueAtTime(v||.05,actx.currentTime);g.gain.exponentialRampToValueAtTime(.0001,actx.currentTime+d);o.connect(g);g.connect(actx.destination);o.start();o.stop(actx.currentTime+d)}catch(e){}}
  function audioIcon(){el.audio.textContent=muto?"🔇":"🔊"}
  audioIcon();
  el.audio.addEventListener("click",function(e){e.stopPropagation();muto=!muto;try{localStorage.setItem("pop-gioco-muto",muto?"1":"0")}catch(_){}audioIcon()});

  /* ---- utilità ---- */
  function rnd(a,b){return a+Math.random()*(b-a)}
  function clamp(v,a,b){return v<a?a:v>b?b:v}
  function rr(x,y,w,h,r){ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);ctx.closePath()}
  function emoji(e,x,y,s){ctx.font=s+"px system-ui,'Apple Color Emoji','Segoe UI Emoji',sans-serif";ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillText(e,x,y)}
  function lattina(x,y,c){ctx.fillStyle=c||"#FFD23F";ctx.strokeStyle="#061219";ctx.lineWidth=2.5;rr(x-9,y-14,18,28,5);ctx.fill();ctx.stroke();ctx.fillStyle="#fff";ctx.fillRect(x-9,y-4,18,5)}
  function testo(x,y,t,c){S.fx.push({x:x,y:y,t:t,c:c||"#FFD23F",v:1})}
  function fxDraw(dt){S.fx=S.fx.filter(function(f){f.v-=dt*1.2;f.y-=dt*40;if(f.v<=0)return false;ctx.globalAlpha=Math.max(0,f.v);ctx.font="800 18px system-ui,sans-serif";ctx.textAlign="center";ctx.fillStyle="#061219";ctx.fillText(f.t,f.x+1.5,f.y+1.5);ctx.fillStyle=f.c;ctx.fillText(f.t,f.x,f.y);ctx.globalAlpha=1;return true})}
  function cielo(a,b){var g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,a);g.addColorStop(1,b);ctx.fillStyle=g;ctx.fillRect(0,0,W,H)}
  function fumetto(tx,x,y){if(!tx)return;ctx.font="700 14px system-ui,sans-serif";var w=Math.min(W-20,ctx.measureText(tx).width+22);var bx=clamp(x-w/2,8,W-w-8),by=Math.max(46,y);
    ctx.fillStyle="#fff";rr(bx,by,w,30,12);ctx.fill();ctx.strokeStyle="#061219";ctx.lineWidth=3;ctx.stroke();ctx.fillStyle="#061219";ctx.textAlign="left";ctx.textBaseline="middle";ctx.fillText(tx,bx+11,by+15,w-22)}
  function dici(f,t){S.frase=f;S.fraseT=t||2.4}
  function banner(t){el.banner.textContent=t;el.banner.classList.remove("on");void el.banner.offsetWidth;el.banner.classList.add("on")}
  function colpito(){if(S.demo||S.inv>0)return false;S.cuori--;S.inv=1.3;S.shake=.35;bip(140,.35,"sawtooth",.07,70);if(navigator.vibrate)try{navigator.vibrate(80)}catch(e){}aggHud();if(S.cuori<=0){fine();}return true}
  function punto(n,x,y,c){S.punti+=n;if(x!=null)testo(x,y,"+"+n,c);aggHud()}

  /* ---- input ---- */
  var IN={giu:false,x:null,y:null,sx:0,dir:0,tap:0};
  function pos(e){var r=can.getBoundingClientRect();var t=e.touches&&e.touches[0]?e.touches[0]:e;IN.x=(t.clientX-r.left)/r.width*W;IN.y=(t.clientY-r.top)/r.height*H}
  function inGioco(){return S&&!S.fine&&el.start.hidden}
  function giu(e){if(!inGioco())return;if(e.target&&e.target.closest&&e.target.closest("button,a,.cover"))return;if(e.cancelable)e.preventDefault();pos(e);IN.giu=true;IN.tap++;if(G.tap)G.tap(IN.x,IN.y)}
  function muovi(e){if(!inGioco())return;if(IN.giu||e.type==="mousemove"){pos(e)}if(e.cancelable&&IN.giu&&e.type==="touchmove")e.preventDefault()}
  function su(){IN.giu=false;if(G&&G.su&&inGioco())G.su()}
  var wrap=can.parentNode;
  wrap.addEventListener("touchstart",giu,{passive:false});wrap.addEventListener("touchmove",muovi,{passive:false});
  wrap.addEventListener("touchend",su);wrap.addEventListener("touchcancel",su);
  wrap.addEventListener("mousedown",giu);wrap.addEventListener("mousemove",muovi);window.addEventListener("mouseup",su);
  var TAS={};
  window.addEventListener("keydown",function(e){if(!inGioco())return;var k=e.code;if(["Space","ArrowUp","ArrowDown","ArrowLeft","ArrowRight","KeyA","KeyD","KeyW","KeyS"].indexOf(k)<0)return;e.preventDefault();if(TAS[k])return;TAS[k]=true;
    if(k==="Space"||k==="ArrowUp"||k==="KeyW"||k==="ArrowDown"||k==="KeyS"){IN.giu=true;IN.tap++;if(G.tap)G.tap(null,null,k)}});
  window.addEventListener("keyup",function(e){TAS[e.code]=false;if(e.code==="Space"||e.code==="ArrowUp"||e.code==="KeyW"||e.code==="ArrowDown"||e.code==="KeyS")su()});
  function asseX(){return (TAS.ArrowRight||TAS.KeyD?1:0)-(TAS.ArrowLeft||TAS.KeyA?1:0)}

  /* ======================================================
     I 5 GIOCHI
     ====================================================== */
  var GIOCHI={};

  /* 1 – SQUALO: POP sul canotto, evita le pinne e prendi le lattine */
  GIOCHI.squalo={
    nome:"Arriva la pinna!",unita:"lattine",
    frasi:["Ci serve una barca più grande! 🛶","Tranquilli, è solo un'onda… vero? 😬","Da Pop Stop non ci sono pinne, solo snack 🦈"],
    nuovo:function(){S.px=W/2;S.v=110;S.cose=[];S.gen=0;S.onda=0;S.prese=0},
    step:function(dt){
      var tx=IN.giu&&IN.x!=null?IN.x:null, ax=asseX();
      if(ax)S.px+=ax*320*dt; else if(tx!=null)S.px+=(tx-S.px)*Math.min(1,dt*9);
      S.px=clamp(S.px,40,W-40);
      S.v=110+S.t*3.2; S.onda+=dt;
      S.gen-=dt; if(S.gen<=0){S.gen=Math.max(.38,1.1-S.t*.012);
        var r=Math.random();
        if(r<.62)S.cose.push({k:"pinna",x:rnd(30,W-30),y:-30,vx:rnd(-40,40)*(S.t>25?1.5:1),w:rnd(.9,1.3)});
        else if(r<.92)S.cose.push({k:"lat",x:rnd(30,W-30),y:-30,c:["#FFD23F","#ff4f8b","#19d6c8","#e8133b"][Math.floor(rnd(0,4))]});
        else S.cose.push({k:"boa",x:rnd(30,W-30),y:-30});}
      var py=H-56;
      S.cose.forEach(function(c){c.y+=S.v*dt*(c.k==="pinna"?1.15:1);if(c.vx){c.x+=c.vx*dt;if(c.x<20||c.x>W-20)c.vx*=-1}
        var dx=Math.abs(c.x-S.px),dy=Math.abs(c.y-py);
        if(!c.via&&dx<34&&dy<26){
          if(c.k==="pinna"){if(colpito()){c.via=true;dici("Ahi! Mi ha morso il canotto 😱",1.6)}}
          else if(c.k==="lat"){c.via=true;S.prese++;punto(10,c.x,c.y-20);bip(880,.08,"square",.05)}
          else {c.via=true;if(S.cuori<3){S.cuori++;aggHud();testo(c.x,c.y-20,"❤️+1","#ff4f8b")}else punto(25,c.x,c.y-20);bip(600,.2,"triangle",.06)}}});
      S.cose=S.cose.filter(function(c){return !c.via&&c.y<H+40});
      if(Math.floor(S.t)%1===0)S.punti=Math.floor(S.t)*2+S.prese*10;aggHud();
    },
    draw:function(){
      cielo("#1d6b8f","#0b3d5e");
      ctx.strokeStyle="rgba(255,255,255,.18)";ctx.lineWidth=2;
      for(var i=0;i<9;i++){var y=((i*48+S.onda*S.v)%(H+48))-24;ctx.beginPath();for(var x=0;x<=W;x+=20){ctx.lineTo(x,y+Math.sin(x/40+S.onda*2+i)*4)}ctx.stroke()}
      S.cose.forEach(function(c){
        if(c.k==="pinna"){ctx.save();ctx.translate(c.x,c.y);ctx.scale(c.w,c.w);ctx.fillStyle="#5d6f7a";ctx.strokeStyle="#061219";ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(-16,10);ctx.quadraticCurveTo(-4,-28,14,-30);ctx.quadraticCurveTo(6,-8,18,10);ctx.closePath();ctx.fill();ctx.stroke();
          ctx.strokeStyle="rgba(255,255,255,.6)";ctx.beginPath();ctx.ellipse(0,12,26,5,0,0,Math.PI*2);ctx.stroke();ctx.restore()}
        else if(c.k==="lat")lattina(c.x,c.y+Math.sin(S.onda*3+c.x)*3,c.c);
        else {ctx.fillStyle="#ff5a4e";ctx.strokeStyle="#061219";ctx.lineWidth=3;ctx.beginPath();ctx.arc(c.x,c.y,15,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.fillStyle="#fff";ctx.fillRect(c.x-15,c.y-4,30,8);ctx.strokeRect(c.x-15,c.y-4,30,8)}
      });
      var py=H-56,bob=Math.sin(S.onda*4)*3;
      ctx.fillStyle="#FFD23F";ctx.strokeStyle="#061219";ctx.lineWidth=3;ctx.beginPath();ctx.ellipse(S.px,py+14+bob,40,15,0,0,Math.PI*2);ctx.fill();ctx.stroke();
      if(!(S.inv>0&&Math.floor(S.t*14)%2))pop(S.px,py+12+bob,58,Math.sin(S.onda*3)*.06);
      ctx.fillStyle="#ff4f8b";ctx.beginPath();ctx.ellipse(S.px,py+20+bob,42,9,0,0,Math.PI);ctx.fill();ctx.stroke();
      fumetto(S.fraseT>0?S.frase:"",S.px,py-110);
    },
    fineTit:function(){return S.t>60?"Sei il re del mare! 🛶":S.t>25?"Bella traversata! 🌊":"Ci voleva una barca più grande! 🦈"},
    riga:function(){return Math.floor(S.t)+" secondi in mare e "+S.prese+" lattine"},
    share:function(pt){return "Ho resistito "+Math.floor(S.t)+" secondi tra le pinne con POP 🦈🛶 ("+pt+" punti). Mi batti?"}
  };

  /* 2 – DINO: avanza solo quando il dinosauro non guarda */
  GIOCHI.dino={
    nome:"Il parco dei dinosauri",unita:"recinti",
    frasi:["Se non ti muovi, non ti vede… 🦖","Shhh! Il bicchiere trema 🥤","La macchina degli snack è oltre il recinto!"],
    nuovo:function(){S.liv=1;S.d=0;S.stato="dorme";S.timer=rnd(1.6,2.6);S.ok=0;S.trema=0;S.premio=[];
      S.lung=420;for(var i=0;i<4;i++)S.premio.push({d:rnd(60,S.lung-60),ok:true})},
    step:function(dt){
      var muove=IN.giu||asseX()>0;
      S.timer-=dt;
      if(S.stato==="dorme"&&S.timer<0.7&&S.timer>0)S.trema=1;
      if(S.grazia>0)S.grazia-=dt;
      if(S.timer<=0){
        if(S.stato==="dorme"){S.stato="guarda";S.grazia=.3;S.timer=rnd(1.2,2.2)+S.liv*.1;bip(110,.5,"sawtooth",.08,60);S.trema=0}
        else {S.stato="dorme";S.timer=rnd(1.4,3.2)/(1+S.liv*.08);}}
      if(muove){S.d+=(70+S.liv*6)*dt;S.passo=(S.passo||0)+dt*10;
        if(S.stato==="guarda"&&S.grazia<=0&&S.inv<=0){if(colpito()){dici("Mi ha visto! 😱",1.5);S.d=Math.max(0,S.d-90)}}}
      S.premio.forEach(function(p){if(p.ok&&Math.abs(p.d-S.d)<14){p.ok=false;punto(5,null);testo(px(S.d),H-120,"🍫 +5");bip(900,.07)}});
      if(S.d>=S.lung){S.liv++;punto(50+S.liv*10,null);banner("Recinto "+S.liv);dici("Uff! Passato 😅",1.6);bip(520,.3,"triangle",.07,1040);
        S.d=0;S.lung=Math.min(900,420+S.liv*40);S.premio=[];for(var i=0;i<4;i++)S.premio.push({d:rnd(60,S.lung-60),ok:true});S.stato="dorme";S.timer=rnd(1.2,2.4)}
      aggHud();
    },
    draw:function(){
      cielo(S.stato==="guarda"?"#e86a3c":"#7fd3f0",S.stato==="guarda"?"#ffb36b":"#d8f3ff");
      var g=H-70;
      ctx.fillStyle="#2f7a3e";for(var i=0;i<8;i++){ctx.beginPath();ctx.arc(i*W/7,g-20,60,Math.PI,0);ctx.fill()}
      ctx.fillStyle="#4cb85f";ctx.fillRect(0,g,W,H-g);ctx.fillStyle="#7a5232";ctx.fillRect(0,g+26,W,H-g);
      // recinto
      ctx.strokeStyle="#c9c9c9";ctx.lineWidth=3;for(var k=0;k<4;k++){ctx.beginPath();ctx.moveTo(0,g-90+k*18);ctx.lineTo(W,g-90+k*18);ctx.stroke()}
      ctx.fillStyle="#8a8a8a";for(var p=0;p<W;p+=90)ctx.fillRect(p,g-100,8,100);
      // dinosauro dietro il recinto
      var dx=W*.62,dy=g-70+(S.trema?Math.sin(S.t*60)*3:0);
      ctx.fillStyle="#3f8f4f";ctx.strokeStyle="#061219";ctx.lineWidth=4;
      ctx.beginPath();ctx.ellipse(dx,dy,95,50,0,0,Math.PI*2);ctx.fill();ctx.stroke();
      var hx=S.stato==="guarda"?dx-110:dx+90, hy=dy-60;
      ctx.beginPath();ctx.ellipse(hx,hy,55,30,S.stato==="guarda"?.1:-.2,0,Math.PI*2);ctx.fill();ctx.stroke();
      ctx.fillStyle="#fff";ctx.beginPath();ctx.arc(hx+(S.stato==="guarda"?-22:20),hy-8,S.stato==="guarda"?10:3,0,Math.PI*2);ctx.fill();ctx.stroke();
      if(S.stato==="guarda"){ctx.fillStyle="#061219";ctx.beginPath();ctx.arc(hx-25,hy-6,5,0,Math.PI*2);ctx.fill();
        ctx.fillStyle="#fff";for(var t=0;t<5;t++){ctx.beginPath();ctx.moveTo(hx-48+t*10,hy+14);ctx.lineTo(hx-43+t*10,hy+24);ctx.lineTo(hx-38+t*10,hy+14);ctx.fill()}}
      else {ctx.fillStyle="#061219";emoji("💤",hx+50,hy-40,22)}
      // bicchiere che trema
      ctx.save();ctx.translate(W-46+(S.trema?Math.sin(S.t*70)*2:0),g+8);ctx.fillStyle="rgba(255,255,255,.7)";ctx.strokeStyle="#061219";ctx.lineWidth=2;rr(-12,-32,24,34,4);ctx.fill();ctx.stroke();
      ctx.fillStyle="#19d6c8";ctx.fillRect(-10,-18,20,18);if(S.trema){ctx.strokeStyle="#fff";ctx.beginPath();ctx.arc(0,-18,5,0,Math.PI*2);ctx.stroke()}ctx.restore();
      // percorso
      var x0=40,x1=W-90;ctx.strokeStyle="rgba(6,18,25,.35)";ctx.setLineDash([8,8]);ctx.beginPath();ctx.moveTo(x0,g+12);ctx.lineTo(x1,g+12);ctx.stroke();ctx.setLineDash([]);
      S.premio.forEach(function(q){if(q.ok)emoji("🍫",px(q.d),g-6,20)});
      // distributore traguardo
      ctx.fillStyle="#05848A";ctx.strokeStyle="#061219";ctx.lineWidth=3;rr(x1+6,g-70,40,76,6);ctx.fill();ctx.stroke();ctx.fillStyle="#e9fbfb";ctx.fillRect(x1+12,g-60,28,40);ctx.fillStyle="#FFD23F";ctx.font="800 9px system-ui";ctx.textAlign="center";ctx.fillText("h24",x1+26,g-6);
      var X=px(S.d),bob=IN.giu?Math.abs(Math.sin(S.passo||0))*-5:0;
      if(!(S.inv>0&&Math.floor(S.t*14)%2))pop(X,g+20+bob,64);
      // occhio-semaforo
      ctx.fillStyle=S.stato==="guarda"?"#ff3b3b":"#3ee07a";ctx.strokeStyle="#061219";ctx.lineWidth=3;ctx.beginPath();ctx.arc(W-30,64,13,0,Math.PI*2);ctx.fill();ctx.stroke();
      ctx.fillStyle="#061219";ctx.font="800 11px system-ui";ctx.textAlign="right";ctx.fillText(S.stato==="guarda"?"FERMO!":"VAI",W-50,68);
      fumetto(S.fraseT>0?S.frase:"",X,g-150);
    },
    fineTit:function(){return S.liv>6?"Domatore di dinosauri! 🦖":S.liv>3?"Scappato per un pelo! 😅":"Ti ha visto! 🦖"},
    riga:function(){return (S.liv-1)+" recinti superati"},
    share:function(pt){return "Ho superato "+(S.liv-1)+" recinti senza farmi vedere dal dinosauro con POP 🦖 ("+pt+" punti). Ci riesci?"}
  };
  function px(d){return 40+(W-130)*clamp(d/S.lung,0,1)}

  /* 3 – SPAZIO: tieni premuto per salire, evita gli asteroidi */
  GIOCHI.spazio={
    nome:"POP nello spazio",unita:"stelle",
    frasi:["Houston, abbiamo uno snack! 🚀","Verso l'infinito… e lo snack! ✨","Anche nello spazio Pop Stop è aperto h24 🌌"],
    nuovo:function(){S.y=H/2;S.vy=0;S.cose=[];S.gen=.6;S.stelle=[];S.prese=0;S.dist=0;
      for(var i=0;i<60;i++)S.stelle.push({x:rnd(0,W),y:rnd(0,H),z:rnd(.2,1)})},
    step:function(dt){
      var spinta=IN.giu||TAS.Space||TAS.ArrowUp||TAS.KeyW;
      S.vy+=(spinta?-620:430)*dt;S.vy=clamp(S.vy,-300,340);S.y+=S.vy*dt;
      if(S.y<92){S.y=92;S.vy=0}if(S.y>H-24){S.y=H-24;S.vy=-200;colpito()}
      var v=170+S.t*4;S.dist+=v*dt;
      S.stelle.forEach(function(s){s.x-=v*s.z*dt*.4;if(s.x<0){s.x=W;s.y=rnd(0,H)}});
      S.gen-=dt;if(S.gen<=0){S.gen=Math.max(.45,1.05-S.t*.01);
        var r=Math.random();
        if(r<.66)S.cose.push({k:"ast",x:W+40,y:rnd(40,H-40),r:rnd(16,30+Math.min(20,S.t*.4)),rot:0,vr:rnd(-2,2),vy:rnd(-30,30)});
        else S.cose.push({k:"stella",x:W+30,y:rnd(40,H-40)})}
      var X=110;
      S.cose.forEach(function(c){c.x-=v*dt;if(c.vy){c.y+=c.vy*dt;if(c.y<20||c.y>H-20)c.vy*=-1}if(c.vr)c.rot+=c.vr*dt;
        var dx=c.x-X,dy=c.y-(S.y-24),d=Math.sqrt(dx*dx+dy*dy);
        if(!c.via&&c.k==="ast"&&d<c.r+20){if(colpito()){c.via=true;dici("Boom! Che botta 💥",1.4)}}
        if(!c.via&&c.k==="stella"&&d<30){c.via=true;S.prese++;punto(10,c.x,c.y-14);bip(1040,.08,"triangle",.05)}});
      S.cose=S.cose.filter(function(c){return !c.via&&c.x>-60});
      S.punti=Math.floor(S.dist/50)+S.prese*10;aggHud();
    },
    draw:function(){
      cielo("#070b1f","#1b1446");
      S.stelle.forEach(function(s){ctx.fillStyle="rgba(255,255,255,"+(.3+s.z*.6)+")";ctx.fillRect(s.x,s.y,2*s.z+.5,2*s.z+.5)});
      ctx.fillStyle="#7b2ff7";ctx.globalAlpha=.5;ctx.beginPath();ctx.arc(W-90,70,40,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;
      ctx.strokeStyle="#FFD23F";ctx.lineWidth=3;ctx.beginPath();ctx.ellipse(W-90,70,62,12,-.3,0,Math.PI*2);ctx.stroke();
      S.cose.forEach(function(c){
        if(c.k==="ast"){ctx.save();ctx.translate(c.x,c.y);ctx.rotate(c.rot);ctx.fillStyle="#8a7a6a";ctx.strokeStyle="#061219";ctx.lineWidth=3;ctx.beginPath();
          for(var i=0;i<9;i++){var a=i/9*Math.PI*2,rr2=c.r*(i%2?.82:1);ctx.lineTo(Math.cos(a)*rr2,Math.sin(a)*rr2)}ctx.closePath();ctx.fill();ctx.stroke();
          ctx.fillStyle="#6b5c4e";ctx.beginPath();ctx.arc(-c.r*.3,-c.r*.2,c.r*.22,0,Math.PI*2);ctx.fill();ctx.restore()}
        else emoji("⭐",c.x,c.y,26)});
      var X=110,spinta=IN.giu||TAS.Space||TAS.ArrowUp||TAS.KeyW;
      if(spinta){ctx.fillStyle="#ff9a3c";ctx.beginPath();ctx.moveTo(X-18,S.y-4);ctx.lineTo(X-6,S.y+26+rnd(0,10));ctx.lineTo(X+6,S.y-4);ctx.fill();ctx.fillStyle="#FFD23F";ctx.beginPath();ctx.moveTo(X-10,S.y-4);ctx.lineTo(X-6,S.y+14);ctx.lineTo(X-2,S.y-4);ctx.fill()}
      ctx.strokeStyle="rgba(255,255,255,.75)";ctx.lineWidth=3;ctx.fillStyle="rgba(180,230,255,.18)";ctx.beginPath();ctx.arc(X,S.y-30,34,0,Math.PI*2);ctx.fill();ctx.stroke();
      if(!(S.inv>0&&Math.floor(S.t*14)%2))pop(X,S.y,56,clamp(S.vy/900,-.3,.3));
      fumetto(S.fraseT>0?S.frase:"",X+60,S.y-110);
    },
    fineTit:function(){return S.dist>25000?"Astronauta leggendario! 🚀":S.dist>9000?"Bel viaggio spaziale! 🌌":"Atterraggio di fortuna! 💥"},
    riga:function(){return Math.floor(S.dist/50)+" km nello spazio e "+S.prese+" stelle"},
    share:function(pt){return "Ho fatto "+Math.floor(S.dist/50)+" km nello spazio con POP 🚀⭐ ("+pt+" punti). Arrivi più lontano?"}
  };

  /* 4 – LASER: missione snack, scendi con la corda tra i laser */
  GIOCHI.laser={
    nome:"Missione: snack impossibile",unita:"colpi",
    frasi:["Missione: prendere lo snack 🕶️","Niente panico, sono un professionista 😎","Il caveau più goloso della città…"],
    nuovo:function(){S.liv=0;S.colpi=0;nuovoColpo()},
    step:function(dt){
      var scendi=IN.giu||TAS.Space||TAS.ArrowDown||TAS.KeyS;
      if(S.preso){S.y-=260*dt;if(S.y<=40){S.colpi++;punto(100+S.liv*25,null);banner("Colpo "+S.colpi+" riuscito!");dici("Missione compiuta 🕶️",1.6);bip(520,.3,"triangle",.07,1040);nuovoColpo()}aggHud();return}
      S.y+=(scendi?150+S.liv*8:-60)*dt;S.y=clamp(S.y,40,S.fondo);
      S.laser.forEach(function(l){l.t+=dt;var ciclo=l.on+l.off;var f=(l.t+l.fase)%ciclo;l.acceso=f<l.on;l.x=W/2+Math.sin(l.t*l.vel+l.fase)*l.amp;
        if(l.acceso&&S.inv<=0&&Math.abs(S.y-36-l.y)<26&&Math.abs(l.x-W/2)<l.lung/2+20){if(colpito()){S.allarme=1.2;dici("Allarme! 🚨 Si ricomincia",1.6);S.y=40}}});
      if(S.y>=S.fondo){S.preso=true;bip(900,.12);testo(W/2,S.fondo-90,"🍫 Preso!")}
      if(S.allarme>0)S.allarme-=dt;
      aggHud();
    },
    draw:function(){
      cielo("#101820","#22303c");
      ctx.strokeStyle="rgba(255,255,255,.05)";ctx.lineWidth=1;for(var x=0;x<W;x+=32){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke()}
      if(S.allarme>0&&Math.floor(S.t*8)%2){ctx.fillStyle="rgba(255,40,40,.25)";ctx.fillRect(0,0,W,H)}
      // lucernario
      ctx.fillStyle="#3a4c5a";ctx.fillRect(W/2-46,0,92,24);ctx.strokeStyle="#061219";ctx.lineWidth=3;ctx.strokeRect(W/2-46,0,92,24);
      // piedistallo con lo snack
      ctx.fillStyle="#d7dde2";rr(W/2-38,S.fondo+6,76,H-S.fondo,6);ctx.fill();ctx.stroke();
      if(!S.preso){ctx.fillStyle="rgba(180,230,255,.25)";rr(W/2-28,S.fondo-40,56,46,8);ctx.fill();ctx.stroke();emoji(S.snack,W/2,S.fondo-16,30)}
      S.laser.forEach(function(l){var x0=l.x-l.lung/2,x1=l.x+l.lung/2;
        ctx.fillStyle="#555";ctx.fillRect(x0-8,l.y-6,8,12);ctx.fillRect(x1,l.y-6,8,12);
        if(l.acceso){ctx.strokeStyle="rgba(255,40,60,.35)";ctx.lineWidth=9;ctx.beginPath();ctx.moveTo(x0,l.y);ctx.lineTo(x1,l.y);ctx.stroke();ctx.strokeStyle="#ff2b45";ctx.lineWidth=2.5;ctx.stroke()}
        else{ctx.strokeStyle="rgba(255,40,60,.15)";ctx.setLineDash([4,6]);ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(x0,l.y);ctx.lineTo(x1,l.y);ctx.stroke();ctx.setLineDash([])}});
      // corda e POP a testa in giù… quasi
      ctx.strokeStyle="#c9a36b";ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(W/2,24);ctx.lineTo(W/2,S.y-72);ctx.stroke();
      if(!(S.inv>0&&Math.floor(S.t*14)%2)){pop(W/2,S.y,64);if(S.preso)emoji(S.snack,W/2+28,S.y-30,24)}
      ctx.fillStyle="#061219";ctx.beginPath();ctx.ellipse(W/2,S.y-56,22,6,0,0,Math.PI*2);ctx.fill();
      fumetto(S.fraseT>0?S.frase:"",W/2+110,S.y-110);
    },
    fineTit:function(){return S.colpi>5?"Il colpo del secolo! 🕶️":S.colpi>2?"Agente goloso! 😎":"Scattato l'allarme! 🚨"},
    riga:function(){return S.colpi+" snack rubati dal caveau"},
    share:function(pt){return "Ho fatto "+S.colpi+" colpi nel caveau degli snack con POP 🕶️🍫 ("+pt+" punti). Sei più bravo?"}
  };
  function nuovoColpo(){S.liv++;S.y=40;S.preso=false;S.fondo=H-70;S.laser=[];S.snack=["🍫","🥤","🍟","🍬","🥪"][S.liv%5];
    var n=Math.min(6,1+S.liv);for(var i=0;i<n;i++){var y=90+i*((S.fondo-140)/Math.max(1,n-1||1));
      S.laser.push({y:Math.min(S.fondo-60,y),lung:rnd(120,Math.min(W*.9,180+S.liv*30)),amp:S.liv>2?rnd(0,Math.min(160,S.liv*20)):0,vel:rnd(.6,1.4),on:rnd(.8,1.6),off:rnd(.7,1.3),fase:rnd(0,3),t:0,acceso:false,x:W/2})}}

  /* 5 – FANTASMI: tocca i fantasmi alle finestre, non toccare i gatti */
  GIOCHI.fantasmi={
    nome:"Acchiappa i fantasmi",unita:"fantasmi",
    frasi:["Chi chiamerai? Me! 👻","La casa è infestata… di fame 😋","Toccali tutti, ma lascia stare il gatto 🐈‍⬛"],
    nuovo:function(){S.fin=[];S.gen=.8;S.prese=0;S.durata=60;S.combo=0;
      var cols=4,rows=3,w=Math.min(110,(W-80)/cols-14),h=60;
      for(var r=0;r<rows;r++)for(var c=0;c<cols;c++)S.fin.push({x:W/2+(c-(cols-1)/2)*(w+18),y:100+r*(h+16),w:w,h:h,chi:null,t:0})},
    step:function(dt){
      S.durata-=dt;if(S.durata<=0){S.durata=0;fine();return}
      S.gen-=dt;if(S.gen<=0){S.gen=Math.max(.32,.9-S.t*.01);var libere=S.fin.filter(function(f){return !f.chi});if(libere.length){var f=libere[Math.floor(Math.random()*libere.length)];
        var r=Math.random();f.chi=r<.18?"gatto":r<.26?"oro":"fant";f.t=0;f.vita=Math.max(.7,1.6-S.t*.012)}}
      S.fin.forEach(function(f){if(f.chi){f.t+=dt;if(f.t>f.vita){if(f.chi==="fant")S.combo=0;f.chi=null}}});
      aggHud();
    },
    tap:function(x,y){if(x==null)return;var hit=null;S.fin.forEach(function(f){if(x>f.x-f.w/2&&x<f.x+f.w/2&&y>f.y-f.h/2&&y<f.y+f.h/2)hit=f});
      if(!hit||!hit.chi)return;
      if(hit.chi==="gatto"){colpito();dici("Era il gatto! 🐈‍⬛ Scusa micio",1.4);S.combo=0}
      else{S.combo++;var n=(hit.chi==="oro"?30:10)+Math.min(20,(S.combo-1)*2);S.prese++;punto(n,hit.x,hit.y-30,hit.chi==="oro"?"#FFD23F":"#fff");bip(hit.chi==="oro"?1200:760,.1,"square",.05);
        if(S.combo>0&&S.combo%8===0)dici("Combo x"+S.combo+"! 🔥",1.2)}
      hit.chi=null;S.popX=hit.x;S.popT=.25},
    draw:function(){
      cielo("#1a0f2e","#3b1f4f");
      ctx.fillStyle="#f4f1c9";ctx.beginPath();ctx.arc(W-60,46,26,0,Math.PI*2);ctx.fill();ctx.fillStyle="#1a0f2e";ctx.beginPath();ctx.arc(W-50,40,24,0,Math.PI*2);ctx.fill();
      // casa
      var top=70,lw=S.fin.length?Math.abs(S.fin[3].x-S.fin[0].x)+S.fin[0].w+50:W-40;
      ctx.fillStyle="#2b2238";ctx.strokeStyle="#061219";ctx.lineWidth=4;ctx.fillRect(W/2-lw/2,top,lw,H-top);ctx.strokeRect(W/2-lw/2,top,lw,H-top);
      ctx.fillStyle="#3d2f4f";ctx.beginPath();ctx.moveTo(W/2-lw/2-20,top);ctx.lineTo(W/2,top-56);ctx.lineTo(W/2+lw/2+20,top);ctx.closePath();ctx.fill();ctx.stroke();
      S.fin.forEach(function(f){
        ctx.fillStyle=f.chi?"#ffe79a":"#0d0a18";rr(f.x-f.w/2,f.y-f.h/2,f.w,f.h,6);ctx.fill();ctx.strokeStyle="#061219";ctx.lineWidth=3;ctx.stroke();
        if(f.chi){var k=Math.min(1,f.t*6),off=(1-k)*20;ctx.save();ctx.beginPath();rr(f.x-f.w/2,f.y-f.h/2,f.w,f.h,6);ctx.clip();
          emoji(f.chi==="gatto"?"🐈‍⬛":"👻",f.x,f.y+off,f.chi==="oro"?40:44);if(f.chi==="oro"){ctx.globalAlpha=.5;emoji("✨",f.x+24,f.y-18,20);ctx.globalAlpha=1}ctx.restore()}
        ctx.strokeStyle="#061219";ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(f.x,f.y-f.h/2);ctx.lineTo(f.x,f.y+f.h/2);ctx.moveTo(f.x-f.w/2,f.y);ctx.lineTo(f.x+f.w/2,f.y);ctx.stroke()});
      // POP con l'aspirapolvere acchiappa-fantasmi
      var X=S.popT>0?S.popX:W/2;if(S.popT>0)S.popT-=1/60;
      if(!(S.inv>0&&Math.floor(S.t*14)%2))pop(clamp(X,50,W-50),H-6,64);
      ctx.fillStyle="#9aa6ad";ctx.strokeStyle="#061219";ctx.lineWidth=3;rr(clamp(X,50,W-50)+22,H-60,14,40,5);ctx.fill();ctx.stroke();
      // timer
      ctx.fillStyle="rgba(6,18,25,.8)";rr(W/2-44,48,88,26,13);ctx.fill();ctx.fillStyle=S.durata<10?"#ff5a4e":"#FFD23F";ctx.font="800 15px system-ui";ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillText("⏱ "+Math.ceil(S.durata)+" s",W/2,61);
      fumetto(S.fraseT>0?S.frase:"",W/2,H-120);
    },
    fineTit:function(){return S.cuori<=0?"Troppi gatti! 🐈‍⬛":S.prese>45?"Acchiappafantasmi d'oro! 👻":S.prese>25?"Casa liberata! 🏚️":"I fantasmi ridono ancora 👻"},
    riga:function(){return S.prese+" fantasmi acchiappati"},
    share:function(pt){return "Ho acchiappato "+S.prese+" fantasmi con POP 👻 ("+pt+" punti). Ne prendi di più?"}
  };

  var G=GIOCHI[QUALE]; if(!G) return;

  /* ---- stato e ciclo ---- */
  var S=null,ultimo=0,raf=0;
  function nuovo(){S={t:0,cuori:3,punti:0,inv:0,shake:0,fx:[],frase:"",fraseT:0,fine:false};G.nuovo()}
  function aggHud(){el.cuori.textContent=S.cuori>0?"❤️".repeat(S.cuori):"💔";el.punti.textContent=S.punti;
    if(el.extra){var v=G.unita==="lattine"?S.prese:G.unita==="recinti"?S.liv-1:G.unita==="stelle"?S.prese:G.unita==="colpi"?S.colpi:S.prese;el.extra.textContent=v||0}}
  function disegna(){
    ctx.setTransform(dpr*scala,0,0,dpr*scala,0,0);
    ctx.save();if(S.shake>0)ctx.translate(rnd(-5,5),rnd(-5,5));
    G.draw();fxDraw(0);ctx.restore();
  }
  function ciclo(t){
    if(!S||S.fine)return;
    var dt=Math.max(0,Math.min(0.033,(t-ultimo)/1000||0));ultimo=Math.max(ultimo,t);
    try{S.t+=dt;if(S.inv>0)S.inv-=dt;if(S.shake>0)S.shake-=dt;if(S.fraseT>0)S.fraseT-=dt;
      G.step(dt);if(S.fine)return;
      ctx.setTransform(dpr*scala,0,0,dpr*scala,0,0);ctx.save();if(S.shake>0)ctx.translate(rnd(-5,5),rnd(-5,5));G.draw();fxDraw(dt);ctx.restore();
    }catch(err){if(window.console)console.error(err)}
    raf=requestAnimationFrame(ciclo);
  }
  document.addEventListener("visibilitychange",function(){if(document.hidden){cancelAnimationFrame(raf)}else if(S&&!S.fine&&el.start.hidden){ultimo=performance.now();raf=requestAnimationFrame(ciclo)}});

  function via(){
    el.start.hidden=true;el.end.hidden=true;root.classList.add("in-corsa");
    misura();nuovo();aggHud();IN.giu=false;
    banner(G.nome);dici(G.frasi[Math.floor(Math.random()*G.frasi.length)],2.6);
    ultimo=performance.now();cancelAnimationFrame(raf);raf=requestAnimationFrame(ciclo);
    can.parentNode.scrollIntoView({block:"center",behavior:"smooth"});
  }
  function fine(){
    if(S.fine)return;S.fine=true;cancelAnimationFrame(raf);root.classList.remove("in-corsa");IN.giu=false;
    disegna();
    var pt=S.punti,rec=pt>best;
    if(rec){best=pt;try{localStorage.setItem(KEY,best)}catch(e){}}
    el.tit.textContent=G.fineTit();
    el.fin.innerHTML="<b>"+pt+"</b> punti · "+G.riga();
    el.rec.textContent=rec?"🎉 Nuovo record!":"Il tuo record: "+best+" punti";
    el.share.href="https://wa.me/?text="+encodeURIComponent(G.share(pt)+" "+location.origin+location.pathname);
    el.end.hidden=false;bip(330,.5,"triangle",.06,200);
  }
  root.querySelectorAll("[data-via]").forEach(function(b){b.addEventListener("click",function(e){e.stopPropagation();via()})});
  if(best)el.best.textContent="Il tuo record: "+best+" punti";
  if(location.hash==="#prova")window.__film=function(){return S};

  /* anteprima dietro la copertina */
  misura();nuovo();S.demo=true;
  (function demo(){if(!el.start.hidden||!S)return;S.t+=1/60;if(S.fraseT>0)S.fraseT=0;
    try{if(QUALE!=="fantasmi")G.step(1/60);else{S.gen-=1/60;GIOCHI.fantasmi.step.call(null,0);}}catch(e){}
    S.cuori=3;S.inv=0;S.fine=false;if(QUALE==="laser"&&S.y>=S.fondo-4)nuovoColpo();
    disegna();requestAnimationFrame(demo)})();
})();
