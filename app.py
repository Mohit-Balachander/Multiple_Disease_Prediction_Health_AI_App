import os
import pickle
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from streamlit_option_menu import option_menu
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler

# Set page configuration
st.set_page_config(page_title="Health Assistant",
                   layout="wide",
                   page_icon="🧑‍⚕️")

# Get working directory
working_dir = os.path.dirname(os.path.abspath(__file__))

# Function to load models
def load_model(version_folder, model_name):
    model_path = os.path.join(working_dir, "backend", "saved_models", version_folder, model_name)
    try:
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        if hasattr(model, 'predict'):
            return model
        else:
            st.error(f"Error: Loaded object from {model_path} is not a model (missing predict method)")
            return None
    except Exception as e:
        st.error(f"Error loading model from {model_path}: {str(e)}")
        return None

# Function to load scaler/preprocessor if exists
def load_scaler(version_folder, scaler_name):
    try:
        scaler_path = os.path.join(working_dir, "backend", "saved_models", version_folder, scaler_name)
        with open(scaler_path, "rb") as f:
            scaler = pickle.load(f)
        if hasattr(scaler, 'transform'):
            return scaler
        else:
            st.error(f"Error: Loaded object from {scaler_path} is not a scaler/preprocessor")
            return None
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"Error loading scaler from {scaler_path}: {str(e)}")
        return None

# Function to load datasets
def load_dataset(dataset_name):
    dataset_path = os.path.join(working_dir, "backend", "dataset", dataset_name)
    try:
        return pd.read_csv(dataset_path)
    except FileNotFoundError:
        st.error(f"Dataset {dataset_name} not found in backend/dataset/ directory")
        return None
    except Exception as e:
        st.error(f"Error loading dataset {dataset_name}: {str(e)}")
        return None

# Function to evaluate model performance
def evaluate_model_performance(model, X_test, y_test, model_name):
    try:
        if model is None:
            st.error(f"Model {model_name} is None, cannot evaluate")
            return None
        
        y_pred = model.predict(X_test)
        
        cm = confusion_matrix(y_test, y_pred)
        
        if cm.shape != (2, 2):
            cm_full = np.zeros((2, 2), dtype=int)
            if cm.shape == (1, 1):
                if y_test.iloc[0] == 0:
                    cm_full[0, 0] = cm[0, 0]
                else:
                    cm_full[1, 1] = cm[0, 0]
            cm = cm_full
        
        metrics = {
            'model_name': model_name,
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='binary', zero_division=0),
            'recall': recall_score(y_test, y_pred, average='binary', zero_division=0),
            'f1_score': f1_score(y_test, y_pred, average='binary', zero_division=0),
            'confusion_matrix': cm
        }
        return metrics
    except Exception as e:
        st.error(f"Error evaluating {model_name}: {str(e)}")
        return None

# Function to create confusion matrix heatmap
def create_confusion_matrix_plot(cm, title, disease_name):
    cm_array = np.array(cm)
    
    fig = go.Figure(data=go.Heatmap(
        z=cm_array,
        x=['Predicted Negative', 'Predicted Positive'],
        y=['Actual Negative', 'Actual Positive'],
        hoverongaps=False,
        colorscale='Blues',
        text=cm_array,
        texttemplate="%{text}",
        textfont={"size": 16},
        showscale=True
    ))
    
    fig.update_layout(
        title=f'{title} - {disease_name}',
        xaxis_title='Predicted',
        yaxis_title='Actual',
        width=400,
        height=400,
        font=dict(size=12)
    )
    
    return fig

# Function to calculate cardiovascular risk score
def calculate_cardiovascular_risk(predictions_dict):
    """
    Calculate overall cardiovascular risk based on multiple disease predictions
    """
    risk_score = 0
    risk_factors = []
    
    # Base risk from heart disease prediction
    if predictions_dict.get('heart_disease', {}).get('prediction') == 1:
        risk_score += 40
        risk_factors.append("Direct Heart Disease Risk")
    
    # Diabetes increases cardiovascular risk
    if predictions_dict.get('diabetes', {}).get('prediction') == 1:
        risk_score += 25
        risk_factors.append("Diabetes (increases cardiovascular complications)")
    
    # Stroke risk is closely related to cardiovascular health
    if predictions_dict.get('stroke', {}).get('prediction') == 1:
        risk_score += 30
        risk_factors.append("Stroke Risk (indicates vascular problems)")
    
    # Parkinson's can affect cardiovascular function
    if predictions_dict.get('parkinsons', {}).get('prediction') == 1:
        risk_score += 15
        risk_factors.append("Parkinson's (may affect autonomic cardiovascular control)")
    
    # Cap at 100
    risk_score = min(risk_score, 100)
    
    return risk_score, risk_factors

# Function to display heart health impact
def display_heart_health_impact(disease_name, prediction, confidence=None):
    """
    Display how the specific disease affects heart health
    """
    st.markdown("---")
    st.subheader("💓 Impact on Heart Health")
    
    impact_info = {
        'Diabetes': {
            'positive': {
                'risk': 'HIGH',
                'color': 'red',
                'description': """
                **Diabetes significantly increases cardiovascular risk:**
                - 2-4x higher risk of heart disease
                - Damages blood vessels over time
                - Increases risk of atherosclerosis
                - Higher risk of heart attack and stroke
                
                **Recommendations:**
                - Regular cardiac check-ups (every 6 months)
                - Monitor blood pressure closely
                - Control cholesterol levels
                - Maintain HbA1c below 7%
                """
            },
            'negative': {
                'risk': 'BASELINE',
                'color': 'green',
                'description': """
                **No diabetes detected - Lower cardiovascular risk:**
                - Maintain healthy blood sugar levels
                - Continue healthy lifestyle
                - Regular monitoring recommended
                """
            }
        },
        'Heart Disease': {
            'positive': {
                'risk': 'CRITICAL',
                'color': 'darkred',
                'description': """
                **Direct heart disease risk detected:**
                - Immediate medical attention required
                - Comprehensive cardiac evaluation needed
                - May require medication or intervention
                
                **Urgent Actions:**
                - Consult cardiologist immediately
                - Complete cardiac workup (ECG, Echo, Stress test)
                - Lifestyle modifications essential
                - Consider medication as prescribed
                """
            },
            'negative': {
                'risk': 'LOW',
                'color': 'green',
                'description': """
                **No direct heart disease detected:**
                - Continue preventive measures
                - Annual cardiac screening recommended
                - Maintain healthy lifestyle
                """
            }
        },
        'Stroke': {
            'positive': {
                'risk': 'VERY HIGH',
                'color': 'red',
                'description': """
                **Stroke risk indicates serious cardiovascular concerns:**
                - Shares common risk factors with heart disease
                - Indicates vascular system problems
                - Urgent cardiovascular assessment needed
                
                **Critical Actions:**
                - Immediate neurologist and cardiologist consultation
                - Vascular health assessment
                - Blood pressure control crucial
                - Antiplatelet therapy may be needed
                """
            },
            'negative': {
                'risk': 'LOW',
                'color': 'green',
                'description': """
                **Low stroke risk - Better cardiovascular outlook:**
                - Continue preventive care
                - Maintain blood pressure control
                - Regular health monitoring
                """
            }
        },
        'Parkinsons': {
            'positive': {
                'risk': 'MODERATE',
                'color': 'orange',
                'description': """
                **Parkinson's can affect cardiovascular function:**
                - Autonomic dysfunction may affect heart rate
                - Blood pressure regulation issues possible
                - Orthostatic hypotension common
                - Increased fall risk
                
                **Monitoring Needed:**
                - Regular cardiovascular assessments
                - Blood pressure monitoring (especially positional)
                - Heart rate variability checks
                - Careful medication management
                """
            },
            'negative': {
                'risk': 'BASELINE',
                'color': 'green',
                'description': """
                **No Parkinson's detected:**
                - Normal autonomic cardiovascular function expected
                - Continue regular health maintenance
                """
            }
        }
    }
    
    status = 'positive' if prediction == 1 else 'negative'
    info = impact_info[disease_name][status]
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown(f"### Cardiovascular Risk Level")
        st.markdown(f"<h2 style='color:{info['color']}'>{info['risk']}</h2>", unsafe_allow_html=True)
        if confidence:
            st.metric("Prediction Confidence", f"{confidence:.1f}%")
    
    with col2:
        st.markdown(info['description'])

