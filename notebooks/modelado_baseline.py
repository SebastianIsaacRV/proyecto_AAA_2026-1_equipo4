"""
Script/notebook de referencia para modelado baseline
Proyecto: Predicción de Incidencia Delictiva Municipal en México
Equipo 4 — AAA 2026-1

Este archivo sirve como punto de partida unificado antes de dividir
el trabajo por tipo de modelo.
"""


import dagshub
dagshub.init(repo_owner='SebastianIsaacRV', repo_name='proyecto_AAA_2026-1_equipo4', mlflow=True)


# ── 0. Imports ────────────────────────────────────────────────────────────────
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import duckdb
import mlflow
import mlflow.sklearn

from pathlib import Path
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Modelos lineales
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet

# SVM
from sklearn.svm import SVR

# No lineales
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

warnings.filterwarnings("ignore")

# ── 1. Cargar dataset ─────────────────────────────────────────────────────────
# Ajusta la ruta según tu config.py
df = pd.read_parquet("../data/processed/dataset_baseline.parquet")




print(f"Shape: {df.shape}")
print(df.dtypes)
print(df.describe())


# ── 2. Features y Target ──────────────────────────────────────────────────────
# Numéricas — necesitan StandardScaler para modelos lineales y SVM
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

# Categóricas — one-hot encoding
FEATURES_CAT = [
    "region",
    "zona_metropolitana",
    "es_frontera",
]

TARGET = "tasa_delitos"

# Eliminar NaN en target o features
df_model = df[FEATURES_NUM + FEATURES_CAT + [TARGET, "año", "cvegeo"]].dropna()

X = df_model[FEATURES_NUM + FEATURES_CAT]
y = df_model[TARGET]

print(f"\nDataset limpio: {X.shape[0]} observaciones, {X.shape[1]} features")
print(f"Target — media: {y.mean():.1f}, std: {y.std():.1f}, min: {y.min():.1f}, max: {y.max():.1f}")


# ── 3. Split de datos ─────────────────────────────────────────────────────────
# Opción A: Split aleatorio simple (baseline rápido)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Opción B (recomendada para datos de panel): split por año
# años_train = df_model[df_model["año"] < 2023]["año"].unique()
# años_test  = df_model[df_model["año"] >= 2023]["año"].unique()
# mask_train = df_model["año"].isin(años_train)
# X_train, X_test = X[mask_train], X[~mask_train]
# y_train, y_test = y[mask_train], y[~mask_train]

print(f"\nTrain: {X_train.shape[0]} obs | Test: {X_test.shape[0]} obs")


# ── 4. Preprocessors ─────────────────────────────────────────────────────────
# Preprocessor CON estandarización (para lineales y SVM)
preprocessor_scaled = ColumnTransformer(transformers=[
    ("num", StandardScaler(), FEATURES_NUM),
    ("cat", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"), FEATURES_CAT),
])

# Preprocessor SIN estandarización (para árboles)
preprocessor_unscaled = ColumnTransformer(transformers=[
    ("num", "passthrough", FEATURES_NUM),
    ("cat", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"), FEATURES_CAT),
])


# ── 5. Definir modelos ────────────────────────────────────────────────────────
MODELS = {
    # ── Lineales (necesitan scaler) ──
    "OLS": Pipeline([
        ("prep", preprocessor_scaled),
        ("model", LinearRegression()),
    ]),
    "Ridge": Pipeline([
        ("prep", preprocessor_scaled),
        ("model", Ridge(alpha=1.0)),
    ]),
    "Lasso": Pipeline([
        ("prep", preprocessor_scaled),
        ("model", Lasso(alpha=0.1, max_iter=5000)),
    ]),
    "ElasticNet": Pipeline([
        ("prep", preprocessor_scaled),
        ("model", ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=5000)),
    ]),

    # ── SVM (necesitan scaler) ──
    "SVR_lineal": Pipeline([
        ("prep", preprocessor_scaled),
        ("model", SVR(kernel="linear", C=1.0)),
    ]),
    "SVR_rbf": Pipeline([
        ("prep", preprocessor_scaled),
        ("model", SVR(kernel="rbf", C=10.0, gamma="scale")),
    ]),

    # ── No lineales (sin scaler) ──
    "RandomForest": Pipeline([
        ("prep", preprocessor_unscaled),
        ("model", RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)),
    ]),
    "GradientBoosting": Pipeline([
        ("prep", preprocessor_unscaled),
        ("model", GradientBoostingRegressor(n_estimators=200, learning_rate=0.05, random_state=42)),
    ]),
}


