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

# ============================================
# CORS Configuration for GitHub Pages and Local Development
# ============================================
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3002",
    "http://localhost:5000",
    "http://127.0.0.1:3000",
    "https://mohit-balachander.github.io",  # GitHub Pages
    "https://*.web.app",
    "https://*.firebaseapp.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=False,  # Set to False when using wildcard
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# --- Data Structures to hold all models, scalers, and their metadata ---
models: Dict[str, Dict[str, Any]] = {}
scalers: Dict[str, Dict[str, Any]] = {}
model_metadata: Dict[str, Dict[str, Any]] = {}

disease_configs = {
    'Diabetes': {
        'model_file': 'diabetes_model.sav', 
        'dataset': 'diabetes.csv', 
        'target_col': 'Outcome',
        'scalers': {'old': None, 'new': 'diabetes_scaler.sav'},
        'algorithms': {'old': 'LogisticRegression', 'new': 'RandomForest'}
    },
    'Heart': {
        'model_file': 'heart_disease_model.sav', 
        'dataset': 'heart.csv', 
        'target_col': 'target',
        'scalers': {'old': None, 'new': 'heart_scaler.sav'},
        'algorithms': {'old': 'DecisionTree', 'new': 'GradientBoosting'}
    },
    'Parkinsons': {
        'model_file': 'parkinsons_model.sav', 
        'dataset': 'parkinsons.csv', 
        'target_col': 'status',
        'scalers': {'old': 'parkinsons_scaler.sav', 'new': None},
        'algorithms': {'old': 'SVM', 'new': 'AdaBoost'}
    },
    'Stroke': {
        'model_file': 'stroke_model.sav', 
        'dataset': 'healthcare-dataset-stroke-data.csv', 
        'target_col': 'stroke',
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

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Health Prediction API is running",
        "version": "2.0.0",
        "status": "healthy"
    }

@app.get("/models-metadata")
async def get_models_metadata():
    """Get metadata for all loaded models"""
    return model_metadata

class PredictionRequest(BaseModel):
    model_version: str
    form_data: Dict[str, Any]

# --- Helper function to calculate cardiovascular risk ---
def calculate_cardiovascular_risk(predictions_dict):
    """Calculate overall cardiovascular risk based on individual predictions"""
    risk_score = 0
    risk_factors = []
    
    # Safely check each prediction, handling None values
    heart_pred = predictions_dict.get('Heart')
    if heart_pred and heart_pred.get('prediction') == 1:
        risk_score += 40
        risk_factors.append("Direct Heart Disease Risk")
    
    diabetes_pred = predictions_dict.get('Diabetes')
    if diabetes_pred and diabetes_pred.get('prediction') == 1:
        risk_score += 25
        risk_factors.append("Diabetes (increases cardiovascular complications)")
    
    stroke_pred = predictions_dict.get('Stroke')
    if stroke_pred and stroke_pred.get('prediction') == 1:
        risk_score += 30
        risk_factors.append("Stroke Risk (indicates vascular problems)")
    
    # Parkinson's may affect autonomic cardiovascular control
    parkinsons_pred = predictions_dict.get('Parkinsons')
    if parkinsons_pred and parkinsons_pred.get('prediction') == 1:
        risk_score += 15
        risk_factors.append("Parkinson's (may affect autonomic cardiovascular control)")

    risk_score = min(risk_score, 100)
    return {'score': risk_score, 'factors': risk_factors}

# --- Generic Prediction Function ---
async def make_prediction(disease: str, request: PredictionRequest, return_dict=False):
    """
    Generic prediction function for all diseases
    
    Args:
        disease: Name of the disease (Diabetes, Heart, Parkinsons, Stroke)
        request: PredictionRequest containing model_version and form_data
        return_dict: If True, returns None on error instead of raising HTTPException
    """
    version = request.model_version
    data = request.form_data
    
    model = models.get(disease, {}).get(version)
    scaler = scalers.get(disease, {}).get(version)
    metadata = model_metadata.get(disease, {}).get(version)

    if not model or not metadata:
        if return_dict: 
            return None
        raise HTTPException(
            status_code=404, 
            detail=f"{version.capitalize()} model for {disease} not found."
        )

    # Special handling for Parkinson's feature names
    if disease == "Parkinsons":
        parkinsons_name_map = {
            "fo": "MDVP:Fo(Hz)", 
            "fhi": "MDVP:Fhi(Hz)", 
            "flo": "MDVP:Flo(Hz)", 
            "Jitter_percent": "MDVP:Jitter(%)", 
            "Jitter_Abs": "MDVP:Jitter(Abs)",
            "RAP": "MDVP:RAP", 
            "PPQ": "MDVP:PPQ", 
            "DDP": "Jitter:DDP", 
            "Shimmer": "MDVP:Shimmer", 
            "Shimmer_dB": "MDVP:Shimmer(dB)",
            "APQ3": "Shimmer:APQ3", 
            "APQ5": "Shimmer:APQ5", 
            "APQ": "MDVP:APQ", 
            "DDA": "Shimmer:DDA", 
            "NHR": "NHR", 
            "HNR": "HNR",
            "RPDE": "RPDE", 
            "DFA": "DFA", 
            "spread1": "spread1", 
            "spread2": "spread2", 
            "D2": "D2", 
            "PPE": "PPE"
        }
        try:
            data = {parkinsons_name_map[key]: value for key, value in data.items()}
        except KeyError as e:
            if return_dict: 
                return None
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid feature name for Parkinson's model: {e}"
            )

    try:
        input_df = pd.DataFrame([data])
        input_for_model = input_df
        
        # Apply scaling if scaler exists
        if scaler:
            try:
                input_for_model = scaler.transform(input_df)
            except Exception:
                input_for_model = scaler.transform(input_df.values)

        # Make prediction
        prediction = model.predict(input_for_model)
        
        # Calculate confidence if model supports probability
        confidence = 100.0
        if hasattr(model, 'predict_proba'):
            try:
                probability = model.predict_proba(input_for_model)
                confidence = float(np.max(probability[0])) * 100
            except Exception:
                pass  # Use default confidence
        
        result = {
            "prediction": int(prediction[0]),
            "confidence": round(confidence, 2),
            "result_message": f"High risk of {disease}" if prediction[0] == 1 else f"Low risk of {disease}",
            "model_accuracy": round(metadata['accuracy'] * 100, 2),
            "algorithm": metadata['algorithm']
        }
        return result
    except Exception as e:
        if return_dict: 
            return None
        raise HTTPException(
            status_code=500, 
            detail=f"Prediction error: {str(e)}"
        )