# Function to create comprehensive health visualization
def create_comprehensive_health_chart(predictions_dict):
    """
    Create a comprehensive visualization of all health predictions
    """
    diseases = []
    risks = []
    colors = []
    
    disease_map = {
        'diabetes': 'Diabetes',
        'heart_disease': 'Heart Disease',
        'stroke': 'Stroke',
        'parkinsons': "Parkinson's"
    }
    
    for key, name in disease_map.items():
        if key in predictions_dict and predictions_dict[key]:
            diseases.append(name)
            pred = predictions_dict[key].get('prediction', 0)
            conf = predictions_dict[key].get('confidence', 50)
            
            # Risk percentage based on prediction and confidence
            risk = (pred * conf) if pred == 1 else ((1 - pred) * (100 - conf))
            risks.append(risk)
            colors.append('red' if pred == 1 else 'green')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=diseases,
        x=risks,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgb(8,48,107)', width=1.5)
        ),
        text=[f"{r:.1f}%" for r in risks],
        textposition='auto',
    ))
    
    fig.update_layout(
        title="Comprehensive Health Risk Assessment",
        xaxis_title="Risk Level (%)",
        yaxis_title="Health Conditions",
        xaxis=dict(range=[0, 100]),
        height=400,
        showlegend=False
    )
    
    return fig

# Sidebar Navigation
with st.sidebar:
    selected = option_menu('Multiple Disease Prediction System',
                          ['Model Comparison Dashboard',
                           'Diabetes Prediction',
                           'Heart Disease Prediction',
                           'Parkinsons Prediction',
                           'Stroke Prediction',
                           'Comprehensive Health Assessment'],
                          menu_icon='hospital-fill',
                          icons=['bar-chart', 'activity', 'heart', 'person', 'lightning', 'clipboard-heart'],
                          default_index=0)

