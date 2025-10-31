import os
import pickle
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from fastapi.middleware.cors import CORSMiddleware
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

app = FastAPI(title="Health Prediction API", version="2.0.0")

# Add CORS Middleware
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3002",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# --- Data Structures to hold all models, scalers, and their metadata ---
models: Dict[str, Dict[str, Any]] = {}
scalers: Dict[str, Dict[str, Any]] = {}
model_metadata: Dict[str, Dict[str, Any]] = {}

disease_configs = {
    'Diabetes': {
        'model_file': 'diabetes_model.sav', 'dataset': 'diabetes.csv', 'target_col': 'Outcome',
        'scalers': {'old': None, 'new': 'diabetes_scaler.sav'},
        'algorithms': {'old': 'LogisticRegression', 'new': 'RandomForest'}
    },
    'Heart': {
        'model_file': 'heart_disease_model.sav', 'dataset': 'heart.csv', 'target_col': 'target',
        'scalers': {'old': None, 'new': 'heart_scaler.sav'},
        'algorithms': {'old': 'DecisionTree', 'new': 'GradientBoosting'}
    },
    'Parkinsons': {
        'model_file': 'parkinsons_model.sav', 'dataset': 'parkinsons.csv', 'target_col': 'status',
        'scalers': {'old': 'parkinsons_scaler.sav', 'new': None},
        'algorithms': {'old': 'SVM', 'new': 'AdaBoost'}
    },
    'Stroke': {
        'model_file': 'stroke_model.sav', 'dataset': 'healthcare-dataset-stroke-data.csv', 'target_col': 'stroke',
        'scalers': {'old': 'stroke_preprocessor.sav', 'new': 'stroke_preprocessor.sav'},
        'algorithms': {'old': 'LogisticRegression', 'new': 'RandomForest'}
    }
}

def load_and_evaluate_all_resources():
    """Loads all models/scalers and calculates their accuracy at startup."""
    working_dir = os.path.dirname(os.path.abspath(__file__))

    for disease, config in disease_configs.items():
        print(f"--- Processing {disease} ---")
        models[disease], scalers[disease], model_metadata[disease] = {}, {}, {}
        try:
            df = pd.read_csv(os.path.join(working_dir, "dataset", config['dataset']))
            if disease == 'Parkinsons':
                X = df.drop(columns=['name', config['target_col']], axis=1)
            elif disease == 'Stroke':
                df.drop('id', axis=1, inplace=True, errors='ignore')
                # Correct way to fill NaN in pandas
                bmi_median = df['bmi'].median()
                df['bmi'] = df['bmi'].fillna(bmi_median)
                df = df[df['gender'] != 'Other']
                X = df.drop(columns=[config['target_col']], axis=1)
            else:
                X = df.drop(columns=[config['target_col']], axis=1)
            y = df[config['target_col']]
            _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

            for version in ['old', 'new']:
                try:
                    model_path = os.path.join(working_dir, "saved_models", version, config['model_file'])
                    models[disease][version] = pickle.load(open(model_path, 'rb'))
                    
                    scaler_file = config['scalers'][version]
                    if scaler_file:
                        scaler_path = os.path.join(working_dir, "saved_models", version, scaler_file)
                        scalers[disease][version] = pickle.load(open(scaler_path, 'rb'))
                    else:
                        scalers[disease][version] = None

                    model_to_eval = models[disease][version]
                    scaler_to_eval = scalers[disease][version]
                    X_test_processed = X_test.copy()

                    if scaler_to_eval:
                        try:
                            X_test_processed = scaler_to_eval.transform(X_test_processed)
                        except Exception:
                             X_test_processed = scaler_to_eval.transform(X_test_processed.values)

                    y_pred = model_to_eval.predict(X_test_processed)
                    accuracy = accuracy_score(y_test, y_pred)
                    model_metadata[disease][version] = {
                        'algorithm': config['algorithms'][version],
                        'accuracy': accuracy
                    }
                    print(f"✅ Loaded {version.upper()} {disease} model ({config['algorithms'][version]}) with accuracy: {accuracy:.4f}")
                except FileNotFoundError:
                    print(f"⚠️ {version.upper()} model/scaler for {disease} not found. Skipping.")
                except Exception as e:
                    print(f"❌ Error loading/evaluating {version.upper()} model for {disease}: {e}")
        except Exception as e:
            print(f"❌ Failed to process data for {disease}: {e}")

@app.on_event("startup")
async def startup_event():
    load_and_evaluate_all_resources()

@app.get("/models-metadata")
async def get_models_metadata():
    return model_metadata

class PredictionRequest(BaseModel):
    model_version: str
    form_data: Dict[str, Any]

# --- NEW: Helper function from your Streamlit app ---
def calculate_cardiovascular_risk(predictions_dict):
    risk_score = 0
    risk_factors = []
    
    if predictions_dict.get('Heart', {}).get('prediction') == 1:
        risk_score += 40
        risk_factors.append("Direct Heart Disease Risk")
    if predictions_dict.get('Diabetes', {}).get('prediction') == 1:
        risk_score += 25
        risk_factors.append("Diabetes (increases cardiovascular complications)")
    if predictions_dict.get('Stroke', {}).get('prediction') == 1:
        risk_score += 30
        risk_factors.append("Stroke Risk (indicates vascular problems)")
    
    # Parkinson's is not typically a direct CV risk factor in the same way,
    # but we'll include it as per your original logic.
    if predictions_dict.get('Parkinsons', {}).get('prediction') == 1:
        risk_score += 15
        risk_factors.append("Parkinson's (may affect autonomic cardiovascular control)")

    risk_score = min(risk_score, 100)
    return {'score': risk_score, 'factors': risk_factors}

