import streamlit as st

from titanic_kit import scenes
from titanic_kit.model import load_raw
from titanic_kit.theme import footer, heading

df = load_raw()
heading("The night sea", "891 people, one ocean",
        "Every figure is a real passenger from the dataset. Those who reached a lifeboat float up to the "
        "surface; those who did not sink slowly into the dark. Gold = First class, blue = Second, green = Third. "
        "Hover over anyone to see who they were.")

c1, c2, c3 = st.columns([1.2, 1, 1])
cls = c1.multiselect("Class", [1, 2, 3], default=[1, 2, 3], format_func=lambda x: {1: "1st", 2: "2nd", 3: "3rd"}[x])
sex = c2.multiselect("Sex", ["female", "male"], default=["female", "male"])
who = c3.radio("Show", ["Everyone", "Survivors", "Lost"], horizontal=True)

d = df[df.Pclass.isin(cls) & df.Sex.isin(sex)]
if who == "Survivors":
    d = d[d.Survived == 1]
elif who == "Lost":
    d = d[d.Survived == 0]

rows = [[r.Name, int(r.Survived), int(r.Pclass), r.Sex[0], None if r.Age != r.Age else int(r.Age)]
        for r in d.itertuples()]
if rows:
    scenes.render(scenes.depths_scene(rows), height=700)
else:
    st.info("No passengers match these filters.")
footer()
