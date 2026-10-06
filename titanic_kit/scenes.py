"""Immersive scenes (night sea, dawn lifeboat, abyss, passenger field).

Every scene is a self-contained HTML document (inline SVG + CSS + a little
JavaScript) that Streamlit renders inside an iframe via `components.html`,
so animations work without any external image files.

Optional: drop real photos into /assets (hero.jpg, ...) and the hero scene
will blend them in automatically.
"""
from __future__ import annotations

import base64
import json
import math
from pathlib import Path

import streamlit as st

ASSETS = Path(__file__).resolve().parents[1] / "assets"

HEAD = """
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700;900&family=Karla:wght@400;500&display=swap');
*{box-sizing:border-box}
html,body{margin:0;height:100%;overflow:hidden;background:#02060f;font-family:'Karla',system-ui,sans-serif;color:#eef3fa}
.scene{position:relative;width:100%;height:100vh;overflow:hidden}
.abs{position:absolute}
.title{font-family:'Cinzel',Georgia,serif;letter-spacing:.14em;text-transform:uppercase}
</style>
"""


def render(html: str, height: int = 560) -> None:
    """Show an HTML document in an iframe (new st.iframe, old components.html as fallback)."""
    if hasattr(st, "iframe"):
        st.iframe(html, height=height)
    else:  # older Streamlit versions
        import streamlit.components.v1 as components
        components.html(html, height=height, scrolling=False)


# ----------------------------------------------------------------- helpers
def wave_path(width: int, amp: float, k: int, base: float, phase: float = 0.0,
              height: int = 400) -> str:
    """A perfectly periodic sine-wave 'water' shape (tiles seamlessly)."""
    pts = []
    step = 20
    for x in range(0, width + step, step):
        y = base + amp * math.sin(2 * math.pi * k * x / width + phase)
        pts.append(f"{x},{y:.1f}")
    return "M" + " L".join(pts) + f" L{width},{height} L0,{height} Z"


def ship_svg(funnel="#b9893f", funnel_top="#0a0a0a", hull="#05080f",
             deck="#0b0f18", lights=True, uid="s") -> str:
    """Side view of an Olympic-class liner, bow to the right."""
    ports = ""
    wins = ""
    if lights:
        for i, x in enumerate(range(48, 600, 11)):
            ports += f'<circle cx="{x}" cy="127" r="1.7" class="lt" style="animation-delay:{(i*0.37)%3:.2f}s"/>'
        for row, y in enumerate((88, 98)):
            for i, x in enumerate(range(125, 515, 9)):
                if (i + row) % 5 != 0:
                    wins += f'<rect x="{x}" y="{y}" width="3.2" height="4" class="lt" style="animation-delay:{((i*7+row*3)%11)/4:.2f}s"/>'
        for i, x in enumerate(range(160, 470, 10)):
            wins += f'<rect x="{x}" y="70" width="3" height="4" class="lt" style="animation-delay:{(i%7)/3:.2f}s"/>'
    funnels = ""
    for x in (190, 258, 326, 394):
        funnels += (
            f'<path d="M{x-17},82 L{x-14},22 Q{x},16 {x+14},22 L{x+17},82 Z" fill="{funnel}"/>'
            f'<path d="M{x-14.5},30 Q{x},24 {x+14.5},30 L{x+14},22 Q{x},16 {x-14},22 Z" fill="{funnel_top}"/>'
            f'<rect x="{x-17}" y="76" width="34" height="6" fill="{deck}" opacity=".6"/>'
        )
    return f"""
<svg viewBox="0 0 660 190" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;overflow:visible">
  <style>.lt{{fill:#ffd77a;opacity:.9;animation:fl 3.2s ease-in-out infinite}}
  @keyframes fl{{0%,100%{{opacity:.95}}45%{{opacity:.55}}}}</style>
  <line x1="92" y1="108" x2="92" y2="40" stroke="{hull}" stroke-width="2.4"/>
  <line x1="590" y1="108" x2="592" y2="30" stroke="{hull}" stroke-width="2.4"/>
  <line x1="92" y1="42" x2="150" y2="108" stroke="{hull}" stroke-width=".8"/>
  <line x1="592" y1="32" x2="540" y2="108" stroke="{hull}" stroke-width=".8"/>
  <path d="M14,150 L10,108 L560,108 Q625,104 646,96 Q628,140 585,150 Z" fill="{hull}"/>
  <path d="M10,108 L560,108 Q625,104 646,96 L646,100 Q620,111 560,112 L10,112 Z" fill="#7a1f1f" opacity=".0"/>
  <rect x="112" y="84" width="408" height="24" fill="{deck}"/>
  <rect x="140" y="64" width="340" height="20" fill="{deck}"/>
  <rect x="520" y="76" width="40" height="32" fill="{deck}"/>
  <rect x="528" y="62" width="22" height="14" fill="{deck}"/>
  {funnels}
  {ports}{wins}
  <rect x="10" y="108" width="636" height="2.5" fill="#d9c28a" opacity=".35"/>
</svg>"""


