import os
import mlflow
mlflow.set_tracking_uri("https://dagshub.com/SebastianIsaacRV/proyecto_AAA_2026-1_equipo4.mlflow")
os.environ["MLFLOW_TRACKING_USERNAME"] = "Antonio-JFB"
os.environ["MLFLOW_TRACKING_PASSWORD"] = "fee2eff0dc1f07f5a5358e83ffeb5aa125543ac6"


import mlflow.sklearn
import numpy as np
import pandas as pd
import optuna
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.ensemble import GradientBoostingRegressor
import xgboost as xgb
import lightgbm as lgb

# ── Features ──────────────────────────────────────────────────────────────────
FEATURES_NUM = [
    "indice_marginacion_normalizado_2020",
    "porcentaje_analfabetismo",
    "porcentaje_sin_agua_entubada",
    "porcentaje_viviendas_hacinamiento",
    "fn_pobreza_porcentaje",
    "fn_pobreza_extrema_porcentaje",
    "fn_vulnerable_ingresos_porcentaje",
    "fn_carencia_seguridad_social_porcentaje",
    "prop_urbano",
    "area_km2",
]
FEATURES_CAT = ["region", "zona_metropolitana", "es_frontera"]
TARGET = "tasa_delitos"

# ── Datos ─────────────────────────────────────────────────────────────────────
df = pd.read_parquet("data/processed/dataset_baseline.parquet")
df = df[FEATURES_NUM + FEATURES_CAT + [TARGET]].dropna()

X = df[FEATURES_NUM + FEATURES_CAT]
y = df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

prep = ColumnTransformer([
    ("num", "passthrough", FEATURES_NUM),
    ("cat", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"), FEATURES_CAT),
])

def evaluar(pipeline, nombre):
    cv_rmse = -cross_val_score(pipeline, X_train, y_train,
                                scoring="neg_root_mean_squared_error", cv=5, n_jobs=-1)
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    return {
        "cv_rmse_mean": cv_rmse.mean(),
        "cv_rmse_std":  cv_rmse.std(),
        "test_rmse":    np.sqrt(mean_squared_error(y_test, y_pred)),
        "test_mae":     mean_absolute_error(y_test, y_pred),
        "test_r2":      r2_score(y_test, y_pred),
    }

mlflow.set_experiment("boosting_delitos")

# ── 1. GradientBoosting baseline ──────────────────────────────────────────────
with mlflow.start_run(run_name="GradientBoosting_baseline"):
    pipe = Pipeline([("prep", prep), ("model", GradientBoostingRegressor(n_estimators=500, random_state=42))])
    res = evaluar(pipe, "GradientBoosting")
    mlflow.log_params({"modelo": "GradientBoosting", "n_estimators": 500})
    mlflow.log_metrics(res)
    print("GradientBoosting:", res)

# ── 2. XGBoost con Optuna ─────────────────────────────────────────────────────
def objective_xgb(trial):
    params = {
        "n_estimators":     trial.suggest_int("n_estimators", 200, 1000),
        "max_depth":        trial.suggest_int("max_depth", 3, 10),
        "learning_rate":    trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "subsample":        trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "reg_alpha":        trial.suggest_float("reg_alpha", 1e-4, 10, log=True),
        "reg_lambda":       trial.suggest_float("reg_lambda", 1e-4, 10, log=True),
    }
    pipe = Pipeline([("prep", prep), ("model", xgb.XGBRegressor(**params, random_state=42, n_jobs=-1))])
    cv = -cross_val_score(pipe, X_train, y_train,
                          scoring="neg_root_mean_squared_error", cv=5, n_jobs=1)
    return cv.mean()

study_xgb = optuna.create_study(direction="minimize")
study_xgb.optimize(objective_xgb, n_trials=50)

with mlflow.start_run(run_name="XGBoost_optuna"):
    best = study_xgb.best_params
    pipe = Pipeline([("prep", prep), ("model", xgb.XGBRegressor(**best, random_state=42, n_jobs=-1))])
    res = evaluar(pipe, "XGBoost")
    mlflow.log_params(best)
    mlflow.log_metrics(res)
    mlflow.sklearn.log_model(pipe, "model")
    print("XGBoost:", res)

# ── 3. LightGBM con Optuna ────────────────────────────────────────────────────
def objective_lgb(trial):
    params = {
        "n_estimators":   trial.suggest_int("n_estimators", 200, 1000),
        "max_depth":      trial.suggest_int("max_depth", 3, 10),
        "learning_rate":  trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "num_leaves":     trial.suggest_int("num_leaves", 20, 150),
        "subsample":      trial.suggest_float("subsample", 0.6, 1.0),
        "reg_alpha":      trial.suggest_float("reg_alpha", 1e-4, 10, log=True),
        "reg_lambda":     trial.suggest_float("reg_lambda", 1e-4, 10, log=True),
    }
    pipe = Pipeline([("prep", prep), ("model", lgb.LGBMRegressor(**params, random_state=42, n_jobs=-1, verbose=-1))])
    cv = -cross_val_score(pipe, X_train, y_train,
                          scoring="neg_root_mean_squared_error", cv=5, n_jobs=1)
    return cv.mean()

study_lgb = optuna.create_study(direction="minimize")
study_lgb.optimize(objective_lgb, n_trials=50)

with mlflow.start_run(run_name="LightGBM_optuna"):
    best = study_lgb.best_params
    pipe = Pipeline([("prep", prep), ("model", lgb.LGBMRegressor(**best, random_state=42, n_jobs=-1, verbose=-1))])
    res = evaluar(pipe, "LightGBM")
    mlflow.log_params(best)
    mlflow.log_metrics(res)
    mlflow.sklearn.log_model(pipe, "model")
    print("LightGBM:", res)

print("\n✅ Boosting completado.")