# ====== MODEL COMPARISON DASHBOARD ======
if selected == 'Model Comparison Dashboard':
    st.title('🔍 Enhanced Model Performance Comparison Dashboard')
    
    diseases_info = {
        'Diabetes': {
            'model_file': 'diabetes_model.sav',
            'dataset': 'diabetes.csv',
            'target_col': 'Outcome',
            'scaler_old': None,
            'scaler_new': 'diabetes_scaler.sav',
            'old_algorithm': 'LogisticRegression',
            'new_algorithm': 'RandomForest'
        },
        'Heart': {
            'model_file': 'heart_disease_model.sav',
            'dataset': 'heart.csv',
            'target_col': 'target',
            'scaler_old': None,
            'scaler_new': 'heart_scaler.sav',
            'old_algorithm': 'DecisionTree',
            'new_algorithm': 'GradientBoosting'
        },
        'Parkinsons': {
            'model_file': 'parkinsons_model.sav',
            'dataset': 'parkinsons.csv',
            'target_col': 'status',
            'scaler_old': 'parkinsons_scaler.sav',
            'scaler_new': None,
            'old_algorithm': 'SVM',
            'new_algorithm': 'AdaBoost'
        },
        'Stroke': {
            'model_file': 'stroke_model.sav',
            'dataset': 'healthcare-dataset-stroke-data.csv',
            'target_col': 'stroke',
            'scaler_old': 'stroke_preprocessor.sav',
            'scaler_new': 'stroke_preprocessor.sav',
            'old_algorithm': 'LogisticRegression',
            'new_algorithm': 'RandomForest'
        }
    }
    
    all_metrics = []
    confusion_matrices = {}
    
    for disease, info in diseases_info.items():
        try:
            df = load_dataset(info['dataset'])
            if df is None:
                continue
                
            if disease == 'Parkinsons':
                X = df.drop(columns=['name', info['target_col']], axis=1)
            elif disease == 'Stroke':
                df_processed = df.drop('id', axis=1)
                df_processed['bmi'].fillna(df_processed['bmi'].median(), inplace=True)
                df_processed = df_processed[df_processed['gender'] != 'Other'] if 'Other' in df_processed['gender'].values else df_processed
                
                categorical_features = ['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
                numerical_features = ['age', 'hypertension', 'heart_disease', 'avg_glucose_level', 'bmi']
                X = df_processed[numerical_features + categorical_features]
                y = df_processed[info['target_col']]
            else:
                X = df.drop(columns=info['target_col'], axis=1)
                y = df[info['target_col']]
            
            if disease != 'Stroke':
                y = df[info['target_col']]
            
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
            
            try:
                old_model = load_model('old', info['model_file'])
                if old_model is not None:
                    X_test_old = X_test.copy()
                    
                    if info['scaler_old']:
                        scaler_old = load_scaler('old', info['scaler_old'])
                        if scaler_old:
                            X_test_old = scaler_old.transform(X_test_old)
                    
                    old_metrics = evaluate_model_performance(old_model, X_test_old, y_test, 
                                                           f'{disease}_{info["old_algorithm"]}')
                    if old_metrics:
                        old_metrics['model_type'] = 'Old'
                        old_metrics['disease'] = disease
                        old_metrics['algorithm'] = info['old_algorithm']
                        all_metrics.append(old_metrics)
                        confusion_matrices[f'{disease}_{info["old_algorithm"]}'] = old_metrics['confusion_matrix']
                
            except Exception as e:
                st.warning(f"Could not load old model for {disease}: {str(e)}")
            
            try:
                new_model = load_model('new', info['model_file'])
                if new_model is not None:
                    X_test_new = X_test.copy()
                    
                    if info['scaler_new']:
                        scaler_new = load_scaler('new', info['scaler_new'])
                        if scaler_new:
                            X_test_new = scaler_new.transform(X_test_new)
                    
                    new_metrics = evaluate_model_performance(new_model, X_test_new, y_test, 
                                                           f'{disease}_{info["new_algorithm"]}')
                    if new_metrics:
                        new_metrics['model_type'] = 'New'
                        new_metrics['disease'] = disease
                        new_metrics['algorithm'] = info['new_algorithm']
                        all_metrics.append(new_metrics)
                        confusion_matrices[f'{disease}_{info["new_algorithm"]}'] = new_metrics['confusion_matrix']
                
            except Exception as e:
                st.warning(f"Could not load new model for {disease}: {str(e)}")
                
        except Exception as e:
            st.error(f"Error processing {disease}: {str(e)}")
    
    if all_metrics:
        metrics_df = pd.DataFrame(all_metrics)
        
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance Metrics", "🔄 Confusion Matrix", 
                                         "📈 Detailed Analysis", "🎯 Model Selection Guide"])
        
        with tab1:
            st.subheader("📊 Model Performance Comparison")
            
            fig = go.Figure()
            
            diseases = metrics_df['disease'].unique()
            
            for disease in diseases:
                disease_data = metrics_df[metrics_df['disease'] == disease]
                info = diseases_info[disease]
                
                old_data = disease_data[disease_data['model_type'] == 'Old']
                new_data = disease_data[disease_data['model_type'] == 'New']
                
                if not old_data.empty:
                    fig.add_trace(go.Bar(
                        name=f'{disease}_{info["old_algorithm"]}',
                        x=[f'{disease}_{info["old_algorithm"]}'],
                        y=[old_data.iloc[0]['accuracy']],
                        marker_color='lightblue',
                        text=[f"{old_data.iloc[0]['accuracy']:.3f}"],
                        textposition='auto',
                    ))
                
                if not new_data.empty:
                    fig.add_trace(go.Bar(
                        name=f'{disease}_{info["new_algorithm"]}',
                        x=[f'{disease}_{info["new_algorithm"]}'],
                        y=[new_data.iloc[0]['accuracy']],
                        marker_color='#FA8072',
                        text=[f"{new_data.iloc[0]['accuracy']:.3f}"],
                        textposition='auto',
                    ))
            
            fig.update_layout(
                title="Model Accuracy Comparison Across Diseases",
                xaxis_title="Models",
                yaxis_title="Accuracy",
                yaxis=dict(range=[0, 1]),
                showlegend=False,
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📋 Detailed Performance Metrics")
            display_df = metrics_df[['disease', 'algorithm', 'accuracy', 'precision', 'recall', 'f1_score']].copy()
            display_df.columns = ['Disease', 'Algorithm', 'Accuracy', 'Precision', 'Recall', 'F1-Score']
            display_df = display_df.round(4)
            
            st.dataframe(display_df, use_container_width=True)
        
        with tab2:
            st.subheader("🔄 Confusion Matrices")
            
            num_models = len(confusion_matrices)
            cols_per_row = 2
            
            keys = list(confusion_matrices.keys())
            for i in range(0, len(keys), cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    if i + j < len(keys):
                        key = keys[i + j]
                        cm = confusion_matrices[key]
                        
                        parts = key.split('_')
                        disease = parts[0]
                        algorithm = '_'.join(parts[1:])
                        
                        fig = create_confusion_matrix_plot(cm, algorithm, disease)
                        with cols[j]:
                            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("📈 Detailed Performance Analysis")
            
            if len(metrics_df) > 0:
                fig = go.Figure()
                
                for idx, row in metrics_df.iterrows():
                    fig.add_trace(go.Scatterpolar(
                        r=[row['accuracy'], row['precision'], row['recall'], row['f1_score']],
                        theta=['Accuracy', 'Precision', 'Recall', 'F1-Score'],
                        fill='toself',
                        name=f"{row['disease']}_{row['algorithm']}",
                        line_color='blue' if row['model_type'] == 'Old' else 'red',
                        opacity=0.6
                    ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1]
                        )),
                    showlegend=True,
                    title="Performance Metrics Radar Chart",
                    height=600
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📊 Model Improvement Summary")
            
            improvements = []
            for disease in diseases:
                disease_data = metrics_df[metrics_df['disease'] == disease]
                old_data = disease_data[disease_data['model_type'] == 'Old']
                new_data = disease_data[disease_data['model_type'] == 'New']
                
                if not old_data.empty and not new_data.empty:
                    old_acc = old_data.iloc[0]['accuracy']
                    new_acc = new_data.iloc[0]['accuracy']
                    improvement = ((new_acc - old_acc) / old_acc) * 100
                    
                    improvements.append({
                        'Disease': disease,
                        'Old Model': diseases_info[disease]['old_algorithm'],
                        'New Model': diseases_info[disease]['new_algorithm'],
                        'Old Accuracy': f"{old_acc:.4f}",
                        'New Accuracy': f"{new_acc:.4f}",
                        'Improvement (%)': f"{improvement:.2f}%"
                    })
            
            if improvements:
                improvement_df = pd.DataFrame(improvements)
                st.dataframe(improvement_df, use_container_width=True)
        
        with tab4:
            st.subheader("🎯 Model Selection Guide")
            
            st.markdown("""
            ### How to Choose the Right Model:
            
            #### 1. **Accuracy Priority**
            - Choose models with highest accuracy scores
            - Consider the confidence intervals
            
            #### 2. **Precision vs Recall Trade-off**
            - **High Precision needed**: When false positives are costly (e.g., unnecessary treatments)
            - **High Recall needed**: When false negatives are dangerous (e.g., missing a disease)
            
            #### 3. **Model Interpretability**
            - **Logistic Regression**: Highly interpretable, good for understanding feature importance
            - **Random Forest**: Moderate interpretability, provides feature importance
            - **SVM**: Less interpretable but often high performance
            - **Gradient Boosting**: Good performance but complex
            
            #### 4. **Computational Resources**
            - Simple models (Logistic Regression) are faster for prediction
            - Complex models (Random Forest, Gradient Boosting) may be slower but more accurate
            
            #### 5. **Data Size Considerations**
            - Small datasets: Simpler models often perform better
            - Large datasets: Complex models can leverage more data effectively
            """)
            
            if all_metrics:
                st.subheader("🏆 Current Best Models by Disease")
                
                best_models = {}
                for disease in diseases:
                    disease_data = metrics_df[metrics_df['disease'] == disease]
                    if not disease_data.empty:
                        best_idx = disease_data['f1_score'].idxmax()
                        best_model = disease_data.loc[best_idx]
                        best_models[disease] = {
                            'Algorithm': best_model['algorithm'],
                            'F1-Score': f"{best_model['f1_score']:.4f}",
                            'Accuracy': f"{best_model['accuracy']:.4f}",
                            'Model Type': best_model['model_type']
                        }
                
                for disease, info in best_models.items():
                    st.success(f"**{disease}**: {info['Algorithm']} ({info['Model Type']}) - F1: {info['F1-Score']}, Acc: {info['Accuracy']}")
    
    else:
        st.error("❌ No model metrics could be loaded. Please check your model files and datasets.")

# Sidebar model version selector for predictions
if selected != 'Model Comparison Dashboard' and selected != 'Comprehensive Health Assessment':
    st.sidebar.subheader("Select Model Version")
    model_version = st.sidebar.selectbox("Choose version:", ["old", "new"])

# ====== Diabetes Prediction ======
if selected == 'Diabetes Prediction':
    st.title('🩺 Diabetes Prediction using ML')
    
    diabetes_model = load_model(model_version, 'diabetes_model.sav')
    if diabetes_model is None:
        st.error("Failed to load diabetes prediction model. Please check the model file.")
        st.stop()
    
    diabetes_scaler = load_scaler(model_version, "diabetes_scaler.sav")
    
    if model_version == "old":
        st.info("📊 Using: LogisticRegression")
    else:
        st.info("🧠 Using: RandomForest")
    
    col1, col2, col3 = st.columns(3)
    with col1: 
        Pregnancies = st.number_input('Number of Pregnancies', min_value=0, max_value=20, value=0)
    with col2: 
        Glucose = st.number_input('Glucose Level', min_value=0, max_value=300, value=100)
    with col3: 
        BloodPressure = st.number_input('Blood Pressure', min_value=0, max_value=200, value=70)
    with col1: 
        SkinThickness = st.number_input('Skin Thickness', min_value=0, max_value=100, value=20)
    with col2: 
        Insulin = st.number_input('Insulin Level', min_value=0, max_value=900, value=80)
    with col3: 
        BMI = st.number_input('BMI', min_value=0.0, max_value=70.0, value=25.0, step=0.1)
    with col1: 
        DiabetesPedigreeFunction = st.number_input('Diabetes Pedigree Function', min_value=0.0, max_value=3.0, value=0.5, step=0.01)
    with col2: 
        Age = st.number_input('Age', min_value=1, max_value=120, value=25)
    
    if st.button('🔍 Get Diabetes Prediction', type="primary"):
        user_input = [[Pregnancies, Glucose, BloodPressure, SkinThickness,
                      Insulin, BMI, DiabetesPedigreeFunction, Age]]
        
        if diabetes_scaler:
            user_input = diabetes_scaler.transform(user_input)
        
        try:
            diab_prediction = diabetes_model.predict(user_input)
            diab_prob = diabetes_model.predict_proba(user_input) if hasattr(diabetes_model, 'predict_proba') else None
            
            if diab_prediction[0] == 1:
                st.error('⚠️ **The person is predicted to be diabetic**')
            else:
                st.success('✅ **The person is predicted to be non-diabetic**')
            
            confidence = None
            if diab_prob is not None:
                confidence = max(diab_prob[0]) * 100
                st.info(f"🎯 **Prediction Confidence:** {confidence:.1f}%")
            
            display_heart_health_impact('Diabetes', diab_prediction[0], confidence)
            
        except Exception as e:
            st.error(f"Error making prediction: {str(e)}")

# ====== Heart Disease Prediction ======
if selected == 'Heart Disease Prediction':
    st.title('❤️ Heart Disease Prediction using ML')
    
    heart_disease_model = load_model(model_version, 'heart_disease_model.sav')
    if heart_disease_model is None:
        st.error("Failed to load heart disease prediction model. Please check the model file.")
        st.stop()
    
    heart_scaler = load_scaler(model_version, "heart_scaler.sav")
    
    if model_version == "old":
        st.info("🌳 Using: DecisionTree")
    else:
        st.info("🗳️ Using: GradientBoosting")
    
    col1, col2, col3 = st.columns(3)
    with col1: age = st.number_input('Age', min_value=1, max_value=120, value=50)
    with col2: sex = st.selectbox('Sex', [0, 1], format_func=lambda x: "Female" if x == 0 else "Male")
    with col3: cp = st.selectbox('Chest Pain Type', [0, 1, 2, 3])
    with col1: trestbps = st.number_input('Resting Blood Pressure', min_value=50, max_value=250, value=120)
    with col2: chol = st.number_input('Cholesterol (mg/dl)', min_value=100, max_value=600, value=200)
    with col3: fbs = st.selectbox('Fasting Blood Sugar > 120 mg/dl', [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
    with col1: restecg = st.selectbox('Resting ECG', [0, 1, 2])
    with col2: thalach = st.number_input('Max Heart Rate', min_value=50, max_value=250, value=150)
    with col3: exang = st.selectbox('Exercise Induced Angina', [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
    with col1: oldpeak = st.number_input('ST Depression', min_value=0.0, max_value=10.0, value=1.0, step=0.1)
    with col2: slope = st.selectbox('ST Slope', [0, 1, 2])
    with col3: ca = st.selectbox('Vessels Colored', [0, 1, 2, 3])
    with col1: thal = st.selectbox('Thalassemia', [0, 1, 2, 3])
    
    if st.button('Get Heart Disease Prediction', type="primary"):
        user_input = [[age, sex, cp, trestbps, chol, fbs, restecg, thalach, 
                      exang, oldpeak, slope, ca, thal]]
        
        if heart_scaler:
            user_input = heart_scaler.transform(user_input)
        
        try:
            heart_prediction = heart_disease_model.predict(user_input)
            heart_prob = heart_disease_model.predict_proba(user_input) if hasattr(heart_disease_model, 'predict_proba') else None
            
            if heart_prediction[0] == 1:
                st.error('⚠️ **The person is predicted to have heart disease**')
            else:
                st.success('✅ **The person is predicted to have no heart disease**')
            
            confidence = None
            if heart_prob is not None:
                confidence = max(heart_prob[0]) * 100
                st.info(f"🎯 **Prediction Confidence:** {confidence:.1f}%")
            
            display_heart_health_impact('Heart Disease', heart_prediction[0], confidence)
            
        except Exception as e:
            st.error(f"Error making prediction: {str(e)}")

# ====== Parkinson's Prediction ======
if selected == "Parkinsons Prediction":
    st.title("🧠 Parkinson's Disease Prediction using ML")
    
    parkinsons_model = load_model(model_version, 'parkinsons_model.sav')
    if parkinsons_model is None:
        st.error("Failed to load Parkinson's prediction model. Please check the model file.")
        st.stop()
    
    parkinsons_scaler = load_scaler(model_version, "parkinsons_scaler.sav")
    
    if model_version == "old":
        st.info("📊 Using: SVM")
    else:
        st.info("🧠 Using: AdaBoost")
    
    st.warning("Note: This prediction requires 22 voice measurement parameters. For demonstration, you can use the default values and modify a few key parameters.")
    
    fo = fhi = flo = Jitter_percent = Jitter_Abs = RAP = PPQ = DDP = Shimmer = Shimmer_dB = None
    APQ3 = APQ5 = APQ = DDA = NHR = HNR = RPDE = DFA = spread1 = spread2 = D2 = PPE = None
    
    with st.expander("Fundamental Frequency Parameters", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1: fo = st.number_input('MDVP:Fo(Hz)', value=119.992, step=0.001, format="%.3f")
        with col2: fhi = st.number_input('MDVP:Fhi(Hz)', value=157.302, step=0.001, format="%.3f")
        with col3: flo = st.number_input('MDVP:Flo(Hz)', value=74.997, step=0.001, format="%.3f")
    
    with st.expander("Jitter Parameters"):
        col1, col2, col3 = st.columns(3)
        with col1: Jitter_percent = st.number_input('MDVP:Jitter(%)', value=0.00784, step=0.00001, format="%.5f")
        with col2: Jitter_Abs = st.number_input('MDVP:Jitter(Abs)', value=0.00007, step=0.000001, format="%.6f")
        with col3: RAP = st.number_input('MDVP:RAP', value=0.00370, step=0.00001, format="%.5f")
        with col1: PPQ = st.number_input('MDVP:PPQ', value=0.00554, step=0.00001, format="%.5f")
        with col2: DDP = st.number_input('Jitter:DDP', value=0.01109, step=0.00001, format="%.5f")
    
    with st.expander("Shimmer Parameters"):
        col1, col2, col3 = st.columns(3)
        with col1: Shimmer = st.number_input('MDVP:Shimmer', value=0.04374, step=0.00001, format="%.5f")
        with col2: Shimmer_dB = st.number_input('MDVP:Shimmer(dB)', value=0.426, step=0.001, format="%.3f")
        with col3: APQ3 = st.number_input('Shimmer:APQ3', value=0.02182, step=0.00001, format="%.5f")
        with col1: APQ5 = st.number_input('Shimmer:APQ5', value=0.03130, step=0.00001, format="%.5f")
        with col2: APQ = st.number_input('MDVP:APQ', value=0.02971, step=0.00001, format="%.5f")
        with col3: DDA = st.number_input('Shimmer:DDA', value=0.06545, step=0.00001, format="%.5f")
    
    with st.expander("Noise and Harmony Parameters"):
        col1, col2 = st.columns(2)
        with col1: NHR = st.number_input('NHR', value=0.02211, step=0.00001, format="%.5f")
        with col2: HNR = st.number_input('HNR', value=21.033, step=0.001, format="%.3f")
    
    with st.expander("Nonlinear Dynamics Parameters"):
        col1, col2, col3, col4 = st.columns(4)
        with col1: RPDE = st.number_input('RPDE', value=0.414783, step=0.000001, format="%.6f")
        with col2: DFA = st.number_input('DFA', value=0.815285, step=0.000001, format="%.6f")
        with col3: spread1 = st.number_input('spread1', value=-4.813031, step=0.000001, format="%.6f")
        with col4: spread2 = st.number_input('spread2', value=0.266482, step=0.000001, format="%.6f")
    
    with st.expander("Additional Parameters"):
        col1, col2, col3 = st.columns(3)
        with col1: D2 = st.number_input('D2', value=2.301442, step=0.000001, format="%.6f")
        with col2: PPE = st.number_input('PPE', value=0.284654, step=0.000001, format="%.6f")
    
    if st.button("Get Parkinson's Prediction", type="primary"):
        user_input = [[
            fo, fhi, flo, Jitter_percent, Jitter_Abs, RAP, PPQ, DDP, 
            Shimmer, Shimmer_dB, APQ3, APQ5, APQ, DDA, NHR, HNR, 
            RPDE, DFA, spread1, spread2, D2, PPE
        ]]
        
        if parkinsons_scaler:
            user_input = parkinsons_scaler.transform(user_input)
        
        try:
            parkinsons_prediction = parkinsons_model.predict(user_input)
            parkinsons_prob = parkinsons_model.predict_proba(user_input) if hasattr(parkinsons_model, 'predict_proba') else None
            
            if parkinsons_prediction[0] == 1:
                st.error("⚠️ **The person is predicted to have Parkinson's disease**")
            else:
                st.success("✅ **The person is predicted to be healthy (No Parkinson's disease)**")
            
            confidence = None
            if parkinsons_prob is not None:
                confidence = max(parkinsons_prob[0]) * 100
                st.info(f"🎯 **Prediction Confidence:** {confidence:.1f}%")
            
            display_heart_health_impact('Parkinsons', parkinsons_prediction[0], confidence)
            
        except Exception as e:
            st.error(f"Error making prediction: {str(e)}")

# ====== STROKE PREDICTION ======
if selected == 'Stroke Prediction':
    st.title('⚡ Stroke Prediction using ML')
    
    stroke_model = load_model(model_version, 'stroke_model.sav')
    if stroke_model is None:
        st.error("Failed to load stroke prediction model. Please check the model file.")
        st.stop()
    
    stroke_preprocessor = load_scaler(model_version, "stroke_preprocessor.sav")
    if stroke_preprocessor is None:
        st.error("Failed to load stroke preprocessor. Please check the preprocessor file.")
        st.stop()
    
    if model_version == "old":
        st.info("📊 Using: LogisticRegression")
    else:
        st.info("🌲 Using: RandomForest")
    
    st.subheader("👤 Personal Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        age = st.number_input('Age', min_value=1, max_value=120, value=50, help="Patient's age in years")
    with col2:
        gender = st.selectbox('Gender', ['Male', 'Female'], help="Patient's gender")
    with col3:
        ever_married = st.selectbox('Ever Married', ['No', 'Yes'], help="Has the patient ever been married?")
    
    st.subheader("🏥 Medical Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        hypertension = st.selectbox('Hypertension', [0, 1], 
                                   format_func=lambda x: "No" if x == 0 else "Yes",
                                   help="Does the patient have hypertension?")
    with col2:
        heart_disease = st.selectbox('Heart Disease', [0, 1], 
                                    format_func=lambda x: "No" if x == 0 else "Yes",
                                    help="Does the patient have heart disease?")
    with col3:
        avg_glucose_level = st.number_input('Average Glucose Level', 
                                           min_value=50.0, max_value=300.0, value=100.0, step=0.1,
                                           help="Average glucose level in blood (mg/dL)")
    
    col1, col2 = st.columns(2)
    with col1:
        bmi = st.number_input('BMI (Body Mass Index)', 
                             min_value=10.0, max_value=50.0, value=25.0, step=0.1,
                             help="Body Mass Index")
    with col2:
        smoking_status = st.selectbox('Smoking Status', 
                                     ['never smoked', 'formerly smoked', 'smokes', 'Unknown'],
                                     help="Patient's smoking status")
    
    st.subheader("💼 Lifestyle Information")
    col1, col2 = st.columns(2)
    
    with col1:
        work_type = st.selectbox('Work Type', 
                                ['Private', 'Self-employed', 'Govt_job', 'children', 'Never_worked'],
                                help="Type of work/employment")
    with col2:
        residence_type = st.selectbox('Residence Type', 
                                     ['Urban', 'Rural'],
                                     help="Type of residence area")
    
    st.subheader("📋 Risk Assessment Information")
    
    risk_factors = []
    if age > 65:
        risk_factors.append("Advanced age (>65)")
    if hypertension == 1:
        risk_factors.append("Hypertension")
    if heart_disease == 1:
        risk_factors.append("Heart disease")
    if avg_glucose_level > 140:
        risk_factors.append("High glucose level")
    if bmi > 30:
        risk_factors.append("Obesity (BMI > 30)")
    if smoking_status == 'smokes':
        risk_factors.append("Current smoker")
    
    if risk_factors:
        st.warning(f"⚠️ **Identified Risk Factors:** {', '.join(risk_factors)}")
    else:
        st.success("✅ **No major risk factors identified**")
    
    if st.button('🔍 Get Stroke Prediction', type="primary"):
        user_data = pd.DataFrame({
            'age': [age],
            'hypertension': [hypertension],
            'heart_disease': [heart_disease],
            'avg_glucose_level': [avg_glucose_level],
            'bmi': [bmi],
            'gender': [gender],
            'ever_married': [ever_married],
            'work_type': [work_type],
            'Residence_type': [residence_type],
            'smoking_status': [smoking_status]
        })
        
        try:
            user_input_processed = stroke_preprocessor.transform(user_data)
            
            stroke_prediction = stroke_model.predict(user_input_processed)
            stroke_prob = stroke_model.predict_proba(user_input_processed) if hasattr(stroke_model, 'predict_proba') else None
            
            col1, col2 = st.columns(2)
            
            with col1:
                if stroke_prediction[0] == 1:
                    st.error('🚨 **HIGH STROKE RISK DETECTED**')
                    st.markdown("""
                    ### ⚠️ Immediate Recommendations:
                    - **Consult with a healthcare professional IMMEDIATELY**
                    - Schedule comprehensive medical evaluation
                    - Monitor blood pressure and glucose levels daily
                    - Consider emergency medical attention if experiencing symptoms
                    """)
                else:
                    st.success('✅ **LOW STROKE RISK**')
                    st.markdown("""
                    ### 🌟 Prevention Tips:
                    - Maintain a healthy lifestyle
                    - Regular health check-ups (annual)
                    - Control blood pressure and glucose levels
                    - Exercise regularly and maintain healthy diet
                    """)
            
            with col2:
                confidence = None
                if stroke_prob is not None:
                    confidence = max(stroke_prob[0]) * 100
                    risk_prob = stroke_prob[0][1] * 100
                    
                    st.metric("Prediction Confidence", f"{confidence:.1f}%")
                    st.metric("Stroke Risk Probability", f"{risk_prob:.2f}%")
                    
                    if risk_prob < 10:
                        risk_level = "Very Low"
                        risk_color = "green"
                    elif risk_prob < 25:
                        risk_level = "Low"
                        risk_color = "lightgreen"
                    elif risk_prob < 50:
                        risk_level = "Moderate"
                        risk_color = "orange"
                    elif risk_prob < 75:
                        risk_level = "High"
                        risk_color = "red"
                    else:
                        risk_level = "Very High"
                        risk_color = "darkred"
                    
                    st.markdown(f"**Risk Level:** <span style='color:{risk_color}'>{risk_level}</span>", unsafe_allow_html=True)
            
            st.subheader("🧠 Understanding Stroke Risk")
            st.markdown("""
            **Common Stroke Warning Signs (FAST):**
            - **F**ace drooping
            - **A**rm weakness
            - **S**peech difficulty
            - **T**ime to call emergency services
            
            **Controllable Risk Factors:**
            - High blood pressure
            - High cholesterol
            - Diabetes
            - Smoking
            - Obesity
            - Physical inactivity
            
            **Note:** This prediction is for educational purposes only and should not replace professional medical advice.
            """)
            
            display_heart_health_impact('Stroke', stroke_prediction[0], confidence)
                
        except Exception as e:
            st.error(f"Error making prediction: {str(e)}")
            st.error("Please ensure all fields are filled correctly.")
            
    st.markdown("---")
    st.markdown("""
    **⚠️ Medical Disclaimer:** This application is for educational and informational purposes only. 
    It is not intended as a substitute for professional medical advice, diagnosis, or treatment. 
    Always seek the advice of your physician or other qualified healthcare provider with any questions 
    you may have regarding a medical condition.
    """)

# ====== COMPREHENSIVE HEALTH ASSESSMENT ======
if selected == 'Comprehensive Health Assessment':
    st.title('🏥 Comprehensive Health Assessment')
    st.markdown("""
    ### Complete Health Screening
    This comprehensive assessment evaluates your risk across multiple health conditions and provides
    an overall cardiovascular health score.
    """)
    
    # Model version selector
    st.sidebar.subheader("Select Model Version")
    model_version = st.sidebar.selectbox("Choose version:", ["old", "new"], key="comprehensive_model_version")
    
    # Create tabs for different input sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👤 Demographics & Vitals", 
        "🩺 Diabetes Screening", 
        "❤️ Cardiac Screening", 
        "⚡ Stroke Risk Factors",
        "📊 Results & Analysis"
    ])
    
    # Store all inputs in session state
    if 'comprehensive_data' not in st.session_state:
        st.session_state.comprehensive_data = {}
    
    with tab1:
        st.subheader("Demographics and Vital Signs")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            comp_age = st.number_input('Age', min_value=1, max_value=120, value=50, key='comp_age')
            comp_gender = st.selectbox('Gender', ['Male', 'Female'], key='comp_gender')
            comp_height = st.number_input('Height (cm)', min_value=100, max_value=250, value=170, key='comp_height')
        
        with col2:
            comp_weight = st.number_input('Weight (kg)', min_value=30, max_value=200, value=70, key='comp_weight')
            comp_bmi = comp_weight / ((comp_height/100) ** 2)
            st.metric("Calculated BMI", f"{comp_bmi:.2f}")
            comp_bp = st.number_input('Blood Pressure (Systolic)', min_value=80, max_value=200, value=120, key='comp_bp')
        
        with col3:
            comp_glucose = st.number_input('Average Glucose Level', min_value=50.0, max_value=300.0, value=100.0, key='comp_glucose')
            comp_cholesterol = st.number_input('Cholesterol (mg/dl)', min_value=100, max_value=600, value=200, key='comp_chol')
            comp_heart_rate = st.number_input('Resting Heart Rate', min_value=40, max_value=150, value=72, key='comp_hr')
        
        st.session_state.comprehensive_data.update({
            'age': comp_age,
            'gender': comp_gender,
            'bmi': comp_bmi,
            'blood_pressure': comp_bp,
            'glucose': comp_glucose,
            'cholesterol': comp_cholesterol,
            'heart_rate': comp_heart_rate
        })
    
    with tab2:
        st.subheader("Diabetes Risk Factors")
        col1, col2 = st.columns(2)
        
        with col1:
            comp_pregnancies = st.number_input('Number of Pregnancies (if applicable)', min_value=0, max_value=20, value=0, key='comp_preg')
            comp_skin_thickness = st.number_input('Skin Thickness (mm)', min_value=0, max_value=100, value=20, key='comp_skin')
            comp_insulin = st.number_input('Insulin Level', min_value=0, max_value=900, value=80, key='comp_insulin')
        
        with col2:
            comp_dpf = st.number_input('Diabetes Pedigree Function', min_value=0.0, max_value=3.0, value=0.5, step=0.01, key='comp_dpf')
            comp_family_diabetes = st.selectbox('Family History of Diabetes', ['No', 'Yes'], key='comp_fam_diabetes')
        
        st.session_state.comprehensive_data.update({
            'pregnancies': comp_pregnancies,
            'skin_thickness': comp_skin_thickness,
            'insulin': comp_insulin,
            'diabetes_pedigree': comp_dpf,
            'family_diabetes': comp_family_diabetes
        })
    
    with tab3:
        st.subheader("Cardiac Risk Factors")
        col1, col2 = st.columns(2)
        
        with col1:
            comp_chest_pain = st.selectbox('Chest Pain Type', [0, 1, 2, 3], 
                                          format_func=lambda x: ['No Pain', 'Typical Angina', 'Atypical Angina', 'Non-anginal'][x],
                                          key='comp_cp')
            comp_fbs = st.selectbox('Fasting Blood Sugar > 120', ['No', 'Yes'], key='comp_fbs')
            comp_restecg = st.selectbox('Resting ECG', [0, 1, 2],
                                       format_func=lambda x: ['Normal', 'ST-T Abnormality', 'LV Hypertrophy'][x],
                                       key='comp_ecg')
        
        with col2:
            comp_max_hr = st.number_input('Maximum Heart Rate Achieved', min_value=60, max_value=220, value=150, key='comp_max_hr')
            comp_exang = st.selectbox('Exercise Induced Angina', ['No', 'Yes'], key='comp_exang')
            comp_oldpeak = st.number_input('ST Depression', min_value=0.0, max_value=10.0, value=1.0, step=0.1, key='comp_oldpeak')
        
        col1, col2 = st.columns(2)
        with col1:
            comp_slope = st.selectbox('Slope of Peak Exercise ST', [0, 1, 2],
                                     format_func=lambda x: ['Upsloping', 'Flat', 'Downsloping'][x],
                                     key='comp_slope')
            comp_ca = st.selectbox('Major Vessels Colored by Fluoroscopy', [0, 1, 2, 3], key='comp_ca')
        
        with col2:
            comp_thal = st.selectbox('Thalassemia', [0, 1, 2, 3],
                                    format_func=lambda x: ['Normal', 'Fixed Defect', 'Reversible Defect', 'Unknown'][x],
                                    key='comp_thal')
        
        st.session_state.comprehensive_data.update({
            'chest_pain': comp_chest_pain,
            'fasting_blood_sugar': 1 if comp_fbs == 'Yes' else 0,
            'rest_ecg': comp_restecg,
            'max_heart_rate': comp_max_hr,
            'exercise_angina': 1 if comp_exang == 'Yes' else 0,
            'oldpeak': comp_oldpeak,
            'slope': comp_slope,
            'ca': comp_ca,
            'thal': comp_thal
        })
    
    with tab4:
        st.subheader("Stroke and Lifestyle Risk Factors")
        col1, col2 = st.columns(2)
        
        with col1:
            comp_hypertension = st.selectbox('Hypertension', ['No', 'Yes'], key='comp_hyper')
            comp_heart_disease = st.selectbox('Heart Disease History', ['No', 'Yes'], key='comp_hd')
            comp_smoking = st.selectbox('Smoking Status', 
                                       ['never smoked', 'formerly smoked', 'smokes', 'Unknown'],
                                       key='comp_smoke')
        
        with col2:
            comp_married = st.selectbox('Ever Married', ['No', 'Yes'], key='comp_married')
            comp_work = st.selectbox('Work Type',
                                    ['Private', 'Self-employed', 'Govt_job', 'children', 'Never_worked'],
                                    key='comp_work')
            comp_residence = st.selectbox('Residence Type', ['Urban', 'Rural'], key='comp_residence')
        
        st.session_state.comprehensive_data.update({
            'hypertension': 1 if comp_hypertension == 'Yes' else 0,
            'heart_disease_history': 1 if comp_heart_disease == 'Yes' else 0,
            'smoking_status': comp_smoking,
            'ever_married': comp_married,
            'work_type': comp_work,
            'residence_type': comp_residence
        })
    
    with tab5:
        st.subheader("Comprehensive Health Analysis")
        
        if st.button('🔍 Run Complete Health Assessment', type='primary', key='comp_assess'):
            with st.spinner('Analyzing your health data...'):
                predictions = {}
                
                # Diabetes Prediction
                try:
                    diabetes_model = load_model(model_version, 'diabetes_model.sav')
                    diabetes_scaler = load_scaler(model_version, "diabetes_scaler.sav")
                    
                    if diabetes_model:
                        diabetes_input = [[
                            st.session_state.comprehensive_data['pregnancies'],
                            st.session_state.comprehensive_data['glucose'],
                            st.session_state.comprehensive_data['blood_pressure'],
                            st.session_state.comprehensive_data['skin_thickness'],
                            st.session_state.comprehensive_data['insulin'],
                            st.session_state.comprehensive_data['bmi'],
                            st.session_state.comprehensive_data['diabetes_pedigree'],
                            st.session_state.comprehensive_data['age']
                        ]]
                        
                        if diabetes_scaler:
                            diabetes_input = diabetes_scaler.transform(diabetes_input)
                        
                        diab_pred = diabetes_model.predict(diabetes_input)
                        diab_prob = diabetes_model.predict_proba(diabetes_input) if hasattr(diabetes_model, 'predict_proba') else None
                        
                        predictions['diabetes'] = {
                            'prediction': int(diab_pred[0]),
                            'confidence': max(diab_prob[0]) * 100 if diab_prob is not None else 50.0
                        }
                except Exception as e:
                    st.warning(f"Could not complete diabetes prediction: {str(e)}")
                
                # Heart Disease Prediction
                try:
                    heart_model = load_model(model_version, 'heart_disease_model.sav')
                    heart_scaler = load_scaler(model_version, "heart_scaler.sav")
                    
                    if heart_model:
                        heart_input = [[
                            st.session_state.comprehensive_data['age'],
                            1 if st.session_state.comprehensive_data['gender'] == 'Male' else 0,
                            st.session_state.comprehensive_data['chest_pain'],
                            st.session_state.comprehensive_data['blood_pressure'],
                            st.session_state.comprehensive_data['cholesterol'],
                            st.session_state.comprehensive_data['fasting_blood_sugar'],
                            st.session_state.comprehensive_data['rest_ecg'],
                            st.session_state.comprehensive_data['max_heart_rate'],
                            st.session_state.comprehensive_data['exercise_angina'],
                            st.session_state.comprehensive_data['oldpeak'],
                            st.session_state.comprehensive_data['slope'],
                            st.session_state.comprehensive_data['ca'],
                            st.session_state.comprehensive_data['thal']
                        ]]
                        
                        if heart_scaler:
                            heart_input = heart_scaler.transform(heart_input)
                        
                        heart_pred = heart_model.predict(heart_input)
                        heart_prob = heart_model.predict_proba(heart_input) if hasattr(heart_model, 'predict_proba') else None
                        
                        predictions['heart_disease'] = {
                            'prediction': int(heart_pred[0]),
                            'confidence': max(heart_prob[0]) * 100 if heart_prob is not None else 50.0
                        }
                except Exception as e:
                    st.warning(f"Could not complete heart disease prediction: {str(e)}")
                
                # Stroke Prediction
                try:
                    stroke_model = load_model(model_version, 'stroke_model.sav')
                    stroke_preprocessor = load_scaler(model_version, "stroke_preprocessor.sav")
                    
                    if stroke_model and stroke_preprocessor:
                        stroke_data = pd.DataFrame({
                            'age': [st.session_state.comprehensive_data['age']],
                            'hypertension': [st.session_state.comprehensive_data['hypertension']],
                            'heart_disease': [st.session_state.comprehensive_data['heart_disease_history']],
                            'avg_glucose_level': [st.session_state.comprehensive_data['glucose']],
                            'bmi': [st.session_state.comprehensive_data['bmi']],
                            'gender': [st.session_state.comprehensive_data['gender']],
                            'ever_married': [st.session_state.comprehensive_data['ever_married']],
                            'work_type': [st.session_state.comprehensive_data['work_type']],
                            'Residence_type': [st.session_state.comprehensive_data['residence_type']],
                            'smoking_status': [st.session_state.comprehensive_data['smoking_status']]
                        })
                        
                        stroke_input = stroke_preprocessor.transform(stroke_data)
                        stroke_pred = stroke_model.predict(stroke_input)
                        stroke_prob = stroke_model.predict_proba(stroke_input) if hasattr(stroke_model, 'predict_proba') else None
                        
                        predictions['stroke'] = {
                            'prediction': int(stroke_pred[0]),
                            'confidence': max(stroke_prob[0]) * 100 if stroke_prob is not None else 50.0
                        }
                except Exception as e:
                    st.warning(f"Could not complete stroke prediction: {str(e)}")
                
                # Display comprehensive results
                if predictions:
                    st.success("✅ Health assessment completed!")
                    
                    # Calculate cardiovascular risk
                    cv_risk_score, risk_factors = calculate_cardiovascular_risk(predictions)
                    
                    # Display overall risk score
                    st.markdown("---")
                    st.subheader("🎯 Overall Cardiovascular Risk Assessment")
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col1:
                        st.metric("Overall CV Risk Score", f"{cv_risk_score}/100")
                        
                        if cv_risk_score < 25:
                            risk_category = "LOW RISK"
                            risk_color = "green"
                        elif cv_risk_score < 50:
                            risk_category = "MODERATE RISK"
                            risk_color = "orange"
                        elif cv_risk_score < 75:
                            risk_category = "HIGH RISK"
                            risk_color = "red"
                        else:
                            risk_category = "CRITICAL RISK"
                            risk_color = "darkred"
                        
                        st.markdown(f"<h3 style='color:{risk_color}'>{risk_category}</h3>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("**Contributing Risk Factors:**")
                        if risk_factors:
                            for factor in risk_factors:
                                st.markdown(f"- {factor}")
                        else:
                            st.markdown("✅ No major risk factors detected")
                    
                    with col3:
                        if cv_risk_score >= 50:
                            st.error("⚠️ Immediate medical consultation recommended")
                        elif cv_risk_score >= 25:
                            st.warning("⚡ Schedule health checkup soon")
                        else:
                            st.success("✅ Continue preventive care")
                    
                    # Display comprehensive health chart
                    st.markdown("---")
                    st.subheader("📊 Individual Condition Risk Profile")
                    
                    health_chart = create_comprehensive_health_chart(predictions)
                    st.plotly_chart(health_chart, use_container_width=True)
                    
                    # Detailed results for each condition
                    st.markdown("---")
                    st.subheader("🔍 Detailed Results by Condition")
                    
                    result_col1, result_col2 = st.columns(2)
                    
                    with result_col1:
                        if 'diabetes' in predictions:
                            with st.expander("🩺 Diabetes Assessment", expanded=True):
                                pred = predictions['diabetes']
                                if pred['prediction'] == 1:
                                    st.error("⚠️ **Diabetes Risk Detected**")
                                else:
                                    st.success("✅ **No Diabetes Risk**")
                                st.metric("Confidence", f"{pred['confidence']:.1f}%")
                        
                        if 'stroke' in predictions:
                            with st.expander("⚡ Stroke Risk Assessment", expanded=True):
                                pred = predictions['stroke']
                                if pred['prediction'] == 1:
                                    st.error("⚠️ **Stroke Risk Detected**")
                                else:
                                    st.success("✅ **Low Stroke Risk**")
                                st.metric("Confidence", f"{pred['confidence']:.1f}%")
                    
                    with result_col2:
                        if 'heart_disease' in predictions:
                            with st.expander("❤️ Heart Disease Assessment", expanded=True):
                                pred = predictions['heart_disease']
                                if pred['prediction'] == 1:
                                    st.error("⚠️ **Heart Disease Risk Detected**")
                                else:
                                    st.success("✅ **No Heart Disease Risk**")
                                st.metric("Confidence", f"{pred['confidence']:.1f}%")
                    
                    # Recommendations
                    st.markdown("---")
                    st.subheader("📋 Personalized Health Recommendations")
                    
                    recommendations = []
                    
                    if cv_risk_score >= 50:
                        recommendations.append("🚨 **URGENT**: Schedule immediate appointment with healthcare provider")
                        recommendations.append("📊 Request comprehensive cardiovascular evaluation")
                    
                    if predictions.get('diabetes', {}).get('prediction') == 1:
                        recommendations.append("🩸 Monitor blood glucose levels daily")
                        recommendations.append("🥗 Follow diabetic diet plan")
                        recommendations.append("💊 Consult endocrinologist for diabetes management")
                    
                    if predictions.get('heart_disease', {}).get('prediction') == 1:
                        recommendations.append("❤️ Schedule cardiology consultation")
                        recommendations.append("🏃 Start cardiac rehabilitation program")
                        recommendations.append("💊 Review current medications with doctor")
                    
                    if predictions.get('stroke', {}).get('prediction') == 1:
                        recommendations.append("🧠 Consult neurologist for stroke prevention")
                        recommendations.append("💊 Consider antiplatelet therapy (consult doctor)")
                        recommendations.append("📊 Regular blood pressure monitoring")
                    
                    # General recommendations
                    recommendations.append("🏃 Regular physical activity (30 min/day, 5 days/week)")
                    recommendations.append("🥗 Maintain healthy diet (low sodium, high fiber)")
                    recommendations.append("🚭 Avoid smoking and limit alcohol")
                    recommendations.append("😴 Ensure adequate sleep (7-8 hours)")
                    recommendations.append("📊 Annual health screenings")
                    
                    for rec in recommendations:
                        st.markdown(rec)
                    
                    # Medical disclaimer
                    st.markdown("---")
                    st.warning("""
                    **⚠️ IMPORTANT MEDICAL DISCLAIMER:**
                    
                    This comprehensive health assessment is for **educational and informational purposes only**. 
                    It should NOT be used as a substitute for professional medical advice, diagnosis, or treatment.
                    
                    - Always consult qualified healthcare providers for medical decisions
                    - Seek immediate medical attention if experiencing symptoms
                    - Regular medical checkups are essential regardless of predictions
                    - This tool uses AI/ML models which may have limitations
                    """)
                    
                else:
                    st.error("❌ Unable to complete health assessment. Please try again or check model files.")
                    
        else:
            st.info("👆 Click the button above to run your complete health assessment")
            st.markdown("""
            ### What this assessment includes:
            - 🩺 Diabetes risk evaluation
            - ❤️ Heart disease risk analysis
            - ⚡ Stroke risk assessment
            - 💓 Overall cardiovascular health score
            - 📋 Personalized health recommendations
            
            **Please fill in all the information in the previous tabs before running the assessment.**
            """)