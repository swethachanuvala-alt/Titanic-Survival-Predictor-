import pandas as pd
import streamlit as st

from titanic_kit.model import load_raw
from titanic_kit.theme import footer, heading

df = load_raw()
heading("The ship's records", "Passenger manifest",
        "Filter the passenger list and see who lived - the data tells a stark story about class, gender and age.")

c1, c2, c3, c4 = st.columns(4)
cls = c1.multiselect("Class", [1, 2, 3], default=[1, 2, 3])
sex = c2.multiselect("Sex", ["female", "male"], default=["female", "male"])
port = c3.multiselect("Embarked", ["S", "C", "Q"], default=["S", "C", "Q"])
ages = c4.slider("Age range", 0, 80, (0, 80))

d = df[df.Pclass.isin(cls) & df.Sex.isin(sex) & (df.Embarked.isin(port) | df.Embarked.isna())
       & (df.Age.between(*ages) | df.Age.isna())]

m = st.columns(4)
m[0].metric("Passengers", len(d))
m[1].metric("Survived", int(d.Survived.sum()))
m[2].metric("Lost", int((1 - d.Survived).sum()))
m[3].metric("Survival rate", f"{d.Survived.mean()*100:.1f}%" if len(d) else "–")

t1, t2, t3, t4 = st.tabs(["By class", "By sex", "By age", "Passenger list"])
with t1:
    g = d.groupby("Pclass")["Survived"].mean().mul(100).rename("Survival %")
    g.index = g.index.map({1: "1st class", 2: "2nd class", 3: "3rd class"})
    st.bar_chart(g, color="#d9b66b")
with t2:
    st.bar_chart(d.groupby("Sex")["Survived"].mean().mul(100).rename("Survival %"), color="#7fb6e0")
with t3:
    bins = pd.cut(d["Age"], [0, 12, 18, 30, 45, 60, 100],
                  labels=["0-12", "13-18", "19-30", "31-45", "46-60", "60+"])
    st.bar_chart(d.groupby(bins, observed=True)["Survived"].mean().mul(100).rename("Survival %"), color="#7fc4b4")
with t4:
    show = d[["PassengerId", "Name", "Sex", "Age", "Pclass", "Fare", "Embarked", "Survived"]].copy()
    show["Survived"] = show["Survived"].map({1: "✅ Survived", 0: "💀 Lost"})
    st.dataframe(show, width="stretch", hide_index=True, height=420)
footer()
