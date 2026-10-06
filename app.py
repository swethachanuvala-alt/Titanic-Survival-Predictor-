"""R.M.S. Titanic - Survival Predictor  |  entry point (run: streamlit run app.py)"""
import runpy
import sys
from pathlib import Path

import streamlit as st

# make sure the project root is importable on any host (local, Streamlit Cloud, ...)
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(page_title="Titanic · Would you have survived?", page_icon="🚢",
                   layout="wide", initial_sidebar_state="collapsed")

from titanic_kit import registry  # noqa: E402
from titanic_kit.model import DataError, load_raw  # noqa: E402
from titanic_kit.theme import inject_css  # noqa: E402

inject_css()

# Fail with a readable message (Streamlit Cloud redacts raw exceptions) if the data file is wrong.
try:
    load_raw()
except DataError as err:
    st.error(f"⚠️ Data problem: {err}")
    st.stop()

SCREENS = ROOT / "titanic_kit" / "screens"


def _make_page(name: str):
    """Build a page callable that runs titanic_kit/screens/<name>.py"""
    def _page():
        script = SCREENS / f"{name}.py"
        if not script.exists():
            st.error(f"Missing file: titanic_kit/screens/{name}.py. "
                     f"Folders found next to app.py: {sorted(p.name for p in ROOT.iterdir())}")
            return
        runpy.run_path(str(script), run_name="__main__")
    _page.__name__ = f"screen_{name}"
    return _page


SPECS = [  # key, title, icon, url
    ("home", "The Voyage", "🚢", None),
    ("predict", "Boarding Pass", "🎫", "boarding-pass"),
    ("depths", "The Night Sea", "🌊", "night-sea"),
    ("manifest", "Passenger Manifest", "📜", "manifest"),
    ("model_lab", "Engine Room", "⚙️", "engine-room"),
]
for key, title, icon, url in SPECS:
    if url is None:
        registry.PAGES[key] = st.Page(_make_page(key), title=title, icon=icon, default=True)
    else:
        registry.PAGES[key] = st.Page(_make_page(key), title=title, icon=icon, url_path=url)

st.navigation(list(registry.PAGES.values()), position="top").run()
