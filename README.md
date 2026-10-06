# 🚢 R.M.S. Titanic – Survival Predictor

A multipage Streamlit app wrapped around a Random Forest trained on the Titanic dataset.
Enter a passenger's details, get a boarding pass and watch an animated ocean scene – a dawn
lifeboat if you survive, the dark deep (fish, bubbles, the wreck, drifting figures) if you don't.

## Pages
| Page | What it does |
|------|--------------|
| 🚢 The Voyage | Animated night-sea hero, key statistics, timeline of the sinking |
| 🎫 Boarding Pass | Prediction form → ticket + survival probability + animated verdict scene |
| 🌊 The Night Sea | All 891 passengers as figures rising to lifeboats or sinking (hover for names) |
| 📜 Passenger Manifest | Filterable data explorer with charts |
| ⚙️ Engine Room | Model comparison, feature importance, confusion matrix, ROC curve |

## Run locally (VS Code terminal / cmd)
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows   (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```
Opens at http://localhost:8501

## Push to GitHub
```bash
git init
git add .
git commit -m "Titanic survival predictor"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

## Deploy on Streamlit Community Cloud
1. Go to https://share.streamlit.io and sign in with GitHub.
2. **Create app** → pick your repository, branch `main`, main file path **`app.py`**.
3. Click **Deploy**. First build takes a few minutes.

If the saved model was built with a different scikit-learn version than the server's, the app
re-trains itself automatically from `data/Titanic-Dataset.csv` (takes a few seconds).
You can also re-train manually any time: `python train_model.py`.

## Project structure
```
app.py                 entry point + navigation
titanic_kit/screens/    the five pages
titanic_kit/model.py         feature engineering, training, prediction
titanic_kit/scenes.py        animated ocean / ship / fish / figure scenes
titanic_kit/theme.py         CSS theme
model/                 saved pipeline + metrics
data/                  Titanic-Dataset.csv
notebook/GGST_9.ipynb  original notebook
```

## Note on the model
The notebook label-encodes `Name`, `Ticket`, `Cabin` and `PassengerId`, which a web form cannot
sensibly supply. The app therefore trains a Random Forest on human-readable features – class, sex,
age, fare, family size, cabin, port and title – using the same train/test split (80/20, seed 42).

## Troubleshooting on Streamlit Cloud
- Main file path must be `app.py` and `requirements.txt` must be in the repo root.
- Make sure these folders were pushed: `titanic_kit/`, `titanic_kit/`, `data/`, `model/`, `.streamlit/`.
- If a build ever fails on dependencies, open **Manage app → Settings → Python version** and pick **3.12**, then reboot.
- A red "Data problem" box means `data/Titanic-Dataset.csv` is not the original 891-row training file.