FISH_DEF = """
<svg width="0" height="0" style="position:absolute"><defs>
<symbol id="fish" viewBox="0 0 64 32"><path d="M3,16 C14,1 36,1 50,16 C36,31 14,31 3,16 Z"/><path d="M47,16 L63,3 Q58,16 63,29 Z"/><path d="M22,5 Q30,-1 36,6 Z" opacity=".8"/><circle cx="13" cy="13" r="2.2" fill="#02101c"/></symbol>
<symbol id="person" viewBox="0 0 60 120">
  <circle cx="30" cy="12" r="9"/>
  <path d="M22,24 Q30,20 38,24 L40,62 Q30,68 20,62 Z"/>
  <path d="M22,26 Q8,14 6,0 L11,0 Q14,14 26,28 Z"/>
  <path d="M38,26 Q52,16 56,2 L51,0 Q46,14 34,28 Z"/>
  <path d="M22,60 Q18,92 12,118 L19,119 Q28,94 30,70 Z"/>
  <path d="M38,60 Q44,90 50,112 L43,115 Q34,92 30,70 Z"/>
</symbol></defs></svg>"""


# ------------------------------------------------------------------- hero
def hero_scene(title="R.M.S. Titanic", subtitle="Would you have survived the night of 14 April 1912?") -> str:
    photo_css = ""
    for name in ("hero.jpg", "hero.jpeg", "hero.png"):
        f = ASSETS / name
        if f.exists():
            b64 = base64.b64encode(f.read_bytes()).decode()
            mime = "image/png" if name.endswith("png") else "image/jpeg"
            photo_css = (f".photo{{position:absolute;inset:0;background:url(data:{mime};base64,{b64}) center/cover;"
                         "opacity:.42;mix-blend-mode:screen}")
    w = 1600
    back = wave_path(w, 9, 4, 30, 0.0)
    mid = wave_path(w, 13, 3, 30, 1.7)
    front = wave_path(w, 17, 2, 30, 3.1)
    ship = ship_svg()
    return f"""<!doctype html><html><head>{HEAD}<style>
.sky{{position:absolute;inset:0;background:linear-gradient(#01040b 0%,#06142b 38%,#12335a 62%,#2a5a86 70%)}}
.star{{position:absolute;width:2px;height:2px;border-radius:50%;background:#fff;animation:tw 4s infinite ease-in-out}}
@keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:1}}}}
.moon{{position:absolute;right:11%;top:11%;width:84px;height:84px;border-radius:50%;
  background:radial-gradient(circle at 35% 35%,#fffdf0,#e9e2c0 60%,#cfc79d);box-shadow:0 0 60px 18px rgba(255,248,210,.28),0 0 160px 60px rgba(150,190,255,.12)}}
.sea{{position:absolute;left:0;right:0;bottom:0;height:42%;background:linear-gradient(#10304f,#031020)}}
.wv{{position:absolute;left:0;bottom:0;width:200%;display:flex;animation:drift linear infinite}}
.wv svg{{width:50%;display:block}}
@keyframes drift{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}
.shipwrap{{position:absolute;left:50%;bottom:15%;width:min(78vw,760px);margin-left:calc(min(78vw,760px) / -2);animation:bob 7s ease-in-out infinite;aspect-ratio:660/190}}
@keyframes bob{{0%,100%{{transform:translateY(0) rotate(-.4deg)}}50%{{transform:translateY(7px) rotate(.5deg)}}}}
.smoke{{position:absolute;border-radius:50%;background:rgba(190,200,215,.16);filter:blur(7px);animation:puff 9s linear infinite}}
@keyframes puff{{0%{{transform:translate(0,0) scale(.5);opacity:0}}15%{{opacity:.5}}100%{{transform:translate(-260px,-70px) scale(3.4);opacity:0}}}}
.glint{{position:absolute;right:calc(11% + 20px);bottom:0;width:44px;height:42%;
  background:repeating-linear-gradient(transparent 0 7px,rgba(255,246,200,.35) 7px 9px);filter:blur(1px);
  mask-image:linear-gradient(transparent,#000 15%,#000);animation:shim 3s ease-in-out infinite}}
@keyframes shim{{0%,100%{{opacity:.5;transform:scaleX(1)}}50%{{opacity:.9;transform:scaleX(1.5)}}}}
.berg{{position:absolute;right:3%;bottom:33%;width:210px;opacity:.9;filter:drop-shadow(0 0 22px rgba(170,215,255,.35))}}
.photo{{display:none}}{photo_css}
.hud{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;padding-top:3.2%;text-align:center;
  background:linear-gradient(rgba(1,4,11,.55),transparent 45%)}}
.hud .t1{{font-size:clamp(13px,1.5vw,18px);color:#d9b66b;letter-spacing:.5em}}
.hud h1{{margin:.1em 0 .15em;font-family:'Cinzel',serif;font-weight:900;font-size:clamp(40px,8vw,104px);letter-spacing:.12em;
  background:linear-gradient(#fff6dc,#d9b66b 60%,#9c7a34);-webkit-background-clip:text;color:transparent;text-shadow:0 6px 40px rgba(0,0,0,.4)}}
.hud p{{margin:0;font-size:clamp(14px,1.7vw,21px);color:#cfe0f5;max-width:760px;padding:0 20px;font-style:italic;letter-spacing:.02em}}
.rule{{width:180px;height:1px;background:linear-gradient(90deg,transparent,#d9b66b,transparent);margin:14px auto}}
.cue{{position:absolute;bottom:14px;left:0;right:0;text-align:center;font-size:12px;letter-spacing:.3em;color:#9fb8d6;opacity:.8;text-transform:uppercase}}
</style></head><body><div class="scene">
<div class="sky" id="sky"></div><div class="photo"></div><div class="moon"></div>
<svg class="berg" viewBox="0 0 210 110"><path d="M0,110 L28,70 L52,78 L88,22 L112,48 L134,30 L170,74 L196,66 L210,110Z" fill="#cfe4f5"/><path d="M88,22 L112,48 L98,70 L70,60Z" fill="#9fc3df" opacity=".6"/><path d="M134,30 L170,74 L140,80Z" fill="#9fc3df" opacity=".5"/></svg>
<div class="sea"></div><div class="glint"></div>
<div class="wv" style="height:30%;bottom:19%;animation-duration:70s;opacity:.95"><svg viewBox="0 0 {w} 400" preserveAspectRatio="none" style="height:100%"><path d="{back}" fill="#0b2a49"/></svg><svg viewBox="0 0 {w} 400" preserveAspectRatio="none" style="height:100%"><path d="{back}" fill="#0b2a49"/></svg></div>
<div class="shipwrap">{ship}
  <span class="smoke" style="left:27%;top:-4%;width:30px;height:30px;animation-delay:0s"></span>
  <span class="smoke" style="left:39%;top:-4%;width:30px;height:30px;animation-delay:2.4s"></span>
  <span class="smoke" style="left:50%;top:-4%;width:30px;height:30px;animation-delay:4.8s"></span>
  <span class="smoke" style="left:61%;top:-4%;width:30px;height:30px;animation-delay:7s"></span>
</div>
<div class="wv" style="height:24%;bottom:12%;animation-duration:42s"><svg viewBox="0 0 {w} 400" preserveAspectRatio="none" style="height:100%"><path d="{mid}" fill="#08213b"/></svg><svg viewBox="0 0 {w} 400" preserveAspectRatio="none" style="height:100%"><path d="{mid}" fill="#08213b"/></svg></div>
<div class="wv" style="height:22%;bottom:0;animation-duration:26s"><svg viewBox="0 0 {w} 400" preserveAspectRatio="none" style="height:100%"><path d="{front}" fill="#031428"/></svg><svg viewBox="0 0 {w} 400" preserveAspectRatio="none" style="height:100%"><path d="{front}" fill="#031428"/></svg></div>
<div class="hud"><div class="t1 title">White Star Line</div><h1>{title}</h1><div class="rule"></div><p>{subtitle}</p></div>
<div class="cue">Southampton &nbsp;→&nbsp; New York &nbsp;·&nbsp; April 1912</div>
</div>
<script>
const sky=document.getElementById('sky');
for(let i=0;i<110;i++){{const s=document.createElement('i');s.className='star';
 s.style.left=Math.random()*100+'%';s.style.top=Math.random()*52+'%';
 s.style.animationDelay=(Math.random()*4)+'s';s.style.width=s.style.height=(Math.random()*2+1)+'px';sky.appendChild(s);}}
</script></body></html>"""


