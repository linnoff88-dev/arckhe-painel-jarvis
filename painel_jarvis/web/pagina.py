"""HTML do painel e do login (uma página, sem build). Instalável no celular: manifesto + sw.js + ícones."""

COR = "#0c0c10"

HEAD = f"""<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark">
<meta name="robots" content="noindex"><meta name="theme-color" content="{COR}"><meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="manifest" href="/manifest.webmanifest" crossorigin="use-credentials"><link rel="icon" href="/icone-192.png"><link rel="apple-touch-icon" href="/icone-180.png">
<script>if('serviceWorker' in navigator)addEventListener('load',function(){{navigator.serviceWorker.register('/sw.js').catch(function(){{}})}})</script>"""

CSS = """:root{--bg:#0c0c10;--card:#15151c;--line:#26262f;--tx:#e7e7ea;--fraco:#8b8b98;--am:#FACC15;--ok:#4ade80;--av:#fbbf24;--er:#f87171}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);font:15px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
header{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:1rem 1.2rem;border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--bg);z-index:2}
h1{font-size:1.15rem;margin:0}h1 b{color:var(--am)}.hora{color:var(--fraco);font-size:.85rem}
.faixa{margin:1rem 1.2rem 0;padding:.7rem 1rem;border-radius:.7rem;border:1px solid #5b2323;background:#1f1012;color:#fca5a5;font-size:.9rem}
.faixa.ok{border-color:#1f4d33;background:#0f1a14;color:#86efac}
main{display:grid;gap:1rem;padding:1rem 1.2rem 2rem;grid-template-columns:repeat(auto-fill,minmax(min(100%,19rem),1fr))}
.c{background:var(--card);border:1px solid var(--line);border-radius:.9rem;padding:1rem 1.1rem;cursor:pointer;border-left:4px solid var(--ok)}
.c.aviso{border-left-color:var(--av)}.c.erro{border-left-color:var(--er)}.c.sem{border-left-color:var(--fraco)}
.c h2{font-size:.82rem;text-transform:uppercase;letter-spacing:.06em;color:var(--fraco);margin:0 0 .3rem;display:flex;justify-content:space-between}
.selo{font-size:.72rem;padding:.05rem .5rem;border-radius:1rem;border:1px solid currentColor;text-transform:none;letter-spacing:0}
.s-ok{color:var(--ok)}.s-aviso{color:var(--av)}.s-erro{color:var(--er)}.s-sem{color:var(--fraco)}
.frase{font-size:1.25rem;font-weight:650;margin:.1rem 0 .6rem}.c.erro .frase{color:var(--er)}.c.aviso .frase{color:var(--av)}
.l{display:flex;justify-content:space-between;gap:.8rem;padding:.22rem 0;border-top:1px solid var(--line);font-size:.88rem}
.l span:first-child{color:var(--fraco);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:50%;flex-shrink:0}.l span:last-child{text-align:right;overflow-wrap:anywhere}
.det{display:none;margin-top:.5rem}.c.aberto .det{display:block}
footer{color:var(--fraco);font-size:.8rem;text-align:center;padding:0 1rem 2rem}footer a{color:var(--fraco)}
button{background:none;border:1px solid var(--line);color:var(--tx);border-radius:.5rem;padding:.35rem .7rem;font:inherit;font-size:.85rem}
.login{max-width:22rem;margin:18vh auto;padding:1.5rem;background:var(--card);border:1px solid var(--line);border-radius:1rem}
.login input{width:100%;padding:.7rem;margin:.8rem 0;border-radius:.5rem;border:1px solid var(--line);background:var(--bg);color:var(--tx);font:inherit}
.login button{width:100%;padding:.7rem;background:var(--am);color:#0c0c10;font-weight:700;border:0}.msg{color:var(--er);font-size:.9rem}"""

