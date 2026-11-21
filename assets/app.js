(function(){
  "use strict";
  var $=function(s,r){return (r||document).querySelector(s)}, $$=function(s,r){return [].slice.call((r||document).querySelectorAll(s))};
  var CFG=window.POP||{};

  /* ora di Casavatore */
  function oraRoma(){
    var p=new Intl.DateTimeFormat("it-IT",{timeZone:"Europe/Rome",hour:"2-digit",minute:"2-digit",second:"2-digit",hour12:false}).formatToParts(new Date());
    var o={};p.forEach(function(x){o[x.type]=x.value});
    return {h:+o.hour%24,m:+o.minute,s:+o.second,txt:o.hour+":"+o.minute};
  }
  var FRASI=[
    [0,5,"Notte fonda? Noi siamo svegli."],
    [5,11,"Buongiorno! Colazione al volo o acqua fresca?"],
    [11,15,"Pausa pranzo: tramezzini e bibite fresche."],
    [15,19,"Ora di merenda: dolce o salato?"],
    [19,22,"Serata o partita? Snack e bibite pronti."],
    [22,24,"Fame di notte? Siamo aperti, come sempre."]
  ];
  function tick(){
    var t=oraRoma();
    $$("[data-ora]").forEach(function(e){e.textContent=t.txt});
    var f=FRASI.filter(function(x){return t.h>=x[0]&&t.h<x[1]})[0];
    $$("[data-frase]").forEach(function(e){if(f)e.textContent=f[2]});
    document.body.classList.toggle("day",t.h>=7&&t.h<18);
    var hh=$(".hh"),mh=$(".mh"),sh=$(".sh");
    if(hh){
      hh.style.transform="rotate("+((t.h%12)*30+t.m*.5)+"deg)";
      mh.style.transform="rotate("+(t.m*6+t.s*.1)+"deg)";
      sh.style.transform="rotate("+(t.s*6)+"deg)";
    }
  }
  tick();setInterval(tick,1000);

  /* menu */
  var bg=$(".burger"),nav=$(".nav");
  if(bg)bg.addEventListener("click",function(){var o=nav.classList.toggle("open");bg.setAttribute("aria-expanded",o)});
  $$(".nav a").forEach(function(a){a.addEventListener("click",function(){nav.classList.remove("open")})});

  /* comparsa al scroll */
  if("IntersectionObserver" in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add("in");io.unobserve(e.target)}})},{rootMargin:"0px 0px -8% 0px"});
    $$(".reveal").forEach(function(e){io.observe(e)});
  } else $$(".reveal").forEach(function(e){e.classList.add("in")});

  /* mappa caricata al tocco */
  $$(".mapcard").forEach(function(m){
    function load(){if(m.dataset.on)return;m.dataset.on=1;var f=document.createElement("iframe");f.title="Mappa Pop Stop h24 Casavatore";f.loading="lazy";f.referrerPolicy="no-referrer-when-downgrade";f.src=m.dataset.src;m.appendChild(f)}
    m.addEventListener("click",load);
    m.addEventListener("keydown",function(e){if(e.key==="Enter"||e.key===" "){e.preventDefault();load()}});
  });

  /* scheda prodotto */
  var sheet=$("#sheet");
  function apri(nome,stato){
    if(!sheet)return;
    $("#sh-n",sheet).textContent=nome;
    $("#sh-s",sheet).textContent=stato==="ultimi"?"Ultimi pezzi nelle macchine: corri!":"Disponibile ora nelle macchine di Casavatore";
    sheet.classList.add("on");sheet.setAttribute("aria-hidden","false");
    setTimeout(function(){$(".x",sheet).focus()},50);
  }
  function chiudi(){if(sheet){sheet.classList.remove("on");sheet.setAttribute("aria-hidden","true")}}
  if(sheet){
    sheet.addEventListener("click",function(e){if(e.target===sheet||e.target.closest(".x"))chiudi()});
    document.addEventListener("keydown",function(e){if(e.key==="Escape")chiudi()});
  }
  document.addEventListener("click",function(e){
    var b=e.target.closest("[data-p]");
    if(b){e.preventDefault();apri(b.dataset.p,b.dataset.s)}
  });

  /* elenco prodotti dal vivo */
  var box=$("#prodotti");
  if(box){
    var q=$("#q"),chips=$("#chips"),agg=$("#agg"),cat="Tutto",dati=null;
    var ICO=CFG.icone||{};
    var par=new URLSearchParams(location.search);
    if(par.get("cat"))cat=par.get("cat");
    if(par.get("q"))q.value=par.get("q");
    function norm(s){return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"")}
    function render(){
      if(!dati)return;
      var t=norm(q.value.trim());
      var r=dati.filter(function(p){return (cat==="Tutto"||p.c===cat)&&(!t||norm(p.n+" "+p.c).indexOf(t)>-1)});
      var g={};r.forEach(function(p){(g[p.c]=g[p.c]||[]).push(p)});
      box.innerHTML="";
      if(!r.length){box.innerHTML='<p class="empty">Nessun prodotto trovato. Prova un\'altra parola o scrivici su WhatsApp: magari arriva col prossimo carico.</p>';return}
      (CFG.ordine||Object.keys(g)).forEach(function(c){
        if(!g[c])return;
        var s=document.createElement("div");s.className="group";
        var h=document.createElement("h2");h.textContent=(ICO[c]||"")+" "+c;s.appendChild(h);
        var ul=document.createElement("ul");ul.className="plist";
        g[c].forEach(function(p){
          var li=document.createElement("li"),b=document.createElement("button"),n=document.createElement("span"),st=document.createElement("span");
          b.type="button";b.dataset.p=p.n;b.dataset.s=p.s;n.textContent=p.n;
          st.className="st"+(p.s==="ultimi"?" u":"");st.textContent=p.s==="ultimi"?"Ultimi pezzi":"Disponibile";
          b.appendChild(n);b.appendChild(st);li.appendChild(b);ul.appendChild(li);
        });
        s.appendChild(ul);box.appendChild(s);
      });
    }
    function disegnaChips(){
      chips.innerHTML="";
      ["Tutto"].concat(CFG.ordine||[]).forEach(function(c){
        if(c!=="Tutto"&&!dati.some(function(p){return p.c===c}))return;
        var b=document.createElement("button");b.type="button";b.className="chip";b.textContent=(ICO[c]?ICO[c]+" ":"")+c;
        b.setAttribute("aria-pressed",c===cat);
        b.onclick=function(){cat=c;$$(".chip",chips).forEach(function(x){x.setAttribute("aria-pressed",x===b)});render();window.scrollTo({top:box.offsetTop-150,behavior:"smooth"})};
        chips.appendChild(b);
      });
    }
    q.addEventListener("input",render);
    fetch(CFG.stock+"?"+Date.now()).then(function(r){return r.json()}).then(function(d){
      dati=d.prodotti||[];
      agg.textContent=dati.length+" prodotti nelle macchine · aggiornato il "+d.aggiornato;
      disegnaChips();render();
    }).catch(function(){});
  }

  /* conteggio prodotti dal vivo (home) */
  var cnt=$("[data-count]");
  if(cnt&&CFG.stock)fetch(CFG.stock+"?"+Date.now()).then(function(r){return r.json()}).then(function(d){cnt.textContent=(d.prodotti||[]).length}).catch(function(){});
})();
