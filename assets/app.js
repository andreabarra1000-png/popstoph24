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

  /* POP: occhi che seguono il dito, salto e corsa verso il gioco */
  var pops=$$(".pop .p-pup");
  function guarda(x,y){
    pops.forEach(function(p){
      var sv=p.ownerSVGElement;if(!sv)return;var r=sv.getBoundingClientRect();if(!r.width)return;
      var cx=r.left+r.width/2,cy=r.top+r.height*.33;var dx=x-cx,dy=y-cy,d=Math.sqrt(dx*dx+dy*dy)||1;
      p.style.transform="translate("+(dx/d*5).toFixed(1)+"px,"+(dy/d*5).toFixed(1)+"px)";
    });
  }
  window.addEventListener("pointermove",function(e){guarda(e.clientX,e.clientY)},{passive:true});
  window.addEventListener("touchstart",function(e){var t=e.touches[0];if(t)guarda(t.clientX,t.clientY)},{passive:true});
  var pw=$("a.popwrap");
  if(pw){pw.addEventListener("click",function(e){
    if(e.metaKey||e.ctrlKey)return;e.preventDefault();var u=pw.href;pw.classList.add("scappa");
    var b=$(".bubble",pw);if(b)b.innerHTML="Andiamo a giocare! 🏃";
    setTimeout(function(){location.href=u},700);
  })}
  /* POP che corre: frasi e contachilometri */
  var fr=$("[data-pop-frasi]");
  if(fr){
    var FR=[
      "Corri, POP, corri! 🏃",
      "La vita è come una scatola di snack: non sai mai quello che ti capita 🍫",
      function(){return "Sono le "+oraRoma().txt+" e sto ancora correndo 💨"},
      "Ho corso fino a Secondigliano… e già che c'ero ho continuato 🌴",
      "Sono un po' stanco… ma Pop Stop non chiude mai 😅",
      "Mamma diceva: le macchine piene non si lasciano mai 🧃"
    ],fi=0;
    setInterval(function(){fi=(fi+1)%FR.length;fr.classList.add("cambia");setTimeout(function(){var x=FR[fi];fr.textContent=typeof x==="function"?x():x;fr.classList.remove("cambia")},260)},4200);
  }
  var gg=$("[data-giorni]"),km=$("[data-km]");
  if(gg||km){
    var inizio=Date.UTC(2026,8,10,14,58,0);
    function conta(){var ms=Date.now()-inizio;if(gg)gg.textContent=Math.floor(ms/864e5);if(km)km.textContent=(ms/36e5*8).toLocaleString("it-IT",{minimumFractionDigits:2,maximumFractionDigits:2})}
    conta();setInterval(conta,1000);
  }

  /* contatori */
  if("IntersectionObserver" in window){
    var co=new IntersectionObserver(function(es){es.forEach(function(e){if(!e.isIntersecting)return;co.unobserve(e.target);
      var el=e.target,fin=parseInt(el.textContent,10);if(!fin)return;var t0=performance.now();
      (function step(t){var k=Math.min(1,(t-t0)/1200);el.textContent=Math.round(fin*(1-Math.pow(1-k,3)));if(k<1)requestAnimationFrame(step)})(t0);
    })});
    $$(".facts b").forEach(function(b){if(/^\d+$/.test(b.textContent.trim()))co.observe(b)});
  }

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
  function apri(nome,stato,img,dove,cat){
    if(!sheet)return;
    $("#sh-n",sheet).textContent=nome;
    var bi=$("#sh-i",sheet);bi.innerHTML="";bi.className="pimg big";
    if(img){var im=document.createElement("img");im.src=CFG.img.replace("{}",img);im.alt=nome;bi.appendChild(im)}else{bi.textContent="🛒";bi.className="pimg big ph"}
    $("#sh-m",sheet).textContent=dove?"📍 Lo trovi in: "+dove:"";
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
    if(b){e.preventDefault();apri(b.dataset.p,b.dataset.s,b.dataset.i,b.dataset.d)}
  });

  /* elenco prodotti dal vivo */
  var box=$("#prodotti");
  if(box){
    var q=$("#q"),chips=$("#chips"),agg=$("#agg"),cat="Tutto",dati=null;
    var ICO=CFG.icone||{};
    var par=new URLSearchParams(location.search);
    if(par.get("cat"))cat=par.get("cat");
    if(par.get("q"))q.value=par.get("q");
    function dove(m){var per={};m.forEach(function(x){(per[x[0]]=per[x[0]]||[]).push(x[1])});
      var POS={1:"1ª macchina da sinistra",2:"2ª macchina da sinistra",3:"2ª macchina da destra",4:"1ª macchina da destra"};
      return Object.keys(per).sort().map(function(k){return (POS[k]||"Macchina "+k)+" · n. "+per[k].join(", ")}).join(" · ")}
    function norm(s){return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"")}
    function render(){
      if(!dati)return;
      var t=norm(q.value.trim());
      var r=dati.filter(function(p){return (cat==="Tutto"||p.c===cat)&&(!t||norm(p.n+" "+p.c+" "+dove(p.m||[])).indexOf(t)>-1)});
      var g={};r.forEach(function(p){(g[p.c]=g[p.c]||[]).push(p)});
      box.innerHTML="";
      if(!r.length){box.innerHTML='<p class="empty">Nessun prodotto trovato. Prova un\'altra parola o scrivici su WhatsApp: magari arriva col prossimo carico.</p>';return}
      (CFG.ordine||Object.keys(g)).forEach(function(c){
        if(!g[c])return;
        var s=document.createElement("div");s.className="group";
        var h=document.createElement("h2");h.textContent=(ICO[c]||"")+" "+c;s.appendChild(h);
        var ul=document.createElement("ul");ul.className="plist";
        g[c].forEach(function(p){
          var li=document.createElement("li"),b=document.createElement("button");
          var d=dove(p.m||[]);
          b.type="button";b.className="pc";b.dataset.p=p.n;b.dataset.s=p.s;b.dataset.i=p.i||"";b.dataset.d=d;
          var wi=document.createElement("span");wi.className="pimg";
          if(p.i){var im=document.createElement("img");im.src=CFG.img.replace("{}",p.i);im.alt=p.n;im.loading="lazy";im.width=160;im.height=160;
            im.onerror=function(){var ph=document.createElement("span");ph.className="ph";ph.textContent=ICO[p.c]||"🛒";im.replaceWith(ph)};wi.appendChild(im)}
          else{var ph=document.createElement("span");ph.className="ph";ph.textContent=ICO[p.c]||"🛒";wi.appendChild(ph)}
          var n=document.createElement("span");n.className="pn";n.textContent=p.n;
          var m=document.createElement("span");m.className="pm";m.textContent="📍 "+d;
          var st=document.createElement("span");st.className="st"+(p.s==="ultimi"?" u":"");st.textContent=p.s==="ultimi"?"Ultimi pezzi":"Disponibile";
          b.appendChild(wi);b.appendChild(n);if(d)b.appendChild(m);b.appendChild(st);li.appendChild(b);ul.appendChild(li);
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
