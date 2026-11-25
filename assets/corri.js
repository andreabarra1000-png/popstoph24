/* Gioco «Corri, POP, corri!» – Pop Stop h24 */
(function(){
  "use strict";
  var $=function(s){return document.querySelector(s)};
  var root=$("#corri"); if(!root) return;
  document.body.classList.add("giocando");
  var can=$("#c-can"),ctx=can.getContext("2d");
  var el={start:$("#c-start"),end:$("#c-end"),cuori:$("#c-cuori"),ciocc:$("#c-ciocc"),metri:$("#c-metri"),
    banner:$("#c-banner"),fin:$("#c-fin"),rec:$("#c-record"),best:$("#c-best"),share:$("#c-share"),audio:$("#c-audio"),tit:$("#c-tit")};

  /* ---- immagini di POP (3 fotogrammi) ---- */
  var base=(document.currentScript&&document.currentScript.src)||"";
  base=base.replace(/corri\.js.*$/,"");
  var IMG=[0,1,2].map(function(i){var im=new Image();im.src=base+"pop-corsa-"+i+".svg";return im});

  /* ---- dimensioni ---- */
  var H=360,W=640,scala=1,dpr=1;
  function misura(){
    var r=can.parentNode.getBoundingClientRect();
    var cw=r.width, ch=Math.max(cw*0.62,Math.min(cw*0.88,window.innerHeight*0.62));
    can.style.width=cw+"px";can.style.height=ch+"px";
    dpr=Math.min(window.devicePixelRatio||1,((navigator.deviceMemory&&navigator.deviceMemory<=2)||(navigator.hardwareConcurrency&&navigator.hardwareConcurrency<=2))?1:2);
    can.width=Math.round(cw*dpr);can.height=Math.round(ch*dpr);
    scala=ch/H; W=Math.max(420,Math.min(1000,cw/scala));
  }
  window.addEventListener("resize",misura);

  /* ---- suoni ---- */
  var muto=false,actx=null,best=0;
  try{best=+localStorage.getItem("pop-corri-record")||0;muto=localStorage.getItem("pop-gioco-muto")==="1"}catch(e){}
  function bip(f,d,t,v){if(muto)return;try{actx=actx||new (window.AudioContext||window.webkitAudioContext)();var o=actx.createOscillator(),g=actx.createGain();o.type=t||"square";o.frequency.setValueAtTime(f,actx.currentTime);o.frequency.exponentialRampToValueAtTime(f*1.5,actx.currentTime+d);g.gain.setValueAtTime(v||.05,actx.currentTime);g.gain.exponentialRampToValueAtTime(.0001,actx.currentTime+d);o.connect(g);g.connect(actx.destination);o.start();o.stop(actx.currentTime+d)}catch(e){}}
  function audioIcon(){el.audio.textContent=muto?"🔇":"🔊"}
  audioIcon();
  el.audio.addEventListener("click",function(e){e.stopPropagation();muto=!muto;try{localStorage.setItem("pop-gioco-muto",muto?"1":"0")}catch(_){}audioIcon()});

  /* ---- mondo ---- */
  var G=300; // altezza del terreno
  var TAPPE=[
    {n:"Alabama",cielo:["#7fd3f0","#d8f3ff"],terra:"#4cb85f",sotto:"#7a5232"},
    {n:"Coast to coast",cielo:["#ff7a45","#ffd59a"],terra:"#d9925a",sotto:"#9b4a2a"},
    {n:"A pesca di gamberi",cielo:["#46596a","#8aa1b1"],terra:"#8a6a4a",sotto:"#3b2a1a"}
  ];
  var FRASI=["Corri, POP, corri! 🏃","La vita è come una scatola di snack 🍫","Coast to coast! 🌄","Non mi fermo mai: Pop Stop è aperto h24 😎","Piove, ma io corro lo stesso 🌧️","Stupido è chi si ferma! 💨"];
  var S=null,ultimo=0,raf=0;

  function nuovo(){
    S={x:0,v:230,p:{y:G-60,vy:0,terra:true,salti:0,tieni:0,inv:0,frame:0,ft:0},
      suolo:[[ -200,900]],piatt:[],ciocc:[],scatole:[],nemici:[],fx:[],
      gen:900,cuori:3,c:0,tappa:-1,t:0,fine:false,frase:"",fraseT:0,piuma:{x:500,y:60}};
    genera(2400);
  }
  function rnd(a,b){return a+Math.random()*(b-a)}

  /* generazione a blocchi */
  function genera(fino){
    while(S.gen<fino){
      var x=S.gen, m=S.x/10, diff=Math.min(1,m/1500);
      // buca
      var buca=x>1400&&Math.random()<0.35+diff*0.25;
      if(buca){var gw=rnd(70,110+diff*50);S.gen+=gw;x=S.gen;}
      var len=rnd(520,900);
      S.suolo.push([x,x+len]);
      if(buca){ // cioccolatini ad arco sopra la buca
        for(var i=0;i<4;i++)S.ciocc.push({x:x-gw+gw*(i+.5)/4,y:G-95-Math.sin(Math.PI*(i+.5)/4)*45,ok:true});
      }
      // contenuto del blocco
      var k=x+rnd(160,260);
      while(k<x+len-120){
        var r=Math.random();
        if(r<0.28){ // piattaforma con cioccolatini
          var pw=rnd(110,180),py=rnd(185,225);
          S.piatt.push({x:k,y:py,w:pw});
          for(var j=0;j<3;j++)S.ciocc.push({x:k+pw*(j+.5)/3,y:py-26,ok:true});
          if(Math.random()<.4)S.scatole.push({x:k+pw/2-17,y:py-110,piena:true,b:0});
          k+=pw+rnd(90,160);
        }else if(r<0.48){ // scatola da colpire da sotto
          S.scatole.push({x:k,y:G-140,piena:true,b:0});
          S.ciocc.push({x:k+17,y:G-175,ok:true});
          k+=rnd(150,220);
        }else if(r<0.66){ // granchio
          S.nemici.push({t:"granchio",x:k,y:G-26,w:34,h:26,vx:-40,vivo:true});
          k+=rnd(170,240);
        }else if(r<0.80){ // panchina con scatola di cioccolatini
          S.nemici.push({t:"panchina",x:k,y:G-36,w:74,h:36,vivo:true});
          S.ciocc.push({x:k+37,y:G-80,ok:true});
          k+=rnd(190,260);
        }else if(r<0.90&&m>150){ // pallone che rimbalza
          S.nemici.push({t:"palla",x:k+200,y:G-120,w:30,h:30,vx:-70,vy:0,vivo:true});
          k+=rnd(200,280);
        }else{ // fila di cioccolatini
          for(var q=0;q<5;q++)S.ciocc.push({x:k+q*30,y:G-34,ok:true});
          k+=rnd(190,250);
        }
      }
      S.gen=x+len;
    }
    // pulizia
    var lim=S.x-400;
    S.suolo=S.suolo.filter(function(s){return s[1]>lim});
    S.piatt=S.piatt.filter(function(s){return s.x+s.w>lim});
    S.ciocc=S.ciocc.filter(function(s){return s.x>lim&&s.ok});
    S.scatole=S.scatole.filter(function(s){return s.x>lim-40});
    S.nemici=S.nemici.filter(function(s){return s.x>lim-80&&s.y<H+80});
  }

  /* ---- input ---- */
  var giu=false;
  function salta(){
    if(!S||S.fine)return;
    var p=S.p;
    if(p.terra){p.vy=-640;p.terra=false;p.salti=1;p.tieni=.22;bip(520,.12);polvere()}
    else if(p.salti<2){p.vy=-540;p.salti=2;p.tieni=.12;bip(700,.12)}
  }
  var ultimoTocco=0;
  function inGioco(){return S&&!S.fine&&el.start.hidden}
  function premi(e){
    if(!inGioco())return;
    if(e.target&&e.target.closest&&e.target.closest("button,a,.cover"))return;
    var ora=Date.now(); if(ora-ultimoTocco<90)return; ultimoTocco=ora;
    if(e.cancelable)e.preventDefault();
    giu=true;salta();
  }
  function lascia(){giu=false}
  var wrap=can.parentNode;
  wrap.addEventListener("touchstart",premi,{passive:false});
  wrap.addEventListener("touchend",lascia);wrap.addEventListener("touchcancel",lascia);
  wrap.addEventListener("pointerdown",function(e){if(e.pointerType!=="touch")premi(e)});
  wrap.addEventListener("mousedown",function(e){premi(e)});
  window.addEventListener("pointerup",lascia);window.addEventListener("mouseup",lascia);
  var bs=document.getElementById("c-salta");
  if(bs){bs.addEventListener("touchstart",function(e){e.stopPropagation();if(e.cancelable)e.preventDefault();if(!inGioco())return;var o=Date.now();if(o-ultimoTocco<90)return;ultimoTocco=o;giu=true;salta()},{passive:false});
    bs.addEventListener("mousedown",function(e){e.stopPropagation();if(!inGioco())return;var o=Date.now();if(o-ultimoTocco<90)return;ultimoTocco=o;giu=true;salta()});
    bs.addEventListener("touchend",lascia)}
  window.addEventListener("keydown",function(e){if(e.code==="Space"||e.code==="ArrowUp"||e.code==="KeyW"){if(S&&!S.fine){e.preventDefault();if(!giu){giu=true;salta()}}}});
  window.addEventListener("keyup",function(e){if(e.code==="Space"||e.code==="ArrowUp"||e.code==="KeyW")giu=false});

  /* ---- effetti ---- */
  function testo(x,y,t,c){S.fx.push({k:"t",x:x,y:y,t:t,c:c||"#FFD23F",v:1})}
  function polvere(){for(var i=0;i<5;i++)S.fx.push({k:"p",x:S.x+100,y:G-4,vx:rnd(-80,-20),vy:rnd(-60,-10),v:1})}
  function dici(f){S.frase=f;S.fraseT=2.6}
  function banner(t){el.banner.textContent=t;el.banner.classList.remove("on");void el.banner.offsetWidth;el.banner.classList.add("on")}

  function colpito(){
    var p=S.p; if(p.inv>0)return;
    S.cuori--;p.inv=1.6;bip(160,.3,"sawtooth",.07);
    if(navigator.vibrate)try{navigator.vibrate(80)}catch(e){}
    aggHud();
    if(S.cuori<=0)fine();
  }
  function aggHud(){el.cuori.textContent="❤️".repeat(Math.max(0,S.cuori))+"🤍".repeat(3-Math.max(0,S.cuori));el.ciocc.textContent=S.c;el.metri.textContent=Math.floor(S.x/10)}

  /* ---- aggiornamento ---- */
  function suoloA(x){for(var i=0;i<S.suolo.length;i++){var s=S.suolo[i];if(x>=s[0]&&x<=s[1])return true}return false}
  function passo(dt){
    S.t+=dt;
    S.v=Math.min(470,230+S.x/10*0.12);
    S.x+=S.v*dt;
    var p=S.p,px=S.x+100,pw=34,ph=54;
    // tappa
    var tp=Math.floor(Math.max(0,S.x)/10/500)%3;
    if(tp!==S.tappa){S.tappa=tp;banner(TAPPE[tp].n+(S.x>100?" · giro "+(1+Math.floor(S.x/10/1500)):""));if(S.x>100)dici(FRASI[[0,2,4][tp]])}
    if(S.t>4&&Math.random()<dt*0.04&&S.fraseT<=0)dici(FRASI[Math.floor(Math.random()*FRASI.length)]);
    // fisica
    var prima=p.y+ph;
    var g=1900; if(giu&&p.vy<0&&p.tieni>0){g*=0.45;p.tieni-=dt}
    p.vy+=g*dt; if(p.vy>1100)p.vy=1100;
    p.y+=p.vy*dt;
    p.terra=false;
    var piedi=p.y+ph;
    // terreno
    if(p.vy>=0&&prima<=G+2&&piedi>=G&&(suoloA(px+6)||suoloA(px+pw-6))){p.y=G-ph;p.vy=0;p.terra=true;p.salti=0}
    // piattaforme (solo da sopra)
    S.piatt.forEach(function(q){var sx=q.x;if(p.vy>=0&&prima<=q.y+2&&piedi>=q.y&&px+pw-6>sx&&px+6<sx+q.w){p.y=q.y-ph;p.vy=0;p.terra=true;p.salti=0}});
    // scatole: colpo da sotto, appoggio da sopra
    S.scatole.forEach(function(b){
      var bx=b.x,by=b.y,bs=34;
      if(px+pw-6>bx&&px+6<bx+bs){
        if(p.vy<0&&p.y<=by+bs&&p.y-p.vy*dt>=by+bs-2){p.y=by+bs;p.vy=60;if(b.piena){b.piena=false;b.b=.25;for(var i=0;i<4;i++){S.c++;S.fx.push({k:"c",x:bx+17,y:by-10,vy:-340-i*60,v:1})}testo(bx+17,by-30,"+4 🍫");bip(880,.25,"triangle",.07);aggHud()}else bip(200,.08)}
        else if(p.vy>=0&&prima<=by+2&&piedi>=by){p.y=by-ph;p.vy=0;p.terra=true;p.salti=0}
      }
      if(b.b>0)b.b-=dt;
    });
    if(p.terra&&p.salti===0){p.ft+=dt*S.v/36;}else p.ft=0;
    // caduta nella buca
    if(p.y>H+40){
      S.cuori--;aggHud();bip(120,.4,"sawtooth",.07);
      if(S.cuori<=0){fine();return}
      // rinasce sul prossimo pezzo di terreno
      var nx=S.x+100;for(var i=0;i<S.suolo.length;i++){if(S.suolo[i][1]>nx+60){nx=Math.max(nx,S.suolo[i][0]+20);break}}
      S.x=nx-100;p.y=G-ph-120;p.vy=0;p.inv=1.6;dici("Mi rialzo e corro! 💪");
    }
    if(p.inv>0)p.inv-=dt;
    // cioccolatini
    S.ciocc.forEach(function(c){if(c.ok&&Math.abs(c.x-(px+pw/2))<26&&Math.abs(c.y-(p.y+ph/2))<34){c.ok=false;S.c++;bip(990,.08,"triangle",.05);S.fx.push({k:"s",x:c.x,y:c.y,v:1});aggHud();if(S.c===25)dici(FRASI[1])}});
    // nemici
    S.nemici.forEach(function(n){
      if(!n.vivo){n.y+=300*dt;return}
      if(n.t==="granchio"){n.x+=n.vx*dt}
      if(n.t==="palla"){n.x+=n.vx*dt;n.vy+=1400*dt;n.y+=n.vy*dt;if(n.y+n.h>=G&&suoloA(n.x+n.w/2)){n.y=G-n.h;n.vy=-520}}
      var hit=px+pw-8>n.x&&px+8<n.x+n.w&&p.y+ph-4>n.y&&p.y+6<n.y+n.h;
      if(!hit)return;
      if(n.t!=="panchina"&&p.vy>0&&prima<=n.y+10){n.vivo=false;p.vy=-480;p.salti=1;var pt=n.t==="granchio"?"+5 🍫":"+3 🍫";S.c+=n.t==="granchio"?5:3;testo(n.x,n.y-10,pt);bip(440,.15,"square",.06);aggHud()}
      else if(n.t==="panchina"&&p.vy>=0&&prima<=n.y+6){p.y=n.y-ph;p.vy=0;p.terra=true;p.salti=0}
      else colpito();
    });
    // piuma
    S.piuma.x-=(S.v*0.25+20)*dt;S.piuma.y=60+Math.sin(S.t*1.3)*28;if(S.piuma.x<-40)S.piuma.x=W+rnd(200,800);
    // effetti
    S.fx.forEach(function(f){f.v-=dt*(f.k==="t"?.8:1.6);if(f.k==="t")f.y-=40*dt;if(f.k==="c"){f.vy+=1300*dt;f.y+=f.vy*dt}if(f.k==="p"){f.x+=f.vx*dt;f.y+=f.vy*dt}});
    S.fx=S.fx.filter(function(f){return f.v>0});
    if(S.fraseT>0)S.fraseT-=dt;
    if(Math.floor(S.x/10)%5===0)el.metri.textContent=Math.floor(S.x/10);
    genera(S.x+W+800);
  }

  /* ---- disegno ---- */
  function cielo(tp){
    var t=TAPPE[tp],g=ctx.createLinearGradient(0,0,0,G);g.addColorStop(0,t.cielo[0]);g.addColorStop(1,t.cielo[1]);ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
    var o1=-(S.x*0.15)%W,o2=-(S.x*0.4)%600;
    if(tp===0){
      ctx.fillStyle="rgba(255,255,255,.8)";for(var i=0;i<3;i++){var cx=((i*260-S.x*0.08)%(W+200)+W+200)%(W+200)-100;nuvola(cx,50+i*22)}
      for(var k=-1;k<3;k++){ctx.fillStyle="#8fd49a";colle(o1+k*W,G,W*0.7,110);ctx.fillStyle="#5fc070";colle(o2+k*600+200,G,420,70)}
      emo("🌳",(((-S.x*0.5)%700)+700)%700+W*0.1,G-10,54);
    }else if(tp===1){
      ctx.fillStyle="#ffcf5a";ctx.beginPath();ctx.arc(W*0.72,95,38,0,7);ctx.fill();
      for(var k2=-1;k2<3;k2++){var bx=o1+k2*W;ctx.fillStyle="#c25a38";butte(bx+40,G,120,150);butte(bx+W*0.55,G,90,120);ctx.fillStyle="#a8452a";butte(o2+k2*600+300,G,70,80)}
    }else{
      ctx.fillStyle="#2f6f8f";ctx.fillRect(0,G-70,W,70);ctx.fillStyle="#3c86a8";for(var w=-1;w<W/40+2;w++){ctx.beginPath();ctx.arc(((w*40-S.x*0.3)%40+40)%40+w*40-40,G-70,14,Math.PI,0);ctx.fill()}
      var nx=((W+300-(S.x*0.2)%(W+300))%(W+300))-150;ctx.save();ctx.translate(nx,G-80);ctx.rotate(Math.sin(S.t*2)*0.06);emo("🚢",0,0,64);ctx.restore();
    }
  }
  function nuvola(x,y){ctx.beginPath();ctx.arc(x,y,18,0,7);ctx.arc(x+22,y-8,22,0,7);ctx.arc(x+46,y,18,0,7);ctx.fill()}
  function colle(x,y,w,h){ctx.beginPath();ctx.ellipse(x+w/2,y,w/2,h,0,Math.PI,0);ctx.fill()}
  function butte(x,y,w,h){ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+w*0.12,y-h);ctx.lineTo(x+w*0.88,y-h);ctx.lineTo(x+w,y);ctx.fill()}
  function emo(e,x,y,s){ctx.font=s+"px system-ui,'Apple Color Emoji','Segoe UI Emoji','Noto Color Emoji',sans-serif";ctx.textAlign="center";ctx.textBaseline="bottom";ctx.fillText(e,x,y)}
  function rr(x,y,w,h,r){ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);ctx.closePath()}

  function disegna(){
    ctx.setTransform(dpr*scala,0,0,dpr*scala,0,0);
    var tp=Math.max(0,S.tappa)%3,T=TAPPE[tp],cam=S.x;
    cielo(tp);
    // piuma
    ctx.save();ctx.translate(S.piuma.x,S.piuma.y);ctx.rotate(Math.sin(S.t*2.4)*0.5);emo("🪶",0,12,26);ctx.restore();
    // terreno
    S.suolo.forEach(function(s){var x0=s[0]-cam,x1=s[1]-cam;if(x1<-10||x0>W+10)return;
      ctx.fillStyle=T.sotto;ctx.fillRect(x0,G,x1-x0,H-G);ctx.fillStyle=T.terra;ctx.fillRect(x0,G,x1-x0,14);
      ctx.fillStyle="rgba(0,0,0,.18)";ctx.fillRect(x0,G+14,x1-x0,4);
      if(tp===1){ctx.fillStyle="#3a3f45";ctx.fillRect(x0,G+24,x1-x0,26);ctx.fillStyle="#FFD23F";for(var d=Math.ceil((s[0])/60)*60;d<s[1]-30;d+=60)ctx.fillRect(d-cam,G+35,30,4)}
      if(tp===2){ctx.fillStyle="rgba(0,0,0,.25)";for(var d2=Math.ceil(s[0]/28)*28;d2<s[1];d2+=28)ctx.fillRect(d2-cam,G,2,H-G)}
      ctx.strokeStyle="#061219";ctx.lineWidth=3;ctx.strokeRect(x0,G,x1-x0,H-G+4)});
    // piattaforme
    S.piatt.forEach(function(q){var x=q.x-cam;if(x>W||x+q.w<0)return;ctx.fillStyle="#8a5a2b";rr(x,q.y,q.w,16,6);ctx.fill();ctx.strokeStyle="#061219";ctx.lineWidth=3;ctx.stroke();ctx.fillStyle="#b07a40";ctx.fillRect(x+6,q.y+4,q.w-12,3)});
    // scatole
    S.scatole.forEach(function(b){var x=b.x-cam,y=b.y-(b.b>0?Math.sin(b.b*12)*6:0);if(x>W||x<-40)return;
      ctx.fillStyle=b.piena?"#05848A":"#5b6b70";rr(x,y,34,34,6);ctx.fill();ctx.strokeStyle="#061219";ctx.lineWidth=3;ctx.stroke();
      if(b.piena){ctx.fillStyle="#FFD23F";ctx.font="800 15px Bricolage,system-ui,sans-serif";ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillText("POP",x+17,y+18)}});
    // cioccolatini
    S.ciocc.forEach(function(c){if(!c.ok)return;var x=c.x-cam;if(x<-20||x>W+20)return;emo("🍫",x,c.y+12+Math.sin(S.t*5+c.x)*2,24)});
    // nemici
    S.nemici.forEach(function(n){var x=n.x-cam;if(x>W+80||x<-90)return;
      if(n.t==="granchio"){ctx.save();ctx.translate(x+n.w/2,n.y+n.h);if(!n.vivo)ctx.scale(1,-1);emo("🦀",0,4+Math.abs(Math.sin(S.t*10))*-3,34);ctx.restore()}
      else if(n.t==="palla"){ctx.save();ctx.translate(x+15,n.y+15);ctx.rotate(S.t*-6);emo("🏈",0,15,32);ctx.restore()}
      else{panchina(x,n.y)}});
    // POP
    var p=S.p,px=100,fr=p.terra?(Math.floor(p.ft)%2):2,im=IMG[fr];
    if(!(p.inv>0&&Math.floor(p.inv*12)%2)){
      ctx.save();ctx.translate(px+17,p.y+54);ctx.rotate(p.terra?0.12:(p.vy<0?-0.08:0.18));
      if(im.complete&&im.naturalWidth)ctx.drawImage(im,-34,-66,68,94);else{ctx.fillStyle="#05848A";ctx.fillRect(-17,-54,34,54)}
      ctx.restore();
    }
    // effetti
    S.fx.forEach(function(f){ctx.globalAlpha=Math.max(0,Math.min(1,f.v));var x=f.x-cam;
      if(f.k==="t"){ctx.font="800 18px Bricolage,system-ui,sans-serif";ctx.textAlign="center";ctx.lineWidth=4;ctx.strokeStyle="#061219";ctx.strokeText(f.t,x,f.y);ctx.fillStyle=f.c;ctx.fillText(f.t,x,f.y)}
      else if(f.k==="c")emo("🍫",x,f.y,22);
      else if(f.k==="s"){ctx.strokeStyle="#FFD23F";ctx.lineWidth=3;ctx.beginPath();ctx.arc(x,f.y,(1-f.v)*26+4,0,7);ctx.stroke()}
      else{ctx.fillStyle="rgba(230,240,240,.7)";ctx.beginPath();ctx.arc(x,f.y,5,0,7);ctx.fill()}
      ctx.globalAlpha=1});
    // pioggia
    if(tp===2){ctx.strokeStyle="rgba(255,255,255,.35)";ctx.lineWidth=1.5;ctx.beginPath();for(var i=0;i<70;i++){var rx=((i*97+S.t*-120)%W+W)%W,ry=((i*53+S.t*620)%H);ctx.moveTo(rx,ry);ctx.lineTo(rx-6,ry+16)}ctx.stroke()}
    // fumetto
    if(S.fraseT>0){var tx=S.frase;ctx.font="700 14px system-ui,sans-serif";var w=Math.min(W-130,ctx.measureText(tx).width+22);var bx=Math.min(px+30,W-w-10),by=Math.max(8,p.y-48);
      ctx.globalAlpha=Math.min(1,S.fraseT*2);ctx.fillStyle="#fff";rr(bx,by,w,30,12);ctx.fill();ctx.strokeStyle="#061219";ctx.lineWidth=3;ctx.stroke();ctx.fillStyle="#061219";ctx.textAlign="left";ctx.textBaseline="middle";ctx.fillText(tx,bx+11,by+15,w-22);ctx.globalAlpha=1}
  }
  function panchina(x,y){ctx.fillStyle="#8a5a2b";ctx.strokeStyle="#061219";ctx.lineWidth=2.5;
    rr(x,y+4,74,8,3);ctx.fill();ctx.stroke();rr(x,y+16,74,7,3);ctx.fill();ctx.stroke();
    ctx.fillStyle="#3b2a1a";ctx.fillRect(x+6,y+23,6,13);ctx.fillRect(x+62,y+23,6,13);
    ctx.fillStyle="#6b3a1f";ctx.fillRect(x+40,y-8,24,12);ctx.fillStyle="#e8133b";ctx.fillRect(x+40,y-8,24,4)}

  /* ---- ciclo ---- */
  function ciclo(t){
    if(!S||S.fine)return;
    var dt=Math.max(0,Math.min(0.033,(t-ultimo)/1000||0));ultimo=Math.max(ultimo,t);
    try{passo(dt);if(S.fine)return;disegna()}catch(err){if(window.console)console.error(err)}
    raf=requestAnimationFrame(ciclo);
  }
  document.addEventListener("visibilitychange",function(){if(document.hidden){cancelAnimationFrame(raf)}else if(S&&!S.fine){ultimo=performance.now();raf=requestAnimationFrame(ciclo)}});

  function via(){
    el.start.hidden=true;el.end.hidden=true;root.classList.add("in-corsa");
    misura();nuovo();aggHud();
    dici(FRASI[0]);banner(TAPPE[0].n);S.tappa=0;
    ultimo=performance.now();cancelAnimationFrame(raf);raf=requestAnimationFrame(ciclo);
    can.parentNode.scrollIntoView({block:"center",behavior:"smooth"});
  }
  function fine(){
    S.fine=true;cancelAnimationFrame(raf);disegna();root.classList.remove("in-corsa");giu=false;
    var m=Math.floor(S.x/10),pt=m+S.c*10,rec=pt>best;
    if(rec){best=pt;try{localStorage.setItem("pop-corri-record",best)}catch(e){}}
    el.tit.textContent=m>1500?"Che corsa! 🏆":m>600?"Sei arrivato lontano! 🏃":"Ti sei fermato! 😮‍💨";
    el.fin.innerHTML="<b>"+pt+"</b> punti · "+m+" m e "+S.c+" 🍫";
    el.rec.textContent=rec?"🎉 Nuovo record!":"Il tuo record: "+best+" punti";
    var msg="Ho corso "+m+" metri con POP e preso "+S.c+" cioccolatini 🏃🍫 ("+pt+" punti). Mi batti? "+location.origin+location.pathname;
    el.share.href="https://wa.me/?text="+encodeURIComponent(msg);
    el.end.hidden=false;bip(330,.5,"triangle",.06);
  }
  root.querySelectorAll("[data-via]").forEach(function(b){b.addEventListener("click",function(e){e.stopPropagation();via()})});
  if(best)el.best.textContent="Il tuo record: "+best+" punti";
  if(location.hash==="#prova")window.__corri=function(){return S};

  /* schermata iniziale animata */
  misura();nuovo();S.tappa=0;
  (function demo(t){if(S&&!S.fine&&el.start.hidden)return;S.x+=2.2;S.t=t/1000;S.p.ft+=0.12;S.p.terra=true;S.p.y=G-54;genera(S.x+W+800);
    S.suolo.forEach(function(s){});disegna();requestAnimationFrame(demo)})(0);
})();
