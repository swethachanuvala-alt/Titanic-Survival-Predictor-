"""Re-train the model:  python train_model.py"""
from titanic_kit.model import train_and_save

if __name__ == "__main__":
    m = train_and_save()
    print(f"Saved model/titanic_rf_pipeline.joblib  |  test accuracy {m['accuracy']:.3f}  |  CV {m['cv_mean']:.3f}")