# ============================================
# API Endpoints for Individual Diseases
# ============================================

@app.post("/predict/diabetes")
async def predict_diabetes(request: PredictionRequest):
    """
    Predict diabetes risk
    
    Required fields in form_data:
    - Pregnancies, Glucose, BloodPressure, SkinThickness, 
      Insulin, BMI, DiabetesPedigreeFunction, Age
    """
    return await make_prediction("Diabetes", request)

@app.post("/predict/heart")
async def predict_heart(request: PredictionRequest):
    """
    Predict heart disease risk
    
    Required fields in form_data:
    - age, sex, cp, trestbps, chol, fbs, restecg, 
      thalach, exang, oldpeak, slope, ca, thal
    """
    return await make_prediction("Heart", request)

@app.post("/predict/parkinsons")
async def predict_parkinsons(request: PredictionRequest):
    """
    Predict Parkinson's disease risk
    
    Required fields in form_data:
    - fo, fhi, flo, Jitter_percent, Jitter_Abs, RAP, PPQ, DDP,
      Shimmer, Shimmer_dB, APQ3, APQ5, APQ, DDA, NHR, HNR,
      RPDE, DFA, spread1, spread2, D2, PPE
    """
    return await make_prediction("Parkinsons", request)

@app.post("/predict/stroke")
async def predict_stroke(request: PredictionRequest):
    """
    Predict stroke risk
    
    Required fields in form_data:
    - age, hypertension, heart_disease, avg_glucose_level, bmi,
      gender, ever_married, work_type, Residence_type, smoking_status
    """
    return await make_prediction("Stroke", request)

