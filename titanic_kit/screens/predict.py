import html
import zlib

import streamlit as st

from titanic_kit import scenes
from titanic_kit.model import engineer, load_model, load_raw, predict
from titanic_kit.theme import footer, heading

model = load_model()
raw = load_raw()
fare_med = raw.groupby("Pclass")["Fare"].median().round(1).to_dict()

heading("Step aboard", "Your boarding pass",
        "Fill in who you would have been in 1912. The Random Forest weighs class, age, sex, fare, family and "
        "cabin - then decides whether you reach a lifeboat.")

with st.form("pass"):
    a, b, c = st.columns([1.3, 1, 1])
    name = a.text_input("Passenger name", "Mr. Jack Dawson")
    sex = b.selectbox("Sex", ["male", "female"])
    age = c.slider("Age", 1, 80, 28)

    d, e, f = st.columns(3)
    pclass = d.selectbox("Ticket class", [1, 2, 3], index=2,
                         format_func=lambda x: {1: "1st - Promenade suites", 2: "2nd - Cabins", 3: "3rd - Steerage"}[x])
    embarked = e.selectbox("Port of embarkation", ["S", "C", "Q"],
                           format_func=lambda x: {"S": "Southampton", "C": "Cherbourg", "Q": "Queenstown"}[x])
    fare = f.number_input("Fare paid (£)", 0.0, 520.0, float(fare_med.get(3, 8.0)), step=1.0,
                          help="Median fares: 1st ≈ £60, 2nd ≈ £14, 3rd ≈ £8")

    g, h, i = st.columns(3)
    sibsp = g.number_input("Siblings / spouse aboard", 0, 8, 0)
    parch = h.number_input("Parents / children aboard", 0, 6, 0)
    married = i.checkbox("Married woman (Mrs.)", value=False, disabled=(sex == "male"))
    cabin = i.checkbox("Private cabin booked", value=False)

    go = st.form_submit_button("Issue my ticket")

if go:
    title = ("Master" if age < 13 else "Mr") if sex == "male" else ("Mrs" if married else "Miss")
    prob = predict(model, pclass=pclass, sex=sex, age=age, sibsp=sibsp, parch=parch,
                   fare=fare, embarked=embarked, title=title, has_cabin=cabin)
    lived = prob >= 0.5
    port = {"S": "Southampton", "C": "Cherbourg", "Q": "Queenstown"}[embarked]
    cls_name = {1: "First", 2: "Second", 3: "Third"}[pclass]
    safe = html.escape(name.strip() or "Unnamed passenger")
    ticket_no = zlib.crc32(f"{safe}{age}{pclass}{fare}".encode()) % 900000 + 100000

    st.markdown(f"""
<div class="pass"><div class="main">
  <div class="brand">WHITE STAR LINE · R.M.S. TITANIC</div>
  <div class="nm">{safe}</div>
  <div class="grid">
    <div><div class="k">Class</div><div class="v">{cls_name}</div></div>
    <div><div class="k">From</div><div class="v">{port}</div></div>
    <div><div class="k">Age / Sex</div><div class="v">{age} · {sex.title()}</div></div>
    <div><div class="k">Fare</div><div class="v">£{fare:,.2f}</div></div>
  </div><div class="bar"></div></div>
  <div class="stub"><div class="k">Survival odds</div><div class="big">{prob*100:.0f}%</div>
  <div class="k" style="margin-top:.6rem">Ticket</div><div class="v">#{ticket_no}</div></div>
</div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if lived:
        scenes.render(scenes.survived_scene(
            "Lifeboat secured",
            f"The model gives you a {prob*100:.0f}% chance - enough to find a seat in a boat and watch the dawn."),
            height=540)
    else:
        scenes.render(scenes.lost_scene(
            "Lost to the deep",
            f"Only a {prob*100:.0f}% chance of survival. The Atlantic takes you on the coldest night of 1912."),
            height=600)

    color = "linear-gradient(90deg,#c99a3a,#ffe29a)" if lived else "linear-gradient(90deg,#1b4f7a,#7fb6e0)"
    st.markdown(f"""<br><div class="kicker" style="margin-top:0">Probability of survival</div>
<div class="meter"><div style="width:{prob*100:.0f}%;background:{color}"></div></div>
<p class="verdict-note">{prob*100:.1f}% survive · {100-prob*100:.1f}% perish &nbsp;|&nbsp; verdict: <b>{'SURVIVED' if lived else 'DID NOT SURVIVE'}</b></p>""",
                unsafe_allow_html=True)

    d = engineer(raw)
    sim = d[(d.Sex == (1 if sex == "female" else 0)) & (d.Pclass == pclass)]
    cols = st.columns(3)
    cols[0].metric("Real passengers like you", f"{len(sim)}", f"{sex}, {cls_name} class")
    cols[1].metric("Of them, survived", f"{sim['Survived'].mean()*100:.0f}%")
    cols[2].metric("Whole ship survived", f"{raw['Survived'].mean()*100:.0f}%")
    st.caption("The model estimates odds from patterns in 891 recorded passengers; it is a statistical "
               "illustration of history, not a judgement of any individual.")
footer()
