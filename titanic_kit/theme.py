"""Global look & feel: Art-Deco White Star Line meets midnight Atlantic."""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700;900&family=Karla:ital,wght@0,400;0,500;0,700;1,400&display=swap');
:root{--gold:#d9b66b;--gold2:#f2d79b;--navy:#050d1a;--navy2:#0a1a30;--foam:#e8eef7;--mist:#9fb8d6;--blood:#b4423a}
html,body,[class*="css"],.stApp{font-family:'Karla',system-ui,sans-serif}
.stApp{background:radial-gradient(1200px 600px at 70% -10%,#12335a55,transparent),linear-gradient(#050d1a,#030813 60%,#02060f)}
header[data-testid="stHeader"]{background:rgba(3,8,19,.72);backdrop-filter:blur(10px);border-bottom:1px solid #d9b66b33}
#MainMenu,footer{visibility:hidden}
.block-container{padding-top:3.6rem;max-width:1180px}
h1,h2,h3,.cinzel{font-family:'Cinzel',Georgia,serif!important;letter-spacing:.08em;color:var(--gold2)}
h1{font-weight:900} h2,h3{font-weight:700}
p,li,label,.stMarkdown{color:var(--foam)}
a{color:var(--gold)!important}

/* section kicker */
.kicker{font-family:'Cinzel',serif;font-size:.78rem;letter-spacing:.45em;color:var(--gold);text-transform:uppercase;margin:2.2rem 0 .2rem}
.sec-title{font-family:'Cinzel',serif;font-weight:700;font-size:clamp(1.5rem,3vw,2.3rem);letter-spacing:.07em;color:#fff6dc;margin:0 0 .4rem}
.rule{height:1px;background:linear-gradient(90deg,var(--gold),transparent);margin:.2rem 0 1.2rem;width:220px}
.lead{color:#c3d3e8;font-size:1.06rem;line-height:1.7;max-width:760px}

/* glass cards */
.card{background:linear-gradient(160deg,#0d2240cc,#06101fcc);border:1px solid #d9b66b33;border-radius:14px;padding:1.2rem 1.3rem;
  box-shadow:0 10px 40px #00000066, inset 0 1px 0 #ffffff10;height:100%}
.card h4{font-family:'Cinzel',serif;color:var(--gold2);letter-spacing:.1em;margin:.1rem 0 .4rem;font-size:1rem}
.card p{color:#b9cce3;margin:0;font-size:.95rem;line-height:1.55}
.stat{text-align:center}
.stat .n{font-family:'Cinzel',serif;font-weight:900;font-size:2.5rem;color:#fff3d0;line-height:1}
.stat .l{font-size:.72rem;letter-spacing:.28em;text-transform:uppercase;color:var(--mist);margin-top:.5rem}

/* timeline */
.tl{border-left:1px solid #d9b66b66;margin:.5rem 0 0 .5rem;padding-left:1.4rem}
.tl .it{position:relative;margin-bottom:1.15rem}
.tl .it:before{content:"";position:absolute;left:-1.78rem;top:.35rem;width:11px;height:11px;border-radius:50%;background:var(--gold);box-shadow:0 0 0 4px #d9b66b22}
.tl .it.bad:before{background:var(--blood);box-shadow:0 0 0 4px #b4423a33}
.tl .tm{font-family:'Cinzel',serif;color:var(--gold);font-size:.82rem;letter-spacing:.18em}
.tl .tx{color:#d8e4f3}

/* boarding pass */
.pass{display:flex;border-radius:16px;overflow:hidden;border:1px solid #d9b66b88;box-shadow:0 18px 50px #000a;
  background:linear-gradient(120deg,#f4ead2,#e8d8ac);color:#1b1410;font-family:'Karla',sans-serif;position:relative}
.pass:before{content:"";position:absolute;inset:6px;border:1px dashed #8a6d2e66;border-radius:11px;pointer-events:none}
.pass .main{flex:1;padding:1.3rem 1.6rem}
.pass .stub{width:190px;padding:1.3rem 1rem;border-left:2px dashed #8a6d2e;text-align:center;background:#00000008}
.pass .brand{font-family:'Cinzel',serif;font-weight:900;letter-spacing:.3em;font-size:.72rem;color:#7a1f1f}
.pass .nm{font-family:'Cinzel',serif;font-weight:700;font-size:1.5rem;letter-spacing:.06em;margin:.3rem 0 .6rem;color:#1b1410}
.pass .grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.6rem}
.pass .k{font-size:.6rem;letter-spacing:.22em;text-transform:uppercase;color:#7a6a45}
.pass .v{font-weight:700;font-size:1rem}
.pass .big{font-family:'Cinzel',serif;font-weight:900;font-size:2.4rem;color:#7a1f1f;line-height:1}
.pass .bar{height:30px;margin-top:.8rem;background:repeating-linear-gradient(90deg,#1b1410 0 2px,transparent 2px 4px,#1b1410 4px 5px,transparent 5px 9px)}
@media(max-width:700px){.pass{flex-direction:column}.pass .stub{width:auto;border-left:0;border-top:2px dashed #8a6d2e}.pass .grid{grid-template-columns:repeat(2,1fr)}}

/* verdict meter */
.meter{height:16px;border-radius:99px;background:#0a1a30;border:1px solid #d9b66b44;overflow:hidden}
.meter>div{height:100%;border-radius:99px}
.verdict-note{font-size:.95rem;color:#b9cce3}

/* widgets */
.stButton>button,.stFormSubmitButton>button{background:linear-gradient(#e7c880,#b8923f);color:#1a1206;border:0;border-radius:10px;
  font-family:'Cinzel',serif;font-weight:700;letter-spacing:.14em;padding:.7rem 1.6rem;text-transform:uppercase;box-shadow:0 6px 24px #d9b66b33;transition:.2s}
.stButton>button:hover,.stFormSubmitButton>button:hover{transform:translateY(-2px);filter:brightness(1.1);color:#000}
[data-baseweb="select"]>div,.stNumberInput input,.stTextInput input{background:#08162a!important;border-color:#d9b66b44!important;color:var(--foam)!important}
.stSlider [role="slider"]{background:var(--gold)!important}
div[data-testid="stForm"]{border:1px solid #d9b66b33;border-radius:16px;background:#07142899;padding:1.3rem}
.stTabs [data-baseweb="tab"]{font-family:'Cinzel',serif;letter-spacing:.1em}
div[data-testid="stMetric"]{background:#0a1a30aa;border:1px solid #d9b66b33;border-radius:12px;padding:.8rem 1rem}
div[data-testid="stMetricValue"]{font-family:'Cinzel',serif;color:#fff3d0}
iframe{border-radius:16px;border:1px solid #d9b66b33!important;box-shadow:0 20px 60px #000a}
.foot{margin:3rem 0 1rem;text-align:center;color:#6f87a6;font-size:.78rem;letter-spacing:.2em;text-transform:uppercase}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def heading(kicker: str, title: str, lead: str = "") -> None:
    html = f'<div class="kicker">{kicker}</div><div class="sec-title">{title}</div><div class="rule"></div>'
    if lead:
        html += f'<p class="lead">{lead}</p>'
    st.markdown(html, unsafe_allow_html=True)


def card(title: str, body: str) -> str:
    return f'<div class="card"><h4>{title}</h4><p>{body}</p></div>'


def stat(number: str, label: str) -> str:
    return f'<div class="card stat"><div class="n">{number}</div><div class="l">{label}</div></div>'


def footer() -> None:
    st.markdown('<div class="foot">In memory of the passengers and crew of the R.M.S. Titanic · 1912</div>',
                unsafe_allow_html=True)