# ============================================
# Comprehensive Assessment Endpoint
# ============================================

@app.post("/predict/comprehensive")
async def predict_comprehensive(request: PredictionRequest):
    """
    Run comprehensive health assessment across all four disease models
    
    This endpoint takes a comprehensive form with all health parameters
    and returns predictions for Diabetes, Heart Disease, Stroke, and
    an overall Cardiovascular Risk Score.
    """
    form_data = request.form_data
    predictions = {}
    
    # 1. Run Diabetes Prediction
    try:
        diabetes_data = {
            "Pregnancies": form_data['pregnancies'], 
            "Glucose": form_data['glucose'], 
            "BloodPressure": form_data['blood_pressure'],
            "SkinThickness": form_data['skin_thickness'], 
            "Insulin": form_data['insulin'], 
            "BMI": form_data['bmi'],
            "DiabetesPedigreeFunction": form_data['diabetes_pedigree'], 
            "Age": form_data['age']
        }
        predictions['Diabetes'] = await make_prediction(
            "Diabetes", 
            PredictionRequest(model_version=request.model_version, form_data=diabetes_data), 
            return_dict=True
        )
    except Exception as e:
        print(f"Error in comprehensive diabetes prediction: {e}")
        predictions['Diabetes'] = None

    # 2. Run Heart Disease Prediction
    try:
        heart_data = {
            "age": form_data['age'], 
            "sex": 1 if form_data['gender'] == 'Male' else 0, 
            "cp": form_data['chest_pain'],
            "trestbps": form_data['blood_pressure'], 
            "chol": form_data['cholesterol'], 
            "fbs": form_data['fasting_blood_sugar'],
            "restecg": form_data['rest_ecg'], 
            "thalach": form_data['max_heart_rate'], 
            "exang": form_data['exercise_angina'],
            "oldpeak": form_data['oldpeak'], 
            "slope": form_data['slope'], 
            "ca": form_data['ca'], 
            "thal": form_data['thal']
        }
        predictions['Heart'] = await make_prediction(
            "Heart", 
            PredictionRequest(model_version=request.model_version, form_data=heart_data), 
            return_dict=True
        )
    except Exception as e:
        print(f"Error in comprehensive heart prediction: {e}")
        predictions['Heart'] = None

    # 3. Run Stroke Prediction
    try:
        stroke_data = {
            "age": form_data['age'], 
            "hypertension": form_data['hypertension'], 
            "heart_disease": form_data['heart_disease_history'],
            "avg_glucose_level": form_data['glucose'], 
            "bmi": form_data['bmi'], 
            "gender": form_data['gender'],
            "ever_married": form_data['ever_married'], 
            "work_type": form_data['work_type'],
            "Residence_type": form_data['residence_type'], 
            "smoking_status": form_data['smoking_status']
        }
        predictions['Stroke'] = await make_prediction(
            "Stroke", 
            PredictionRequest(model_version=request.model_version, form_data=stroke_data), 
            return_dict=True
        )
    except Exception as e:
        print(f"Error in comprehensive stroke prediction: {e}")
        predictions['Stroke'] = None
    
    # 4. Calculate Cardiovascular Risk
    cv_risk = calculate_cardiovascular_risk(predictions)

    return {
        "individual_predictions": predictions,
        "cardiovascular_risk": cv_risk,
        "timestamp": pd.Timestamp.now().isoformat()
    }

# ============================================
# Health Check and Info Endpoints
# ============================================

@app.get("/health")
async def health_check():
    """Detailed health check with model status"""
    return {
        "status": "healthy",
        "models_loaded": {
            disease: list(models.get(disease, {}).keys()) 
            for disease in disease_configs.keys()
        },
        "total_models": sum(len(models.get(d, {})) for d in disease_configs.keys())
    }