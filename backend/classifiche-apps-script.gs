/* Classifiche giochi Pop Stop h24 – Google Apps Script collegato al foglio «Classifiche giochi Pop Stop».
   Distribuzione: App web, Esegui come «Me», Accesso «Chiunque».
   GET  ?g=<gioco>            -> {settimana:[...], sempre:[...]}
   POST {g, n, ig, p}         -> {settimana, sempre, pos}  */
var GIOCHI = {riempi: 20000, corri: 200000, squalo: 100000, dino: 100000, spazio: 100000, laser: 100000, fantasmi: 100000};
var BRUTTE = /(cazz|merd|stronz|vaffa|fancul|puttan|troi|zoccol|ricchion|froci|negr|bastard|coglion|minchi|figa|culo|porc[oa]d|madonn|sucat|bocchin|pompin|chiavat|sborr|hitler|nazi|porn|camorr|mafia|uccid|ammazz)/i;

function foglio_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName('punteggi') || ss.insertSheet('punteggi');
  if (sh.getLastRow() === 0) sh.appendRow(['data', 'gioco', 'nome', 'instagram', 'punti', 'nascosto']);
  return sh;
}
function lunedi_() { var d = new Date(); var g = (d.getDay() + 6) % 7; d.setHours(0, 0, 0, 0); d.setDate(d.getDate() - g); return d; }
function classifiche_(gioco) {
  var rows = foglio_().getDataRange().getValues().slice(1).filter(function (r) { return r[1] === gioco && !r[5]; });
  var inizio = lunedi_().getTime();
  function top(lista) {
    var best = {};
    lista.forEach(function (r) { var k = String(r[2]).toLowerCase(); if (!best[k] || r[4] > best[k].p) best[k] = {n: r[2], ig: r[3] || '', p: r[4]}; });
    return Object.keys(best).map(function (k) { return best[k]; }).sort(function (a, b) { return b.p - a.p; }).slice(0, 10);
  }
  return {settimana: top(rows.filter(function (r) { return new Date(r[0]).getTime() >= inizio; })), sempre: top(rows)};
}
function out_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
function doGet(e) {
  var g = (e.parameter.g || '').toLowerCase();
  if (!GIOCHI[g]) return out_({err: 'Gioco sconosciuto'});
  return out_(classifiche_(g));
}
function doPost(e) {
  var d; try { d = JSON.parse(e.postData.contents); } catch (x) { return out_({err: 'Dati non validi'}); }
  var g = String(d.g || '').toLowerCase(), n = String(d.n || '').replace(/[<>"'`\\]/g, '').trim().slice(0, 14);
  var ig = String(d.ig || '').replace(/^@/, '').toLowerCase().slice(0, 30), p = Math.floor(Number(d.p));
  if (!GIOCHI[g]) return out_({err: 'Gioco sconosciuto'});
  if (n.length < 3 || BRUTTE.test(n) || /https?:|www\.|\d{6,}/i.test(n)) return out_({err: 'Nome non valido: niente parolacce né link.'});
  if (ig && (!/^[a-z0-9._]{2,30}$/.test(ig) || BRUTTE.test(ig))) return out_({err: 'Nome Instagram non valido.'});
  if (!(p > 0) || p > GIOCHI[g]) return out_({err: 'Punteggio non valido.'});
  var lock = LockService.getScriptLock(); lock.waitLock(5000);
  try {
    var cache = CacheService.getScriptCache(), k = 'r_' + n.toLowerCase();
    if (cache.get(k)) return out_({err: 'Aspetta qualche secondo prima di salvare di nuovo.'});
    cache.put(k, '1', 10);
    foglio_().appendRow([new Date(), g, n, ig, p, '']);
  } finally { lock.releaseLock(); }
  var c = classifiche_(g), pos = 0;
  c.settimana.forEach(function (x, i) { if (!pos && x.n.toLowerCase() === n.toLowerCase()) pos = i + 1; });
  c.pos = pos; return out_(c);
}