# --------------------------------------------------------- survived scene
def survived_scene(title: str, subtitle: str) -> str:
    w = 1600
    sea1 = wave_path(w, 7, 5, 30, 0.4)
    sea2 = wave_path(w, 11, 3, 30, 2.0)
    sea3 = wave_path(w, 15, 2, 30, 4.0)
    ship = ship_svg(funnel="#3a2a22", funnel_top="#120c0a", hull="#150f12", deck="#1d1519", lights=False)
    heads = ""
    for i, x in enumerate(range(34, 232, 24)):
        heads += (f'<circle cx="{x}" cy="{34 + (i%2)*2}" r="7" fill="#120b10"/>'
                  f'<path d="M{x-9},{58} Q{x},{40+(i%2)*2} {x+9},{58} Z" fill="#120b10"/>')
    return f"""<!doctype html><html><head>{HEAD}<style>
.sky{{position:absolute;inset:0;background:linear-gradient(#1d2547 0%,#5b4a7a 28%,#e98c6b 52%,#ffc98a 64%,#ffe6b8 68%)}}
.sun{{position:absolute;left:50%;top:40%;width:200px;height:200px;margin-left:-100px;border-radius:50%;
  background:radial-gradient(circle,#fff9e0 0%,#ffe29a 38%,rgba(255,170,90,.0) 70%);animation:rise 14s ease-out forwards;filter:blur(1px)}}
@keyframes rise{{from{{transform:translateY(90px) scale(.8)}}to{{transform:translateY(-28px) scale(1.05)}}}}
.sea{{position:absolute;left:0;right:0;bottom:0;height:36%;background:linear-gradient(#e0a06f,#35506e 55%,#0e2036)}}
.wv{{position:absolute;left:0;width:200%;display:flex;animation:drift linear infinite}}
.wv svg{{width:50%;display:block}}
@keyframes drift{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}
.sunpath{{position:absolute;left:50%;margin-left:-60px;bottom:0;width:120px;height:36%;
  background:repeating-linear-gradient(transparent 0 6px,rgba(255,236,170,.65) 6px 9px);mask-image:linear-gradient(transparent,#000 20%);animation:shim 2.6s ease-in-out infinite}}
@keyframes shim{{0%,100%{{opacity:.6;transform:scaleX(1)}}50%{{opacity:1;transform:scaleX(1.5)}}}}
.far{{position:absolute;right:9%;bottom:34.5%;width:200px;opacity:.9}}
.berg{{position:absolute;bottom:35%;opacity:.95}}
.boat{{position:absolute;left:50%;bottom:13%;width:min(46vw,430px);margin-left:calc(min(46vw,430px) / -2);animation:rock 5s ease-in-out infinite;transform-origin:50% 90%}}
@keyframes rock{{0%,100%{{transform:rotate(-2.2deg) translateY(0)}}50%{{transform:rotate(2.2deg) translateY(8px)}}}}
.bird{{position:absolute;font-size:18px;color:#2b1f2f;animation:fly linear infinite}}
@keyframes fly{{from{{transform:translateX(-80px)}}to{{transform:translateX(110vw)}}}}
.hud{{position:absolute;left:0;right:0;top:0;padding-top:34px;text-align:center;background:linear-gradient(rgba(14,20,45,.65),transparent)}}
.hud .t1{{font-size:13px;letter-spacing:.5em;color:#ffd9a0}}
.hud h1{{margin:.2em 0;font-family:'Cinzel',serif;font-weight:900;font-size:clamp(30px,5.6vw,66px);letter-spacing:.1em;color:#fff3d6;text-shadow:0 4px 30px rgba(0,0,0,.5)}}
.hud p{{margin:0 auto;max-width:720px;font-style:italic;font-size:clamp(14px,1.5vw,19px);color:#ffe9cc;padding:0 18px}}
</style></head><body><div class="scene">
<div class="sky"></div><div class="sun"></div>
<svg class="berg" style="left:6%;width:190px" viewBox="0 0 210 110"><path d="M0,110 L30,64 L58,72 L96,18 L122,46 L150,24 L186,70 L210,110Z" fill="#f7efe8"/><path d="M96,18 L122,46 L104,72 L74,60Z" fill="#c9b6c9" opacity=".7"/></svg>
<svg class="berg" style="left:27%;width:110px;bottom:35.5%" viewBox="0 0 210 110"><path d="M0,110 L40,60 L84,66 L120,28 L160,70 L210,110Z" fill="#f2e6e0"/></svg>
<div class="far">{ship}</div>
<div class="sea"></div><div class="sunpath"></div>
<div class="wv" style="height:20%;bottom:20%;animation-duration:60s;opacity:.85"><svg viewBox="0 0 {w} 400" preserveAspectRatio="none" style="height:100%"><path d="{sea1}" fill="#b97d62"/></svg><svg viewBox="0 0 {w} 400" preserveAspectRatio="none" style="height:100%"><path d="{sea1}" fill="#b97d62"/></svg></div>
<div class="wv" style="height:22%;bottom:8%;animation-duration:36s"><svg viewBox="0 0 {w} 400" preserveAspectRatio="none" style="height:100%"><path d="{sea2}" fill="#27405f"/></svg><svg viewBox="0 0 {w} 400" preserveAspectRatio="none" style="height:100%"><path d="{sea2}" fill="#27405f"/></svg></div>
<div class="boat"><svg viewBox="0 0 280 110" style="width:100%"><g>
  <line x1="20" y1="64" x2="-30" y2="102" stroke="#120b10" stroke-width="3"/><line x1="262" y1="64" x2="312" y2="102" stroke="#120b10" stroke-width="3"/>
  {heads}
  <path d="M4,60 Q140,92 276,60 L262,84 Q140,106 18,84 Z" fill="#1a0f14"/><path d="M4,60 Q140,92 276,60" fill="none" stroke="#c99a5a" stroke-width="2"/></g></svg></div>
<div class="wv" style="height:20%;bottom:0;animation-duration:20s"><svg viewBox="0 0 {w} 400" preserveAspectRatio="none" style="height:100%"><path d="{sea3}" fill="#0e2036"/></svg><svg viewBox="0 0 {w} 400" preserveAspectRatio="none" style="height:100%"><path d="{sea3}" fill="#0e2036"/></svg></div>
<span class="bird" style="top:24%;animation-duration:38s">⌄ ⌄</span><span class="bird" style="top:31%;animation-duration:52s;animation-delay:-20s;font-size:14px">⌄</span>
<div class="hud"><div class="t1 title">Dawn · 15 April 1912</div><h1>{title}</h1><p>{subtitle}</p></div>
</div></body></html>"""