# ── 6. Función de evaluación ──────────────────────────────────────────────────
def evaluar_modelo(nombre, pipeline, X_tr, X_te, y_tr, y_te, cv=5):
    """Entrena, evalúa con CV y en test. Devuelve dict con métricas."""
    # CV en train
    cv_rmse = -cross_val_score(
        pipeline, X_tr, y_tr,
        scoring="neg_root_mean_squared_error", cv=cv, n_jobs=-1
    )
    cv_r2 = cross_val_score(
        pipeline, X_tr, y_tr,
        scoring="r2", cv=cv, n_jobs=-1
    )

    # Fit final y evaluación en test
    pipeline.fit(X_tr, y_tr)
    y_pred = pipeline.predict(X_te)

    rmse_test = np.sqrt(mean_squared_error(y_te, y_pred))
    mae_test  = mean_absolute_error(y_te, y_pred)
    r2_test   = r2_score(y_te, y_pred)

    return {
        "modelo": nombre,
        "cv_rmse_mean": cv_rmse.mean(),
        "cv_rmse_std":  cv_rmse.std(),
        "cv_r2_mean":   cv_r2.mean(),
        "cv_r2_std":    cv_r2.std(),
        "test_rmse":    rmse_test,
        "test_mae":     mae_test,
        "test_r2":      r2_test,
    }


# ── 7. Entrenamiento y tracking con MLflow ────────────────────────────────────
# Si tienen DagsHub configurado, sustituir la URI de MLflow:
# mlflow.set_tracking_uri("https://dagshub.com/<usuario>/<repo>.mlflow")
mlflow.set_experiment("incidencia_delictiva_baseline")



resultados = []

for nombre, pipeline in MODELS.items():
    print(f"\nEntrenando {nombre}...")
    with mlflow.start_run(run_name=nombre):
        res = evaluar_modelo(
            nombre, pipeline,
            X_train, X_test, y_train, y_test
        )
        # Log a MLflow
        mlflow.log_param("modelo", nombre)
        mlflow.log_metric("cv_rmse_mean", res["cv_rmse_mean"])
        mlflow.log_metric("cv_r2_mean",   res["cv_r2_mean"])
        mlflow.log_metric("test_rmse",    res["test_rmse"])
        mlflow.log_metric("test_mae",     res["test_mae"])
        mlflow.log_metric("test_r2",      res["test_r2"])
        mlflow.sklearn.log_model(pipeline, artifact_path="model")

        resultados.append(res)
        print(f"  CV RMSE: {res['cv_rmse_mean']:.2f} ± {res['cv_rmse_std']:.2f}")
        print(f"  Test R²: {res['test_r2']:.3f}  |  Test RMSE: {res['test_rmse']:.2f}")


# ── 8. Tabla comparativa ──────────────────────────────────────────────────────
df_resultados = pd.DataFrame(resultados).sort_values("test_rmse")
print("\n── Resultados comparativos ──────────────────────────────────────────────")
print(df_resultados[["modelo","cv_rmse_mean","cv_r2_mean","test_rmse","test_mae","test_r2"]].to_string(index=False))

df_resultados.to_csv("../reports/resultados_baseline.csv", index=False)


# ── 9. Importancia de features (para modelos que lo soportan) ────────────────
def plot_feature_importance(pipeline, nombre_modelo, feature_names_num, feature_names_cat):
    model = pipeline.named_steps["model"]
    prep  = pipeline.named_steps["prep"]

    # Nombres de features transformadas
    cat_names = prep.named_transformers_["cat"].get_feature_names_out(feature_names_cat)
    all_names = list(feature_names_num) + list(cat_names)

    if hasattr(model, "feature_importances_"):
        imp = model.feature_importances_
    elif hasattr(model, "coef_"):
        imp = np.abs(model.coef_)
    else:
        return

    idx = np.argsort(imp)[-15:].astype(int)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh([all_names[i] for i in idx], imp[idx])
    ax.set_title(f"Importancia de features — {nombre_modelo}")
    ax.set_xlabel("Importancia (|coef| o Gini)")
    plt.tight_layout()
    plt.savefig(f"../reports/figures/feat_importance_{nombre_modelo.lower()}.png", dpi=150)
    plt.show()

for nombre, pipeline in MODELS.items():
    plot_feature_importance(pipeline, nombre, FEATURES_NUM, FEATURES_CAT)


print("\n✅ Modelado baseline completado. Revisa reports/ para los resultados.")