JS = r"""(function(){'use strict';
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
var NOME={ok:'ok',aviso:'atenção',erro:'falha',sem:'sem leitura'},abertos={};
function lin(l){return'<div class="l"><span>'+esc(l.rotulo)+'</span><span class="'+(l.estado?'s-'+esc(l.estado):'')+'">'+esc(l.valor)+'</span></div>'}
function desenhar(d){document.title=d.titulo;document.getElementById('tit').innerHTML=esc(d.titulo).replace(/^(\S+)/,'<b>$1</b>');
  var f=document.getElementById('faixa');f.className='faixa'+(d.alertas.length?'':' ok');
  f.textContent=d.alertas.length?d.alertas.length+' ponto(s) de atenção: '+d.alertas.slice(0,4).join(' · '):'Tudo em ordem.';
  document.getElementById('cards').innerHTML=d.cartoes.map(function(c){return'<section class="c '+esc(c.estado)+(abertos[c.id]?' aberto':'')+'" data-id="'+esc(c.id)+'"><h2>'+esc(c.titulo)+'<span class="selo s-'+esc(c.estado)+'">'+(NOME[c.estado]||c.estado)+'</span></h2><p class="frase">'+esc(c.frase)+'</p>'+c.linhas.map(lin).join('')+'<div class="det">'+c.detalhe.map(lin).join('')+'</div></section>'}).join('');
  document.getElementById('hora').textContent='lido às '+new Date(d.gerado_em*1000).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'})}
function semRede(){var f=document.getElementById('faixa');f.className='faixa';f.textContent='Sem conexão com o painel: mostrando a última leitura.'}
function ler(){fetch('/api/painel',{credentials:'same-origin',cache:'no-store'}).then(function(r){if(r.status===401){location.href='/login';throw 0}return r.json()}).then(desenhar).catch(function(e){if(e!==0)semRede()})}
addEventListener('offline',semRede);addEventListener('online',ler);
document.addEventListener('click',function(e){var c=e.target.closest('.c');if(!c)return;abertos[c.dataset.id]=!abertos[c.dataset.id];c.classList.toggle('aberto')});
ler();setInterval(ler,(window.ATUALIZAR||60)*1000);document.addEventListener('visibilitychange',function(){if(!document.hidden)ler()});
})();"""


def painel(titulo, atualizar_s, com_senha):
    sair = '<form method="post" action="/logout"><button>Sair</button></form>' if com_senha else ""
    return f"""<!doctype html><html lang="pt-BR"><head>{HEAD}<title>{titulo}</title><style>{CSS}</style></head><body>
<header><div><h1 id="tit">{titulo}</h1><div class="hora" id="hora">lendo…</div></div>{sair}</header>
<div class="faixa ok" id="faixa">lendo…</div><main id="cards"></main>
<footer>Toque num quadro para ver o detalhe · <a href="https://github.com/inematds/painel-jarvis">painel-jarvis</a></footer>
<script>window.ATUALIZAR={int(atualizar_s)}</script><script>{JS}</script></body></html>"""


def login(titulo, msg=""):
    m = f'<p class="msg">{msg}</p>' if msg else ""
    return f"""<!doctype html><html lang="pt-BR"><head>{HEAD}<title>Entrar · {titulo}</title><style>{CSS}</style></head><body>
<form class="login" method="post" action="/login"><h1><b>{titulo}</b></h1>{m}
<input type="password" name="senha" placeholder="senha" autocomplete="current-password" autofocus required>
<button>Entrar</button><p class="hora">Este aparelho fica lembrado por um ano.</p></form></body></html>"""


def manifesto(titulo):
    return {"name": titulo, "short_name": titulo if len(titulo) <= 12 else "Painel", "start_url": "/", "scope": "/", "id": "/", "display": "standalone",
            "background_color": COR, "theme_color": COR, "lang": "pt-BR",
            "icons": [{"src": "/icone-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
                      {"src": "/icone-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
                      {"src": "/icone-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}


SW = """// painel-jarvis: sem cache (dado ao vivo); sem rede, mostra "sem conexão" em vez do erro do navegador.
self.addEventListener('install',function(){self.skipWaiting()});
self.addEventListener('activate',function(e){e.waitUntil(self.clients.claim())});
self.addEventListener('fetch',function(e){if(e.request.mode!=='navigate')return;
  e.respondWith(fetch(e.request).catch(function(){return new Response('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><body style="background:#0c0c10;color:#e7e7ea;font:16px system-ui;display:grid;place-items:center;height:100vh;margin:0;text-align:center"><div><p style="color:#FACC15;font-weight:700;font-size:1.2rem">Sem conexão com o painel</p><button onclick="location.reload()" style="padding:.7rem 1.3rem;border:0;border-radius:.6rem;background:#FACC15;font-weight:700">Tentar de novo</button></div>',{headers:{'Content-Type':'text/html; charset=utf-8'}})}))});
"""
