/* Classifiche dei giochi di POP.
   Si attiva solo quando API contiene l'indirizzo del database (Apps Script).
   Legge il punteggio dalla schermata finale di ogni gioco: non tocca la logica dei giochi. */
(function(){
  "use strict";
  var API = ""; // es. "https://script.google.com/macros/s/XXXX/exec"
  if(!API) return;

  var path = location.pathname.replace(/\/+$/,"").split("/");
  var i = path.indexOf("gioco");
  if(i < 0) return;
  var GIOCO = path[i+1] || "riempi";

  var BRUTTE = /(cazz|merd|stronz|vaffa|fancul|puttan|troi|zoccol|ricchion|froci|frocio|negr|bastard|coglion|minchi|figa|fica\b|culo|porc[oa]d|dio\s?c|madonn|sucat|bocchin|pompin|chiavat|sborr|pippa|mannaggia|hitler|nazi|duce|kkk|sesso|porn|xxx|fottut|cesso|scem|mongol|handicap|down\b|testa ?di|faccia ?di|camorr|mafia|uccid|ammazz|morte)/i;
  var LINK = /(https?:|www\.|\.com|\.it|\.net|\d{6,}|@.*@)/i;

  function pulisci(s, max){ return String(s||"").replace(/[<>"'`\\]/g,"").replace(/\s+/g," ").trim().slice(0,max); }
  function nomeOk(n){ return n.length>=3 && n.length<=14 && !BRUTTE.test(n.replace(/[^a-zàèéìòù]/gi,"")) && !BRUTTE.test(n) && !LINK.test(n); }
  function igOk(ig){ return !ig || (/^[a-z0-9._]{2,30}$/i.test(ig) && !BRUTTE.test(ig)); }

  function get(){ return fetch(API+"?g="+encodeURIComponent(GIOCO)+"&t="+Date.now()).then(function(r){return r.json()}); }
  function post(d){ return fetch(API,{method:"POST",body:JSON.stringify(d)}).then(function(r){return r.json()}); }

  var css = document.createElement("style");
  css.textContent =
    ".pclass{margin:18px auto 6px;max-width:460px;text-align:left;background:rgba(6,18,25,.72);border:3px solid #061219;border-radius:18px;padding:14px 14px 10px;color:#fff;box-shadow:4px 4px 0 #061219}"+
    ".pclass h3{margin:0 0 8px;font:800 1.2rem var(--fd,sans-serif);color:#ffd23f}"+
    ".pclass form{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px}"+
    ".pclass input{flex:1 1 140px;min-width:0;padding:10px 12px;border-radius:12px;border:2px solid #061219;font:600 1rem system-ui,sans-serif}"+
    ".pclass button{padding:10px 14px;border-radius:12px;border:2px solid #061219;background:#ffd23f;color:#061219;font:800 1rem system-ui,sans-serif;cursor:pointer}"+
    ".pclass .tabs{display:flex;gap:6px;margin:4px 0 8px}.pclass .tabs button{background:transparent;color:#fff;border-color:#fff;padding:6px 10px;font-size:.85rem}.pclass .tabs button.on{background:#fff;color:#061219}"+
    ".pclass ol{margin:0;padding:0;list-style:none;counter-reset:p}.pclass li{display:flex;gap:8px;align-items:center;padding:6px 4px;border-bottom:1px solid rgba(255,255,255,.12);font:600 .95rem system-ui,sans-serif}"+
    ".pclass li b{min-width:28px;color:#ffd23f}.pclass li span{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.pclass li em{font-style:normal;font-weight:800}"+
    ".pclass li a{color:#19d6c8;text-decoration:none;font-size:.85rem}.pclass li.me{background:rgba(255,210,63,.18);border-radius:8px}"+
    ".pclass .msg{min-height:1.2em;font:700 .9rem system-ui,sans-serif;color:#3ee07a;margin:0 0 6px}.pclass .msg.err{color:#ff8a8a}"+
    ".pclass small{display:block;opacity:.7;margin-top:6px;font-size:.75rem}"+
    ".pcrown{margin:10px auto 0;font:800 1rem system-ui,sans-serif;color:#ffd23f;text-align:center}";
  document.head.appendChild(css);

  var dati = {settimana:[], sempre:[]}, vista = "settimana", mio = null;
  try{ mio = JSON.parse(localStorage.getItem("pop-classifica-io")||"null"); }catch(e){}

  function riga(x, pos){
    var me = mio && x.n===mio.n ? " me" : "";
    var ig = x.ig ? ' <a href="https://instagram.com/'+encodeURIComponent(x.ig)+'" target="_blank" rel="noopener nofollow">@'+x.ig+'</a>' : "";
    var medaglia = pos===1?"🥇":pos===2?"🥈":pos===3?"🥉":pos+"°";
    return '<li class="'+me+'"><b>'+medaglia+'</b><span>'+x.n.replace(/</g,"")+ig+'</span><em>'+x.p+'</em></li>';
  }
  function lista(box){
    var l = dati[vista]||[];
    box.querySelector("ol").innerHTML = l.length ? l.map(function(x,k){return riga(x,k+1)}).join("") : "<li><span>Nessuno ancora: il primo posto è libero!</span></li>";
    box.querySelectorAll(".tabs button").forEach(function(b){b.classList.toggle("on",b.dataset.v===vista)});
  }

  function pannello(end){
    var box = end.querySelector(".pclass");
    if(box) return box;
    box = document.createElement("div"); box.className = "pclass";
    box.innerHTML = '<h3>🏆 Classifica</h3>'+
      '<form><input name="n" maxlength="14" placeholder="Il tuo nome" autocomplete="nickname" required>'+
      '<input name="ig" maxlength="31" placeholder="@instagram (facoltativo)" autocapitalize="off">'+
      '<button type="submit">Entra in classifica</button></form>'+
      '<p class="msg" aria-live="polite"></p>'+
      '<div class="tabs"><button type="button" data-v="settimana">Questa settimana</button><button type="button" data-v="sempre">Di sempre</button></div>'+
      '<ol></ol><small>I primi della settimana li annunciamo su Instagram @popstoph24 ogni lunedì. Niente parolacce: i nomi offensivi vengono tolti.</small>';
    var ref = end.querySelector(".row") || end.lastElementChild;
    ref.parentNode.insertBefore(box, ref.nextSibling);
    box.querySelectorAll(".tabs button").forEach(function(b){ b.addEventListener("click", function(e){ e.stopPropagation(); vista=b.dataset.v; lista(box); }); });
    box.addEventListener("click", function(e){ e.stopPropagation(); });
    box.addEventListener("touchstart", function(e){ e.stopPropagation(); }, {passive:true});
    var f = box.querySelector("form");
    if(mio){ f.n.value = mio.n; f.ig.value = mio.ig ? "@"+mio.ig : ""; }
    f.addEventListener("submit", function(e){
      e.preventDefault(); e.stopPropagation();
      var msg = box.querySelector(".msg"); msg.className = "msg";
      var n = pulisci(f.n.value, 14), ig = pulisci(f.ig.value, 31).replace(/^@/,"").toLowerCase();
      if(!nomeOk(n)){ msg.className="msg err"; msg.textContent="Scegli un nome di 3-14 lettere, senza parolacce né link."; return; }
      if(!igOk(ig)){ msg.className="msg err"; msg.textContent="Il nome Instagram non sembra valido."; return; }
      var p = box.dataset.punti|0;
      if(p <= 0){ msg.className="msg err"; msg.textContent="Fai almeno un punto per entrare in classifica!"; return; }
      f.querySelector("button").disabled = true; msg.textContent = "Salvo…";
      mio = {n:n, ig:ig}; try{ localStorage.setItem("pop-classifica-io", JSON.stringify(mio)); }catch(_){}
      post({g:GIOCO, n:n, ig:ig, p:p}).then(function(r){
        if(r.err){ msg.className="msg err"; msg.textContent=r.err; f.querySelector("button").disabled=false; return; }
        dati = r; lista(box);
        msg.textContent = r.pos ? "Sei "+r.pos+"° questa settimana! "+(r.pos<=3?"🔥 Sei sul podio!":"Riprova per salire 💪") : "Salvato!";
        box.dataset.inviato = "1";
      }).catch(function(){ msg.className="msg err"; msg.textContent="Connessione assente: riprova tra poco."; f.querySelector("button").disabled=false; });
    });
    return box;
  }

  function aggiorna(box){ get().then(function(r){ dati = r; lista(box); }).catch(function(){}); }

  function onFine(end){
    var fin = end.querySelector("#c-fin, #g-fin");
    var p = fin && fin.querySelector("b") ? parseInt(fin.querySelector("b").textContent,10) : 0;
    var box = pannello(end);
    box.dataset.punti = p; box.dataset.inviato = "";
    var btn = box.querySelector("form button"); btn.disabled = false;
    box.querySelector(".msg").textContent = p>0 ? "Hai fatto "+p+" punti: mettili in classifica!" : "";
    aggiorna(box);
  }

  function corona(start){
    get().then(function(r){
      var top = (r.settimana||[])[0];
      if(!top) return;
      var c = start.querySelector(".pcrown") || document.createElement("p");
      c.className = "pcrown";
      c.textContent = "👑 Da battere questa settimana: "+top.n+" con "+top.p+" punti";
      if(!c.parentNode) start.appendChild(c);
    }).catch(function(){});
  }

  function avvia(){
    var end = document.querySelector("#c-end, #g-end"), start = document.querySelector("#c-start, #g-start");
    if(start) corona(start);
    if(!end) return;
    new MutationObserver(function(){ if(!end.hidden) onFine(end); }).observe(end, {attributes:true, attributeFilter:["hidden"]});
  }
  if(document.readyState === "loading") document.addEventListener("DOMContentLoaded", avvia); else avvia();
})();
