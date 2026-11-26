/* Giochi di POP a schermo intero – Pop Stop h24 */
(function(){
  "use strict";
  var root=document.querySelector("#corri,#gioco"); if(!root) return;
  var b=document.body, d=document.documentElement;
  var x=document.createElement("button");
  x.className="gesci"; x.type="button"; x.setAttribute("aria-label","Esci dal gioco"); x.innerHTML="✕";
  b.appendChild(x);
  function ridisegna(){try{window.dispatchEvent(new Event("resize"))}catch(e){var ev=document.createEvent("Event");ev.initEvent("resize",true,true);window.dispatchEvent(ev)}}
  function piena(){return document.fullscreenElement||document.webkitFullscreenElement}
  function entra(){
    if(b.classList.contains("gfull")) return;
    b.classList.add("gfull");
    try{history.pushState({gfull:1},"")}catch(e){}
    var rq=d.requestFullscreen||d.webkitRequestFullscreen;
    if(rq){try{var p=rq.call(d,{navigationUI:"hide"});if(p&&p.catch)p.catch(function(){})}catch(e){}}
    window.scrollTo(0,0); ridisegna(); setTimeout(ridisegna,300); setTimeout(ridisegna,800);
  }
  function esci(daIndietro){
    if(!b.classList.contains("gfull")) return;
    b.classList.remove("gfull");
    if(piena()){var ex=document.exitFullscreen||document.webkitExitFullscreen;try{var p=ex.call(document);if(p&&p.catch)p.catch(function(){})}catch(e){}}
    if(!daIndietro){try{if(history.state&&history.state.gfull)history.back()}catch(e){}}
    ridisegna(); setTimeout(ridisegna,300);
    try{root.scrollIntoView({block:"start"})}catch(e){}
  }
  document.addEventListener("click",function(e){var t=e.target;if(t&&t.closest&&t.closest("[data-via]"))entra()},true);
  x.addEventListener("click",function(e){e.stopPropagation();esci()});
  window.addEventListener("popstate",function(){esci(true)});
  function cambio(){if(!piena()&&b.classList.contains("gfull")&&!b.classList.contains("gfull-ios"))esci();ridisegna()}
  document.addEventListener("fullscreenchange",cambio);
  document.addEventListener("webkitfullscreenchange",cambio);
  /* iPhone: niente API di schermo intero, resta la versione a tutta pagina */
  if(!(d.requestFullscreen||d.webkitRequestFullscreen)) b.classList.add("gfull-ios");
  window.addEventListener("orientationchange",function(){setTimeout(ridisegna,300)});
})();