# ------------------------------------------------------------- lost scene
def lost_scene(title: str, subtitle: str) -> str:
    w = 1600
    surf = wave_path(w, 8, 4, 30, 0.8)
    ship = ship_svg(funnel="#162536", funnel_top="#0a1420", hull="#0a1522", deck="#101d2d", lights=True)
    return f"""<!doctype html><html><head>{HEAD}<style>
.water{{position:absolute;left:0;right:0;top:15%;bottom:0;background:linear-gradient(#1c5d86 0%,#0d3556 22%,#06182c 55%,#010509 100%)}}
.air{{position:absolute;left:0;right:0;top:0;height:16%;background:linear-gradient(#01040b,#0a1d38)}}
.star{{position:absolute;width:2px;height:2px;border-radius:50%;background:#fff;opacity:.8}}
.surf{{position:absolute;left:0;top:calc(15% - 14px);width:200%;display:flex;animation:drift 30s linear infinite;height:30px}}
.surf svg{{width:50%;height:100%;display:block}}
@keyframes drift{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}
.ray{{position:absolute;top:15%;width:150px;height:78%;background:linear-gradient(rgba(190,235,255,.30),transparent 80%);
  transform-origin:top center;filter:blur(8px);animation:sway 9s ease-in-out infinite alternate}}
@keyframes sway{{from{{opacity:.25;transform:rotate(var(--r)) scaleX(.8)}}to{{opacity:.7;transform:rotate(calc(var(--r) + 5deg)) scaleX(1.25)}}}}
.vig{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 38%,transparent 30%,rgba(0,0,0,.72) 100%)}}
.wreck{{position:absolute;width:min(58vw,620px);right:-4%;top:21%;transform-origin:20% 90%;opacity:.88;animation:sink 26s ease-in-out infinite alternate}}
@keyframes sink{{from{{transform:rotate(27deg) translateY(0)}}to{{transform:rotate(36deg) translateY(30px)}}}}
.fish{{position:absolute;left:0;fill:#0a2b44;opacity:.9;will-change:transform}}
.fish svg{{display:block}}
.bub{{position:absolute;bottom:-20px;border-radius:50%;border:1px solid rgba(190,235,255,.45);background:rgba(190,235,255,.08);animation:rise linear infinite}}
@keyframes rise{{from{{transform:translateY(0) translateX(0);opacity:0}}10%{{opacity:.9}}to{{transform:translateY(-110vh) translateX(14px);opacity:0}}}}
.ppl{{position:absolute;top:14%;fill:#040a14;stroke:rgba(140,200,230,.38);stroke-width:1.1;animation:fall linear infinite;will-change:transform}}
@keyframes fall{{0%{{transform:translate(0,0) rotate(var(--t));opacity:0}}8%{{opacity:.85}}50%{{transform:translate(var(--dx),48vh) rotate(calc(var(--t) + 14deg))}}88%{{opacity:.35}}100%{{transform:translate(calc(var(--dx)*-.6),95vh) rotate(calc(var(--t) - 10deg));opacity:0}}}}
.lb{{position:absolute;top:calc(15% - 22px);left:12%;width:86px;opacity:.9;animation:bobb 5s ease-in-out infinite}}
@keyframes bobb{{0%,100%{{transform:translateY(0) rotate(-3deg)}}50%{{transform:translateY(4px) rotate(3deg)}}}}
.hud{{position:absolute;left:0;right:0;bottom:0;padding:70px 20px 34px;text-align:center;background:linear-gradient(transparent,rgba(0,3,8,.92) 60%)}}
.hud .t1{{font-size:13px;letter-spacing:.5em;color:#8fb6d4}}
.hud h1{{margin:.2em 0;font-family:'Cinzel',serif;font-weight:900;font-size:clamp(30px,5.6vw,66px);letter-spacing:.1em;color:#e7f1fb;text-shadow:0 4px 30px #000}}
.hud p{{margin:0 auto;max-width:720px;font-style:italic;font-size:clamp(14px,1.5vw,19px);color:#b9d0e6}}
</style></head><body>{FISH_DEF}<div class="scene" id="sc">
<div class="air" id="air"></div><div class="water"></div>
<div id="rays"></div>
<div class="surf"><svg viewBox="0 0 {w} 400" preserveAspectRatio="none"><path d="{surf}" fill="#1c5d86"/></svg><svg viewBox="0 0 {w} 400" preserveAspectRatio="none"><path d="{surf}" fill="#1c5d86"/></svg></div>
<svg class="lb" viewBox="0 0 120 50"><path d="M4,22 Q60,46 116,22 L108,34 Q60,50 12,34Z" fill="#02060d"/><circle cx="40" cy="14" r="5" fill="#02060d"/><circle cx="58" cy="12" r="5" fill="#02060d"/><circle cx="76" cy="14" r="5" fill="#02060d"/></svg>
<div class="wreck">{ship}</div>
<div id="fishes"></div><div id="people"></div><div id="bubs"></div>
<div class="vig"></div>
<div class="hud"><div class="t1 title">Atlantic Ocean · 2.4 km below</div><h1>{title}</h1><p>{subtitle}</p></div>
</div>
<script>
const $=id=>document.getElementById(id), R=(a,b)=>a+Math.random()*(b-a);
for(let i=0;i<70;i++){{const s=document.createElement('i');s.className='star';s.style.left=R(0,100)+'%';s.style.top=R(0,90)+'%';s.style.opacity=R(.2,1);$('air').appendChild(s);}}
for(let i=0;i<7;i++){{const r=document.createElement('div');r.className='ray';r.style.left=(i*15-4)+'%';r.style.setProperty('--r',(R(-14,14))+'deg');r.style.animationDelay=(-R(0,9))+'s';r.style.width=R(70,200)+'px';$('rays').appendChild(r);}}
for(let i=0;i<46;i++){{const b=document.createElement('i');b.className='bub';const s=R(3,13);b.style.width=b.style.height=s+'px';b.style.left=R(0,100)+'%';b.style.animationDuration=R(7,18)+'s';b.style.animationDelay=(-R(0,18))+'s';$('bubs').appendChild(b);}}
const tints=['#0a2b44','#12425f','#1b5a74','#0b3a52','#285f78'];
for(let i=0;i<16;i++){{const f=document.createElement('div');f.className='fish';const s=R(26,78),dir=Math.random()<.5?1:-1;
 f.style.top=R(22,86)+'%';f.style.fill=tints[i%tints.length];
 f.innerHTML='<svg width="'+s+'" height="'+s/2+'" style="transform:scaleX('+(-dir)+')"><use href="#fish"/></svg>';
 $('fishes').appendChild(f);
 const dur=R(16,46)*1000,delay=-R(0,dur),wob=R(6,22),W=()=>innerWidth;
 f.animate([{{transform:'translate('+(dir>0?-120:W()+120)+'px,0)'}},{{transform:'translate('+(dir>0?W()+120:-120)+'px,'+wob+'px)'}}],{{duration:dur,delay:delay,iterations:Infinity}});}}
// school of small fish
for(let g=0;g<2;g++){{const cy=R(35,70),dir=g?1:-1,dur=R(26,34)*1000;
 for(let i=0;i<11;i++){{const f=document.createElement('div');f.className='fish';const s=R(14,22);
  f.style.top=(cy+R(-4,4))+'%';f.style.fill='#1d6d8c';
  f.innerHTML='<svg width="'+s+'" height="'+s/2+'" style="transform:scaleX('+(-dir)+')"><use href="#fish"/></svg>';$('fishes').appendChild(f);
  const off=R(0,160),W=innerWidth;
  f.animate([{{transform:'translate('+(dir>0?-200-off:W+off)+'px,0)'}},{{transform:'translate('+(dir>0?W+off:-200-off)+'px,'+R(-10,10)+'px)'}}],{{duration:dur,delay:-dur*0.35,iterations:Infinity}});}}}}
for(let i=0;i<9;i++){{const p=document.createElementNS('http://www.w3.org/2000/svg','svg');p.setAttribute('viewBox','0 0 60 120');p.setAttribute('class','ppl');
 const h=R(52,92);p.setAttribute('width',h*.5);p.setAttribute('height',h);p.style.left=R(4,92)+'%';
 p.style.setProperty('--t',R(-70,70)+'deg');p.style.setProperty('--dx',R(-70,70)+'px');
 p.style.animationDuration=R(34,62)+'s';p.style.animationDelay=(-R(0,60))+'s';p.innerHTML='<use href="#person"/>';$('people').appendChild(p);}}
</script></body></html>"""


