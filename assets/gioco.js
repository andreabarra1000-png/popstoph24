/* Gioco «Riempi le macchine» – Pop Stop h24 */
(function(){
  "use strict";
  var $=function(s,r){return (r||document).querySelector(s)};
  var root=$("#gioco"); if(!root) return;
  document.body.classList.add("giocando");

  var TIPI=[
    {k:"bibita",e:"🥤",n:"Bibita"},{k:"energy",e:"⚡",n:"Energy"},{k:"acqua",e:"💧",n:"Acqua"},
    {k:"ciocco",e:"🍫",n:"Cioccolato"},{k:"chips",e:"🍟",n:"Patatine"},{k:"tram",e:"🥪",n:"Tramezzino"},
    {k:"cara",e:"🍬",n:"Caramelle"},{k:"caffe",e:"☕",n:"Caffè"}
  ];
  var MACCHINE=[
    {n:"1ª da sinistra",t:["ciocco","ciocco","caffe","chips","ciocco","cara","caffe","chips","ciocco"]},
    {n:"2ª da sinistra",t:["bibita","bibita","energy","tram","tram","energy","bibita","chips","energy"]},
    {n:"2ª da destra",t:["acqua","acqua","cara","energy","acqua","cara","bibita","energy","cara"]},
    {n:"1ª da destra",t:["energy","energy","bibita","ciocco","ciocco","bibita","energy","cara","acqua"]}
  ];
  var tipo={};TIPI.forEach(function(t){tipo[t.k]=t});

  var el={
    start:$("#g-start"),play:$("#g-play"),end:$("#g-end"),
    ora:$("#g-ora"),punti:$("#g-punti"),liv:$("#g-liv"),bar:$("#g-bar i"),
    grid:$("#g-grid"),tray:$("#g-tray"),pop:$("#g-pop"),fum:$("#g-fumetto"),
    fin:$("#g-fin"),record:$("#g-record"),share:$("#g-share"),audio:$("#g-audio"),
    tit:$("#g-tit")
  };

  var S=null,timer=null,best=0,muto=false,actx=null;
  try{best=+localStorage.getItem("pop-gioco-record")||0;muto=localStorage.getItem("pop-gioco-muto")==="1"}catch(e){}
  function salvaRecord(){try{localStorage.setItem("pop-gioco-record",best)}catch(e){}}

  function suono(f,d,tp){
    if(muto) return;
    try{
      actx=actx||new (window.AudioContext||window.webkitAudioContext)();
      var o=actx.createOscillator(),g=actx.createGain();
      o.type=tp||"square";o.frequency.value=f;g.gain.value=.06;
      o.connect(g);g.connect(actx.destination);o.start();
      g.gain.exponentialRampToValueAtTime(.0001,actx.currentTime+(d||.12));
      o.stop(actx.currentTime+(d||.12));
    }catch(e){}
  }
  function vibra(ms){try{navigator.vibrate&&navigator.vibrate(ms)}catch(e){}}
  function aggiornaAudio(){el.audio.textContent=muto?"🔇":"🔊";el.audio.setAttribute("aria-label",muto?"Attiva i suoni":"Togli i suoni")}

  var frasiOk=["Grande!","Vai così!","Perfetto!","Che velocità!","Bravo!","Ottimo!"];
  var frasiNo=["Lì no!","Quello non ci va!","Ops, scomparto sbagliato!"];
  function dici(t,cls){
    el.fum.textContent=t;el.fum.className="fum on "+(cls||"");
    el.pop.classList.remove("salta","trema");void el.pop.offsetWidth;
    el.pop.classList.add(cls==="no"?"trema":"salta");
    clearTimeout(dici.t);dici.t=setTimeout(function(){el.fum.className="fum"},1300);
  }

  function livello(n){
    return {vuoti:Math.min(8+n*3,30),secondi:Math.max(30,48-n*2),fame:Math.max(1.6,4.2-n*.45)};
  }

  function nuovaPartita(){
    S={liv:0,punti:0,combo:0,sel:-1,caricati:0};
    el.start.hidden=true;el.end.hidden=true;el.play.hidden=false;document.body.classList.add("inplay");window.scrollTo(0,0);
    nuovoLivello();
  }

  function nuovoLivello(){
    S.liv++;
    var L=livello(S.liv);
    S.durata=L.secondi;S.resta=L.secondi;S.fame=L.fame;S.prossimaFame=L.fame;
    S.slot=[];
    MACCHINE.forEach(function(m,mi){m.t.forEach(function(k,si){S.slot.push({m:mi,s:si,k:k,pieno:true})})});
    var idx=S.slot.map(function(_,i){return i});
    for(var i=idx.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var t=idx[i];idx[i]=idx[j];idx[j]=t}
    idx.slice(0,L.vuoti).forEach(function(i){S.slot[i].pieno=false});
    S.tray=[];for(var k=0;k<5;k++) S.tray.push(pesca());
    S.sel=-1;
    disegna();
    el.liv.textContent=S.liv;
    dici(S.liv===1?"Riempi tutto prima delle 6!":"Livello "+S.liv+"! Più veloce!");
    clearInterval(timer);S.t0=performance.now();S.last=S.t0;
    timer=setInterval(tick,100);
  }

  function vuoti(){return S.slot.filter(function(s){return !s.pieno})}
  function pesca(){
    var v=vuoti();
    var giaInMano={};(S.tray||[]).forEach(function(k){giaInMano[k]=(giaInMano[k]||0)+1});
    var serve=v.map(function(s){return s.k}).filter(function(k){return !giaInMano[k]});
    if(serve.length&&Math.random()<.75) return serve[Math.floor(Math.random()*serve.length)];
    if(v.length&&Math.random()<.6) return v[Math.floor(Math.random()*v.length)].k;
    return TIPI[Math.floor(Math.random()*TIPI.length)].k;
  }

  function tick(){
    var now=performance.now(),dt=(now-S.last)/1000;S.last=now;
    S.resta-=dt;
    S.prossimaFame-=dt;
    if(S.prossimaFame<=0){
      S.prossimaFame=S.fame*(0.7+Math.random()*.6);
      var pieni=S.slot.filter(function(s){return s.pieno});
      if(pieni.length>4){
        var s=pieni[Math.floor(Math.random()*pieni.length)];
        s.pieno=false;s.preso=true;
        dici("Qualcuno ha preso "+tipo[s.k].n.toLowerCase()+"!","fame");
        suono(220,.15,"triangle");
        disegna();
      }
    }
    var frac=Math.max(0,S.resta/S.durata);
    var min=Math.round((1-frac)*60);
    el.ora.textContent="05:"+("0"+Math.min(59,min)).slice(-2);
    el.bar.style.transform="scaleX("+frac+")";
    el.bar.parentNode.classList.toggle("urgente",frac<.25);
    if(S.resta<=0) fine(false);
  }

  function disegna(){
    var h="";
    MACCHINE.forEach(function(m,mi){
      h+='<div class="gm" data-m="'+mi+'"><div class="gm-top">'+m.n+'</div><div class="gm-slots">';
      S.slot.filter(function(s){return s.m===mi}).forEach(function(s){
        var i=S.slot.indexOf(s);
        var cls="gs"+(s.pieno?" pieno":" vuoto")+(s.nuovo?" nuovo":"")+(s.preso?" preso":"")+(!s.pieno&&S.sel>-1&&S.tray[S.sel]===s.k?" giusto":"");
        h+='<button type="button" class="'+cls+'" data-i="'+i+'" aria-label="'+(s.pieno?tipo[s.k].n+", pieno":"Scomparto vuoto per "+tipo[s.k].n)+'"><span>'+tipo[s.k].e+'</span></button>';
        s.nuovo=false;s.preso=false;
      });
      h+='</div><div class="gm-feet"></div></div>';
    });
    el.grid.innerHTML=h;
    var t="";
    S.tray.forEach(function(k,i){
      t+='<button type="button" class="gt'+(i===S.sel?" sel":"")+'" data-t="'+i+'" aria-pressed="'+(i===S.sel)+'" aria-label="'+tipo[k].n+'"><span>'+tipo[k].e+'</span><small>'+tipo[k].n+'</small></button>';
    });
    el.tray.innerHTML=t;
    el.punti.textContent=S.punti;
  }

  function scegli(i){
    S.sel=(S.sel===i)?-1:i;suono(660,.05);disegna();
  }

  function metti(i){
    var s=S.slot[i];
    if(s.pieno){return}
    if(S.sel<0){
      var j=S.tray.indexOf(s.k);
      if(j<0){dici("Prima prendi un "+tipo[s.k].n.toLowerCase()+" dal carrello!","no");suono(140,.18,"sawtooth");vibra(60);return}
      S.sel=j;
    }
    if(S.tray[S.sel]!==s.k){
      S.combo=0;S.resta=Math.max(0,S.resta-1.5);
      dici(frasiNo[Math.floor(Math.random()*frasiNo.length)],"no");
      suono(140,.18,"sawtooth");vibra(80);
      var b=el.grid.querySelector('[data-i="'+i+'"]');if(b){b.classList.add("errore");setTimeout(function(){b.classList.remove("errore")},350)}
      return;
    }
    s.pieno=true;s.nuovo=true;S.caricati++;
    S.combo++;
    var p=10+Math.min(S.combo,10)*2;S.punti+=p;
    S.tray[S.sel]=pesca();S.sel=-1;
    suono(520+Math.min(S.combo,10)*60,.08);
    if(S.combo>1&&S.combo%5===0) dici("Combo x"+S.combo+"!","ok");
    else if(Math.random()<.25) dici(frasiOk[Math.floor(Math.random()*frasiOk.length)],"ok");
    disegna();
    if(!vuoti().length) livelloFatto();
  }

  function livelloFatto(){
    clearInterval(timer);
    var bonus=Math.round(S.resta)*5;S.punti+=bonus;
    el.punti.textContent=S.punti;
    dici("Macchine piene! +"+bonus+" bonus","ok");
    suono(784,.12);setTimeout(function(){suono(988,.12)},120);setTimeout(function(){suono(1318,.2)},240);
    setTimeout(nuovoLivello,1500);
  }

  function fine(){
    clearInterval(timer);
    var record=S.punti>best;if(record){best=S.punti;salvaRecord()}
    el.play.hidden=true;el.end.hidden=false;document.body.classList.remove("inplay");window.scrollTo(0,0);
    el.tit.textContent=S.liv>1?"Sono le 6: arriva la fila del mattino!":"Sono le 6 e le macchine non sono piene!";
    el.fin.innerHTML="<b>"+S.punti+"</b> punti · livello "+S.liv+" · "+S.caricati+" prodotti caricati";
    el.record.textContent=record?"🏆 Nuovo record!":"Record: "+best;
    var msg="Ho fatto "+S.punti+" punti a «Riempi le macchine» di POP 🟦 Mi batti? "+location.href.split("#")[0];
    el.share.href="https://wa.me/?text="+encodeURIComponent(msg);
    suono(330,.2,"triangle");setTimeout(function(){suono(262,.3,"triangle")},200);
  }

  root.addEventListener("click",function(e){
    var t=e.target.closest("[data-t]");if(t&&S&&!el.play.hidden){scegli(+t.dataset.t);return}
    var s=e.target.closest("[data-i]");if(s&&S&&!el.play.hidden){metti(+s.dataset.i);return}
    if(e.target.closest("[data-via]")){nuovaPartita();return}
    if(e.target.closest("#g-audio")){muto=!muto;try{localStorage.setItem("pop-gioco-muto",muto?"1":"0")}catch(x){}aggiornaAudio();return}
  });
  document.addEventListener("visibilitychange",function(){
    if(!S||el.play.hidden) return;
    if(document.hidden){clearInterval(timer)}else{S.last=performance.now();clearInterval(timer);timer=setInterval(tick,100)}
  });
  aggiornaAudio();
  if(best) $("#g-best").textContent="Il tuo record: "+best+" punti";
})();