# --- Generic Prediction Function (Modified to be internally callable) ---
async def make_prediction(disease: str, request: PredictionRequest, return_dict=False):
    version = request.model_version
    data = request.form_data
    
    model = models.get(disease, {}).get(version)
    scaler = scalers.get(disease, {}).get(version)
    metadata = model_metadata.get(disease, {}).get(version)

    if not model or not metadata:
        if return_dict: return None
        raise HTTPException(status_code=404, detail=f"{version.capitalize()} model for {disease} not found.")

    if disease == "Parkinsons":
        parkinsons_name_map = {
            "fo": "MDVP:Fo(Hz)", "fhi": "MDVP:Fhi(Hz)", "flo": "MDVP:Flo(Hz)", "Jitter_percent": "MDVP:Jitter(%)", "Jitter_Abs": "MDVP:Jitter(Abs)",
            "RAP": "MDVP:RAP", "PPQ": "MDVP:PPQ", "DDP": "Jitter:DDP", "Shimmer": "MDVP:Shimmer", "Shimmer_dB": "MDVP:Shimmer(dB)",
            "APQ3": "Shimmer:APQ3", "APQ5": "Shimmer:APQ5", "APQ": "MDVP:APQ", "DDA": "Shimmer:DDA", "NHR": "NHR", "HNR": "HNR",
            "RPDE": "RPDE", "DFA": "DFA", "spread1": "spread1", "spread2": "spread2", "D2": "D2", "PPE": "PPE"
        }
        try:
            data = {parkinsons_name_map[key]: value for key, value in data.items()}
        except KeyError as e:
            if return_dict: return None
            raise HTTPException(status_code=400, detail=f"Invalid feature name for Parkinson's model: {e}")

    try:
        input_df = pd.DataFrame([data])
        input_for_model = input_df
        
        if scaler:
            try:
                input_for_model = scaler.transform(input_df)
            except Exception:
                input_for_model = scaler.transform(input_df.values)

        prediction = model.predict(input_for_model)
        
        confidence = 100.0
        if hasattr(model, 'predict_proba'):
            try:
                probability = model.predict_proba(input_for_model)
                confidence = float(np.max(probability[0])) * 100
            except Exception:
                pass # Default confidence will be used
        
        result = {
            "prediction": int(prediction[0]),
            "confidence": confidence,
            "result_message": f"High risk of {disease}" if prediction[0] == 1 else f"Low risk of {disease}",
            "accuracy": metadata['accuracy']
        }
        return result
    except Exception as e:
        if return_dict: return None
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# --- API Endpoints for each disease ---
@app.post("/predict/diabetes")
async def predict_diabetes(request: PredictionRequest):
    return await make_prediction("Diabetes", request)

@app.post("/predict/heart")
async def predict_heart(request: PredictionRequest):
    return await make_prediction("Heart", request)

@app.post("/predict/parkinsons")
async def predict_parkinsons(request: PredictionRequest):
    return await make_prediction("Parkinsons", request)

@app.post("/predict/stroke")
async def predict_stroke(request: PredictionRequest):
    return await make_prediction("Stroke", request)

# --- NEW: Comprehensive Assessment Endpoint ---
@app.post("/predict/comprehensive")
async def predict_comprehensive(request: PredictionRequest):
    form_data = request.form_data
    predictions = {}
    
    # 1. Run Diabetes Prediction
    try:
        diabetes_data = {
            "Pregnancies": form_data['pregnancies'], "Glucose": form_data['glucose'], "BloodPressure": form_data['blood_pressure'],
            "SkinThickness": form_data['skin_thickness'], "Insulin": form_data['insulin'], "BMI": form_data['bmi'],
            "DiabetesPedigreeFunction": form_data['diabetes_pedigree'], "Age": form_data['age']
        }
        predictions['Diabetes'] = await make_prediction("Diabetes", PredictionRequest(model_version=request.model_version, form_data=diabetes_data), return_dict=True)
    except Exception as e:
        print(f"Error in comprehensive diabetes pred: {e}")

    # 2. Run Heart Disease Prediction
    try:
        heart_data = {
            "age": form_data['age'], "sex": 1 if form_data['gender'] == 'Male' else 0, "cp": form_data['chest_pain'],
            "trestbps": form_data['blood_pressure'], "chol": form_data['cholesterol'], "fbs": form_data['fasting_blood_sugar'],
            "restecg": form_data['rest_ecg'], "thalach": form_data['max_heart_rate'], "exang": form_data['exercise_angina'],
            "oldpeak": form_data['oldpeak'], "slope": form_data['slope'], "ca": form_data['ca'], "thal": form_data['thal']
        }
        predictions['Heart'] = await make_prediction("Heart", PredictionRequest(model_version=request.model_version, form_data=heart_data), return_dict=True)
    except Exception as e:
        print(f"Error in comprehensive heart pred: {e}")

    # 3. Run Stroke Prediction
    try:
        stroke_data = {
            "age": form_data['age'], "hypertension": form_data['hypertension'], "heart_disease": form_data['heart_disease_history'],
            "avg_glucose_level": form_data['glucose'], "bmi": form_data['bmi'], "gender": form_data['gender'],
            "ever_married": form_data['ever_married'], "work_type": form_data['work_type'],
            "Residence_type": form_data['residence_type'], "smoking_status": form_data['smoking_status']
        }
        predictions['Stroke'] = await make_prediction("Stroke", PredictionRequest(model_version=request.model_version, form_data=stroke_data), return_dict=True)
    except Exception as e:
        print(f"Error in comprehensive stroke pred: {e}")
    
    # 4. Calculate Cardiovascular Risk
    cv_risk = calculate_cardiovascular_risk(predictions)

    return {
        "individual_predictions": predictions,
        "cardiovascular_risk": cv_risk
    }