"""Model utilities: feature engineering, training, loading and prediction.

The saved model is a single scikit-learn Pipeline (preprocessing + Random Forest),
so the web app only needs the passenger's *human-readable* details (class, sex,
age, fare ...) - not the label-encoded Name / Ticket / PassengerId columns that
cannot be filled in sensibly on a web form.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score,
                             roc_curve)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "Titanic-Dataset.csv"
MODEL_PATH = ROOT / "model" / "titanic_rf_pipeline.joblib"
METRICS_PATH = ROOT / "model" / "metrics.json"

NUMERIC = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare",
           "FamilySize", "IsAlone", "HasCabin"]
CATEGORICAL = ["Embarked", "Title"]
FEATURES = NUMERIC + CATEGORICAL

TITLE_MAP = {"Mlle": "Miss", "Ms": "Miss", "Mme": "Mrs"}
COMMON_TITLES = {"Mr", "Mrs", "Miss", "Master"}


REQUIRED = ["Survived", "Pclass", "Name", "Sex", "Age", "SibSp", "Parch", "Fare", "Embarked"]


class DataError(Exception):
    """Raised when the dataset file is missing, unreadable or has the wrong columns."""


def load_raw() -> pd.DataFrame:
    """Read the Titanic CSV defensively (BOM, odd delimiters, header casing/spaces)."""
    if not DATA_PATH.exists():
        raise DataError(f"Dataset not found at data/{DATA_PATH.name}. Make sure the data folder was pushed to GitHub.")
    head = DATA_PATH.read_text(encoding="utf-8-sig", errors="replace")[:200]
    if head.startswith("version https://git-lfs"):
        raise DataError("data/Titanic-Dataset.csv is a Git-LFS pointer, not the real file. Re-add it without LFS.")
    try:
        df = pd.read_csv(DATA_PATH, sep=None, engine="python", encoding="utf-8-sig")
    except Exception as exc:  # malformed / wrong file
        raise DataError(f"Could not parse data/{DATA_PATH.name}: {exc}") from exc
    df.columns = [str(c).strip().strip('"').strip("'") for c in df.columns]
    lower = {c.lower().replace(" ", "").replace("_", ""): c for c in df.columns}
    canon = {"passengerid": "PassengerId", "survived": "Survived", "pclass": "Pclass", "name": "Name",
             "sex": "Sex", "age": "Age", "sibsp": "SibSp", "parch": "Parch", "ticket": "Ticket",
             "fare": "Fare", "cabin": "Cabin", "embarked": "Embarked"}
    df = df.rename(columns={lower[k]: v for k, v in canon.items() if k in lower})
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise DataError(f"data/{DATA_PATH.name} is missing column(s) {missing}. Columns found: {list(df.columns)}. "
                        "Use the original training file (Titanic-Dataset.csv, 891 rows, with a 'Survived' column).")
    for c in ("Cabin", "Ticket"):
        if c not in df.columns:
            df[c] = pd.NA
    return df


def engineer(df: pd.DataFrame) -> pd.DataFrame:
    """Turn raw Titanic columns into model-ready, human-meaningful features."""
    d = df.copy()
    if "Title" not in d.columns:
        d["Title"] = d["Name"].str.extract(r",\s*([^\.]+)\.")[0].str.strip()
    d["Title"] = d["Title"].replace(TITLE_MAP)
    d.loc[~d["Title"].isin(COMMON_TITLES), "Title"] = "Rare"
    d["Sex"] = d["Sex"].map({"male": 0, "female": 1}).fillna(d["Sex"])
    d["Embarked"] = d["Embarked"].fillna("S")
    d["FamilySize"] = d["SibSp"] + d["Parch"] + 1
    d["IsAlone"] = (d["FamilySize"] == 1).astype(int)
    if "HasCabin" not in d.columns:
        d["HasCabin"] = d["Cabin"].notna().astype(int)
    d["Age"] = d["Age"].fillna(d.groupby("Title")["Age"].transform("median"))
    d["Age"] = d["Age"].fillna(d["Age"].median())
    return d


def build_pipeline() -> Pipeline:
    pre = ColumnTransformer(
        [("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL)],
        remainder="passthrough",
    )
    # Shallow, well-regularised forest (chosen by cross-validation) so that it
    # generalises instead of memorising the 891 passengers.
    rf = RandomForestClassifier(
        n_estimators=300, max_depth=5, min_samples_split=5,
        min_samples_leaf=2, max_features="log2",
        random_state=42, n_jobs=-1,
    )
    return Pipeline([("prep", pre), ("rf", rf)])


_CACHE: dict = {}


def train_and_save() -> dict:
    """Train the Random Forest, evaluate it, keep it in memory and (if possible) save it to disk."""
    raw = load_raw()
    d = engineer(raw)
    X, y = d[FEATURES], d["Survived"]
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)

    pipe = build_pipeline().fit(X_tr, y_tr)
    pred = pipe.predict(X_te)
    prob = pipe.predict_proba(X_te)[:, 1]
    cv = cross_val_score(build_pipeline(), X, y, cv=5, scoring="accuracy")
    fpr, tpr, _ = roc_curve(y_te, prob)

    names = pipe.named_steps["prep"].get_feature_names_out()
    imp = pipe.named_steps["rf"].feature_importances_
    agg: dict[str, float] = {}
    for n, v in zip(names, imp):
        n = n.split("__", 1)[1]
        key = "Title" if n.startswith("Title_") else \
              "Embarked" if n.startswith("Embarked_") else n
        agg[key] = agg.get(key, 0.0) + float(v)

    metrics = {
        "sklearn_version": sklearn.__version__,
        "accuracy": float(accuracy_score(y_te, pred)),
        "precision": float(precision_score(y_te, pred)),
        "recall": float(recall_score(y_te, pred)),
        "f1": float(f1_score(y_te, pred)),
        "roc_auc": float(roc_auc_score(y_te, prob)),
        "cv_mean": float(cv.mean()),
        "cv_std": float(cv.std()),
        "confusion": confusion_matrix(y_te, pred).tolist(),
        "n_train": int(len(X_tr)),
        "n_test": int(len(X_te)),
        "importance": dict(sorted(agg.items(), key=lambda kv: -kv[1])),
        "roc": {"fpr": [round(float(v), 4) for v in fpr],
                "tpr": [round(float(v), 4) for v in tpr]},
    }
    _CACHE["model"], _CACHE["metrics"] = pipe, metrics
    try:  # saving is a nicety - never fail because the disk is read-only
        MODEL_PATH.parent.mkdir(exist_ok=True)
        joblib.dump(pipe, MODEL_PATH)
        METRICS_PATH.write_text(json.dumps(metrics, indent=2))
    except Exception:
        pass
    return metrics


def _ensure() -> None:
    """Fill the in-memory cache from disk, or re-train if the saved files are unusable."""
    if "model" in _CACHE and "metrics" in _CACHE:
        return
    try:
        meta = json.loads(METRICS_PATH.read_text())
        if meta.get("sklearn_version") != sklearn.__version__:
            raise RuntimeError("scikit-learn version changed")
        _CACHE["model"] = joblib.load(MODEL_PATH)
        _CACHE["metrics"] = meta
    except Exception:
        train_and_save()


def load_model():
    _ensure()
    return _CACHE["model"]


def load_metrics() -> dict:
    _ensure()
    return _CACHE["metrics"]


def passenger_frame(pclass, sex, age, sibsp, parch, fare, embarked,
                    title, has_cabin) -> pd.DataFrame:
    fam = int(sibsp) + int(parch) + 1
    row = {
        "Pclass": int(pclass), "Sex": 1 if sex == "female" else 0,
        "Age": float(age), "SibSp": int(sibsp), "Parch": int(parch),
        "Fare": float(fare), "FamilySize": fam,
        "IsAlone": int(fam == 1), "HasCabin": int(bool(has_cabin)),
        "Embarked": embarked, "Title": title,
    }
    return pd.DataFrame([row])[FEATURES]


def predict(model, **kwargs) -> float:
    """Return probability of survival (0-1)."""
    return float(model.predict_proba(passenger_frame(**kwargs))[0, 1])


if __name__ == "__main__":
    m = train_and_save()
    print(json.dumps({k: v for k, v in m.items() if k not in ("roc",)}, indent=2))
