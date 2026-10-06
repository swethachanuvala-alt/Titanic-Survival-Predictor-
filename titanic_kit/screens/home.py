import streamlit as st

from titanic_kit import registry, scenes
from titanic_kit.model import load_raw
from titanic_kit.theme import card, footer, heading, stat

df = load_raw()
rate = df["Survived"].mean() * 100
fem = df[df.Sex == "female"]["Survived"].mean() * 100
male = df[df.Sex == "male"]["Survived"].mean() * 100
first = df[df.Pclass == 1]["Survived"].mean() * 100
third = df[df.Pclass == 3]["Survived"].mean() * 100

scenes.render(scenes.hero_scene(), height=560)

heading("The data of one night", "Four in ten made it home",
        "On 15 April 1912 the 'unsinkable' liner went down in the North Atlantic. This dataset records "
        f"{len(df)} of her passengers - who they were, what they paid, where they slept - and whether they "
        "lived. A Random Forest learned the patterns. Now it will judge you.")

c = st.columns(4)
for col, (n, l) in zip(c, [(f"{rate:.0f}%", "Passengers survived"), (f"{fem:.0f}%", "Women survived"),
                           (f"{male:.0f}%", "Men survived"), (f"{first:.0f}% / {third:.0f}%", "First vs third class")]):
    col.markdown(stat(n, l), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
left, right = st.columns([1.1, 1])
with left:
    heading("14 – 15 April 1912", "The longest night")
    st.markdown("""
<div class="tl">
 <div class="it"><div class="tm">10 APRIL</div><div class="tx">Titanic departs Southampton on her maiden voyage to New York.</div></div>
 <div class="it bad"><div class="tm">11:40 PM</div><div class="tx">Lookouts spot an iceberg dead ahead. The ship cannot turn in time.</div></div>
 <div class="it"><div class="tm">12:05 AM</div><div class="tx">Crew are ordered to uncover the lifeboats. There are only enough for about half of those aboard.</div></div>
 <div class="it"><div class="tm">12:45 AM</div><div class="tx">The first lifeboat is lowered - many leave half-empty.</div></div>
 <div class="it bad"><div class="tm">2:20 AM</div><div class="tx">The stern rises, the ship breaks apart and slips beneath the surface.</div></div>
 <div class="it"><div class="tm">≈ 4:00 AM</div><div class="tx">RMS Carpathia arrives and begins to pick up survivors from the boats.</div></div>
</div>""", unsafe_allow_html=True)
with right:
    heading("Your voyage", "Three ways to explore")
    st.markdown(card("🎫 Boarding Pass", "Enter your details, get your ticket and see whether the model puts you in a lifeboat - or in the deep."), unsafe_allow_html=True)
    st.markdown("<div style='height:.7rem'></div>", unsafe_allow_html=True)
    st.markdown(card("🌊 The Night Sea", "Watch all 891 passengers in the dataset drift to the surface or the seabed. Hover to meet them."), unsafe_allow_html=True)
    st.markdown("<div style='height:.7rem'></div>", unsafe_allow_html=True)
    st.markdown(card("📜 Manifest &amp; ⚙️ Engine Room", "Dig into the passenger data and see how the Random Forest was built and how well it performs."), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
if st.button("Go to the boarding pass  →"):
    st.switch_page(registry.PAGES["predict"])
footer()
