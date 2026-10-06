import pandas as pd
import streamlit as st

from titanic_kit.model import load_metrics
from titanic_kit.theme import card, footer, heading

m = load_metrics()
heading("Under the hood", "The engine room",
        "The final model is a Random Forest - the best performer in the notebook's comparison of five tuned algorithms. "
        "Here is how it stacks up and what it pays attention to.")

c = st.columns(5)
c[0].metric("Accuracy", f"{m['accuracy']*100:.1f}%")
c[1].metric("Precision", f"{m['precision']*100:.1f}%")
c[2].metric("Recall", f"{m['recall']*100:.1f}%")
c[3].metric("F1 score", f"{m['f1']*100:.1f}%")
c[4].metric("ROC-AUC", f"{m['roc_auc']:.3f}")
st.caption(f"Held-out test set: {m['n_test']} passengers · 5-fold cross-validation accuracy "
           f"{m['cv_mean']*100:.1f}% ± {m['cv_std']*100:.1f}%")

t1, t2, t3, t4 = st.tabs(["Model comparison", "What matters most", "Confusion matrix", "ROC curve"])

with t1:
    st.markdown("**Tuned models from the notebook** (RandomizedSearchCV, SMOTE-balanced training data):")
    comp = pd.DataFrame({
        "Model": ["Random Forest", "Logistic Regression", "Decision Tree", "XGBoost", "KNN"],
        "Accuracy": [0.7933, 0.7877, 0.7765, 0.7709, 0.7542],
        "Precision": [0.7581, 0.7183, 0.7544, 0.7188, 0.6582],
        "Recall": [0.6812, 0.7391, 0.6232, 0.6667, 0.7536],
        "F1 Score": [0.7176, 0.7286, 0.6825, 0.6917, 0.7027],
        "ROC-AUC": [0.8427, 0.8386, 0.7735, 0.8315, 0.8250],
    })
    st.dataframe(comp, hide_index=True, width="stretch")
    st.bar_chart(comp.set_index("Model")["Accuracy"], color="#d9b66b")
    st.markdown(card("Why Random Forest?",
        "It leads on test accuracy and precision, and has the best cross-validated accuracy (83.4%) and lowest variance "
        "among the tree-based models. In this app the forest is re-trained on human-readable passenger details "
        "(class, sex, age, fare, family size, cabin, port, title) so it can be used from a simple web form."),
        unsafe_allow_html=True)

with t2:
    imp = pd.Series(m["importance"]).sort_values(ascending=False).mul(100).rename("Importance %")
    st.bar_chart(imp, color="#7fb6e0", horizontal=True)
    st.caption("Title (Mr / Mrs / Miss / Master), fare, age and sex dominate - echoing 'women and children first'.")

with t3:
    (tn, fp), (fn, tp) = m["confusion"]
    st.markdown(f"""
<div style="display:grid;grid-template-columns:130px 1fr 1fr;gap:6px;max-width:560px;text-align:center">
<div></div><div class="k" style="color:#9fb8d6">Predicted: lost</div><div class="k" style="color:#9fb8d6">Predicted: survived</div>
<div style="align-self:center;color:#9fb8d6">Actually lost</div>
<div class="card stat"><div class="n">{tn}</div><div class="l">Correct</div></div>
<div class="card stat" style="border-color:#b4423a88"><div class="n">{fp}</div><div class="l">False alarm</div></div>
<div style="align-self:center;color:#9fb8d6">Actually survived</div>
<div class="card stat" style="border-color:#b4423a88"><div class="n">{fn}</div><div class="l">Missed</div></div>
<div class="card stat"><div class="n">{tp}</div><div class="l">Correct</div></div></div>""",
                unsafe_allow_html=True)

with t4:
    roc = pd.DataFrame({"False positive rate": m["roc"]["fpr"], "True positive rate": m["roc"]["tpr"]})
    st.line_chart(roc, x="False positive rate", y="True positive rate", color="#d9b66b")
    st.caption(f"Area under the curve = {m['roc_auc']:.3f} (1.0 is perfect, 0.5 is a coin flip).")
footer()