# ----------------------------------------------- passenger field (canvas)
def depths_scene(passengers: list[list], height: int = 700) -> str:
    """passengers: [name, survived(0/1), pclass, sex('m'/'f'), age|None]"""
    data = json.dumps(passengers).replace("</", "<\\/")
    return """<!doctype html><html><head>""" + HEAD + """<style>
#c{display:block;width:100%;height:100vh}
#tip{position:absolute;pointer-events:none;padding:8px 12px;border-radius:8px;background:rgba(3,10,22,.92);border:1px solid #d9b66b;font-size:13px;line-height:1.35;display:none;max-width:260px;z-index:5}
#tip b{font-family:'Cinzel',serif;letter-spacing:.06em;color:#f2d79b}
#hud{position:absolute;left:16px;top:14px;font-size:13px;letter-spacing:.18em;text-transform:uppercase;color:#cfe0f5;text-shadow:0 2px 8px #000}
#hud span{color:#ffd27a;font-weight:500}
.lbl{position:absolute;right:16px;font-size:11px;letter-spacing:.3em;text-transform:uppercase;color:rgba(190,215,240,.55)}
</style></head><body><div class="scene"><canvas id="c"></canvas><div id="tip"></div>
<div id="hud"></div><div class="lbl" style="top:14px">Lifeboats &amp; rescue</div><div class="lbl" style="bottom:12px">The deep</div></div>
<script>
const DATA=""" + data + """;
const cv=document.getElementById('c'),ctx=cv.getContext('2d'),tip=document.getElementById('tip');
let W,H,DPR=Math.min(window.devicePixelRatio||1,2);
function mul(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
const rnd=mul(1912);
const CL={1:'#f0d28a',2:'#9cc8f2',3:'#7fc4b4'};
let P=[],boats=[],fish=[],bub=[],stars=[],t0=performance.now();
const ease=x=>1-Math.pow(1-x,3);
function layout(){
  W=cv.clientWidth;H=cv.clientHeight;cv.width=W*DPR;cv.height=H*DPR;ctx.setTransform(DPR,0,0,DPR,0,0);
  const surfY=H*0.17;
  const surv=DATA.filter(d=>d[1]==1),lost=DATA.filter(d=>d[1]==0);
  const nb=Math.max(1,Math.ceil(surv.length/36));boats=[];
  for(let i=0;i<nb;i++)boats.push({x:(i+.5)/nb*W*0.94+W*0.03,y:surfY-4+(i%2)*3,ph:rnd()*6});
  P=[];
  surv.forEach((d,i)=>{const b=boats[i%nb],k=Math.floor(i/nb),n=Math.ceil(surv.length/nb);
    const cap=Math.min(k,35);
    P.push({d,tx:b.x+(cap-17.5)*3.2,ty:b.y-9,boat:b,s:1,seed:rnd()*100});});
  lost.forEach(d=>{const depth=Math.pow(rnd(),0.8);
    P.push({d,tx:W*(0.03+rnd()*0.94),ty:surfY+30+depth*(H*0.80-surfY-40),s:1,seed:rnd()*100,depth});});
  P.forEach(p=>{p.sx=W*0.5+(rnd()-.5)*W*0.16;p.sy=surfY+6;p.delay=rnd()*1.1;p.x=p.sx;p.y=p.sy});
  fish=[];for(let i=0;i<14;i++)fish.push({y:H*(0.3+rnd()*0.58),x:rnd()*W,v:(0.15+rnd()*0.45)*(rnd()<.5?-1:1),s:14+rnd()*30});
  bub=[];for(let i=0;i<40;i++)bub.push({x:rnd()*W,y:rnd()*H,r:1+rnd()*3,v:.15+rnd()*.5});
  stars=[];for(let i=0;i<60;i++)stars.push({x:rnd()*W,y:rnd()*surfY*0.9,a:rnd()});
  const r=P.filter(p=>p.d[1]==1).length;
  document.getElementById('hud').innerHTML='Rescued <span>'+r+'</span> &nbsp;·&nbsp; Lost <span>'+(P.length-r)+'</span>';
}
function person(x,y,col,sc,lost,ph){
  ctx.fillStyle=col;ctx.beginPath();ctx.arc(x,y,2.6*sc,0,7);ctx.fill();
  ctx.strokeStyle=col;ctx.lineWidth=1.5*sc;ctx.lineCap='round';ctx.beginPath();
  if(lost){const a=Math.sin(ph)*.5;
    ctx.moveTo(x,y+2.6*sc);ctx.lineTo(x+a*2,y+10*sc);
    ctx.moveTo(x-5*sc,y+1*sc+Math.sin(ph*1.3)*2);ctx.lineTo(x,y+4*sc);ctx.lineTo(x+5*sc,y+1*sc-Math.sin(ph*1.3)*2);
    ctx.moveTo(x+a*2,y+10*sc);ctx.lineTo(x-3*sc+a*3,y+16*sc);ctx.moveTo(x+a*2,y+10*sc);ctx.lineTo(x+3*sc-a*3,y+15*sc);}
  else{ctx.moveTo(x,y+2.6*sc);ctx.lineTo(x,y+8*sc);}
  ctx.stroke();
}
function frame(now){
  const t=(now-t0)/1000;ctx.clearRect(0,0,W,H);
  const surfY=H*0.17;
  let g=ctx.createLinearGradient(0,0,0,surfY);g.addColorStop(0,'#01040b');g.addColorStop(1,'#0c2342');ctx.fillStyle=g;ctx.fillRect(0,0,W,surfY);
  stars.forEach(s=>{ctx.globalAlpha=.3+.7*Math.abs(Math.sin(t*.8+s.a*9));ctx.fillStyle='#fff';ctx.fillRect(s.x,s.y,1.4,1.4)});ctx.globalAlpha=1;
  g=ctx.createLinearGradient(0,surfY,0,H);g.addColorStop(0,'#1d5f88');g.addColorStop(.25,'#0d3556');g.addColorStop(.6,'#051627');g.addColorStop(1,'#010509');
  ctx.fillStyle=g;ctx.fillRect(0,surfY,W,H-surfY);
  for(let i=0;i<6;i++){const x=W*(i/5.5)+Math.sin(t*.3+i)*30;const rg=ctx.createLinearGradient(0,surfY,0,H*.8);
    rg.addColorStop(0,'rgba(190,235,255,.16)');rg.addColorStop(1,'rgba(190,235,255,0)');ctx.fillStyle=rg;
    ctx.beginPath();ctx.moveTo(x-10,surfY);ctx.lineTo(x+40,surfY);ctx.lineTo(x+170+Math.sin(t*.4+i)*40,H*.8);ctx.lineTo(x-90,H*.8);ctx.fill();}
  // seabed + wreck halves
  ctx.fillStyle='#02070d';ctx.beginPath();ctx.moveTo(0,H);ctx.lineTo(0,H*.93);
  for(let x=0;x<=W;x+=40)ctx.lineTo(x,H*.935+Math.sin(x*.012)*6);ctx.lineTo(W,H);ctx.fill();
  ctx.fillStyle='#071423';ctx.save();ctx.translate(W*.16,H*.92);ctx.rotate(-.18);ctx.fillRect(0,-26,170,26);ctx.fillRect(34,-46,18,20);ctx.fillRect(74,-46,18,20);ctx.restore();
  ctx.save();ctx.translate(W*.72,H*.95);ctx.rotate(.14);ctx.fillRect(0,-30,210,30);ctx.beginPath();ctx.moveTo(210,-30);ctx.lineTo(250,-8);ctx.lineTo(210,0);ctx.fill();ctx.restore();
  // fish & bubbles
  fish.forEach(f=>{f.x+=f.v;if(f.x>W+60)f.x=-60;if(f.x<-60)f.x=W+60;ctx.fillStyle='rgba(8,52,78,.8)';
    ctx.save();ctx.translate(f.x,f.y+Math.sin(t+f.s)*4);ctx.scale(f.v>0?-1:1,1);
    ctx.beginPath();ctx.ellipse(0,0,f.s*.5,f.s*.22,0,0,7);ctx.fill();ctx.beginPath();ctx.moveTo(f.s*.45,0);ctx.lineTo(f.s*.75,-f.s*.2);ctx.lineTo(f.s*.75,f.s*.2);ctx.fill();ctx.restore();});
  ctx.strokeStyle='rgba(190,235,255,.4)';ctx.lineWidth=1;bub.forEach(b=>{b.y-=b.v;if(b.y<surfY)b.y=H;ctx.beginPath();ctx.arc(b.x+Math.sin(t+b.y*.02)*4,b.y,b.r,0,7);ctx.stroke()});
  // surface wave
  ctx.fillStyle='#1d5f88';ctx.beginPath();ctx.moveTo(0,surfY+6);for(let x=0;x<=W;x+=12)ctx.lineTo(x,surfY+Math.sin(x*.03+t*1.4)*3);ctx.lineTo(W,surfY+8);ctx.fill();
  // lifeboats
  boats.forEach(b=>{const y=b.y+Math.sin(t*1.2+b.ph)*2,r=Math.sin(t*1.2+b.ph)*.05;
    ctx.save();ctx.translate(b.x,y);ctx.rotate(r);ctx.fillStyle='#050a12';ctx.strokeStyle='#c99a5a';ctx.lineWidth=1.3;
    ctx.beginPath();ctx.moveTo(-60,-4);ctx.quadraticCurveTo(0,20,60,-4);ctx.lineTo(52,6);ctx.quadraticCurveTo(0,26,-52,6);ctx.closePath();ctx.fill();ctx.stroke();ctx.restore();});
  // people
  let hover=null;
  P.forEach(p=>{const k=Math.min(1,Math.max(0,(t-p.delay)/(p.d[1]==1?3.2:4.8)));const e=ease(k);
    let x=p.sx+(p.tx-p.sx)*e,y=p.sy+(p.ty-p.sy)*e;
    if(p.d[1]==1){const bb=p.boat;y=(k<1?y:bb.y+Math.sin(t*1.2+bb.ph)*2-9);}
    else{x+=Math.sin(t*.6+p.seed)*7*e;y+=Math.sin(t*.45+p.seed*2)*5*e+ (k>=1?Math.sin(t*.1+p.seed)*4:0);}
    p.x=x;p.y=y;
    const dep=p.d[1]==1?0:Math.min(1,(y-surfY)/(H*.8));
    ctx.globalAlpha=p.d[1]==1?1:0.95-0.6*dep;
    const col=CL[p.d[2]]||'#fff';
    if(p.d[1]==1){ctx.shadowColor=col;ctx.shadowBlur=6;}
    person(x,y,p.d[1]==1?col:shade(col,1-dep*.7),1,p.d[1]==0,t+p.seed);
    ctx.shadowBlur=0;ctx.globalAlpha=1;
  });
  requestAnimationFrame(frame);
}
function shade(hex,f){const n=parseInt(hex.slice(1),16);return 'rgb('+((n>>16)*f|0)+','+(((n>>8)&255)*f|0)+','+((n&255)*f|0)+')'}
cv.addEventListener('mousemove',e=>{const r=cv.getBoundingClientRect(),mx=e.clientX-r.left,my=e.clientY-r.top;
  let best=null,bd=14;P.forEach(p=>{const d=Math.hypot(p.x-mx,p.y+4-my);if(d<bd){bd=d;best=p}});
  if(best){const d=best.d,cls={1:'First',2:'Second',3:'Third'}[d[2]];
    tip.innerHTML='<b>'+d[0]+'</b><br>'+cls+' class · '+(d[3]=='f'?'Female':'Male')+(d[4]!=null?' · age '+d[4]:'')+'<br>'+(d[1]==1?'<span style="color:#ffd27a">Reached a lifeboat</span>':'<span style="color:#8fb6d4">Lost to the Atlantic</span>');
    tip.style.display='block';tip.style.left=Math.min(mx+14,W-270)+'px';tip.style.top=Math.max(8,my-8)+'px';cv.style.cursor='pointer'}
  else{tip.style.display='none';cv.style.cursor='default'}});
cv.addEventListener('mouseleave',()=>tip.style.display='none');
window.addEventListener('resize',()=>{layout();t0=performance.now()});
layout();requestAnimationFrame(frame);
</script></body></html>"""
