import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Skeleton, { SkeletonTheme } from 'react-loading-skeleton';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import ModelSelector from './ModelSelector';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const API_URL = "http://127.0.0.1:8000";

// Define initial state for the comprehensive form
const initialFormState = {
    // Demographics
    age: 50, gender: 'Male', bmi: 25.0,
    // Vitals
    blood_pressure: 120, glucose: 100, cholesterol: 200, max_heart_rate: 150,
    // Diabetes
    pregnancies: 0, skin_thickness: 20, insulin: 80, diabetes_pedigree: 0.5,
    // Heart
    chest_pain: 0, fasting_blood_sugar: 0, rest_ecg: 0, exercise_angina: 0,
    oldpeak: 1.0, slope: 0, ca: 0, thal: 0,
    // Stroke
    hypertension: 0, heart_disease_history: 0, ever_married: 'No',
    work_type: 'Private', residence_type: 'Urban', smoking_status: 'never smoked',
};

function ComprehensiveAssessment() {
    const [formData, setFormData] = useState(initialFormState);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [modelMetadata, setModelMetadata] = useState({});
    const [selectedModel, setSelectedModel] = useState('new');
    const [activeTab, setActiveTab] = useState('vitals');

    useEffect(() => {
        axios.get(`${API_URL}/models-metadata`)
            .then(response => { if (response.data) setModelMetadata(response.data); })
            .catch(error => console.error("Failed to fetch model metadata:", error));
    }, []);

    const handleChange = (e) => {
        const { name, value, type } = e.target;
        let finalValue = type === 'number' ? parseFloat(value) : value;
        // Handle select-as-number
        if (name === 'hypertension' || name === 'heart_disease_history' || name === 'fasting_blood_sugar' || name === 'exercise_angina' || name === 'sex' || name === 'cp' || name === 'rest_ecg' || name === 'slope' || name === 'ca' || name === 'thal') {
            finalValue = parseInt(value, 10);
        }
        setFormData(prev => ({ ...prev, [name]: finalValue }));
    };

    const handleReset = () => {
        setFormData(initialFormState);
        setResult(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setResult(null);
        try {
            const requestBody = {
                model_version: selectedModel,
                form_data: formData,
            };
            const response = await axios.post(`${API_URL}/predict/comprehensive`, requestBody);
            setResult(response.data);
        } catch (err) {
            console.error(err);
            setResult(null); // Or some error state
        } finally {
            setLoading(false);
        }
    };

    const getRiskColor = (score) => {
        if (score < 25) return 'var(--positive-text)';
        if (score < 50) return 'orange';
        if (score < 75) return 'var(--error-color)';
        return '#dc3545'; // darkred
    };

    // Chart Data
    const chartData = {
        labels: result ? Object.keys(result.individual_predictions) : [],
        datasets: [
          {
            label: 'Risk Confidence',
            data: result ? Object.values(result.individual_predictions).map(pred => (pred ? pred.confidence : 0)) : [],
            backgroundColor: result ? Object.values(result.individual_predictions).map(pred => (pred && pred.prediction === 1 ? 'var(--negative-bg)' : 'var(--positive-bg)')) : [],
            borderColor: result ? Object.values(result.individual_predictions).map(pred => (pred && pred.prediction === 1 ? 'var(--negative-text)' : 'var(--positive-text)')) : [],
            borderWidth: 1,
          },
        ],
      };

    return (
        <section id="comprehensive" className="section">
            <h2 className="section-title">Comprehensive Health Assessment</h2>
            <p className="section-subtitle">
                Fill in all fields to receive a complete cardiovascular risk profile based on multiple AI models.
            </p>
            <div className="prediction-layout">
                {/* --- Left Column: Model Selector --- */}
                <ModelSelector
                    metadata={modelMetadata}
                    selected={selectedModel}
                    onSelect={setSelectedModel}
                    diseaseName="Diabetes" // Use any disease as a proxy
                />

                {/* --- Middle Column: Form --- */}
                <SkeletonTheme baseColor="var(--border-color)" highlightColor="var(--bg-color)">
                    <form onSubmit={handleSubmit} className="prediction-form">
                        <div className="comp-tabs">
                            <button type="button" className={`tab ${activeTab === 'vitals' ? 'active' : ''}`} onClick={() => setActiveTab('vitals')}>Vitals</button>
                            <button type="button" className={`tab ${activeTab === 'diabetes' ? 'active' : ''}`} onClick={() => setActiveTab('diabetes')}>Diabetes</button>
                            <button type="button" className={`tab ${activeTab === 'cardiac' ? 'active' : ''}`} onClick={() => setActiveTab('cardiac')}>Cardiac</button>
                            <button type="button" className={`tab ${activeTab === 'stroke' ? 'active' : ''}`} onClick={() => setActiveTab('Lifestyle')}>Lifestyle</button>
                        </div>
                        
                        {loading ? <Skeleton count={6} height={48} style={{marginTop: '10px'}}/> : (
                        <>
                            {activeTab === 'vitals' && (
                                <div className="form-grid">
                                    <div className="form-group"><label>Age</label><input type="number" name="age" value={formData.age} onChange={handleChange}/></div>
                                    <div className="form-group"><label>Gender</label><select name="gender" value={formData.gender} onChange={handleChange}><option>Male</option><option>Female</option></select></div>
                                    <div className="form-group"><label>BMI</label><input type="number" step="0.1" name="bmi" value={formData.bmi} onChange={handleChange}/></div>
                                    <div className="form-group"><label>Blood Pressure (Systolic)</label><input type="number" name="blood_pressure" value={formData.blood_pressure} onChange={handleChange}/></div>
                                    <div className="form-group"><label>Average Glucose Level</label><input type="number" step="0.1" name="glucose" value={formData.glucose} onChange={handleChange}/></div>
                                    <div className="form-group"><label>Cholesterol (mg/dl)</label><input type="number" name="cholesterol" value={formData.cholesterol} onChange={handleChange}/></div>
                                </div>
                            )}
                            {activeTab === 'diabetes' && (
                                <div className="form-grid">
                                    <div className="form-group"><label>Pregnancies</label><input type="number" name="pregnancies" value={formData.pregnancies} onChange={handleChange}/></div>
                                    <div className="form-group"><label>Skin Thickness (mm)</label><input type="number" name="skin_thickness" value={formData.skin_thickness} onChange={handleChange}/></div>
                                    <div className="form-group"><label>Insulin Level</label><input type="number" name="insulin" value={formData.insulin} onChange={handleChange}/></div>
                                    <div className="form-group"><label>Diabetes Pedigree Fn</label><input type="number" step="0.01" name="diabetes_pedigree" value={formData.diabetes_pedigree} onChange={handleChange}/></div>
                                </div>
                            )}
                            {activeTab === 'cardiac' && (
                                <div className="form-grid">
                                    <div className="form-group"><label>Chest Pain Type</label><select name="chest_pain" value={formData.chest_pain} onChange={handleChange}><option value={0}>No Pain</option><option value={1}>Typical</option><option value={2}>Atypical</option><option value={3}>Non-anginal</option></select></div>
                                    <div className="form-group"><label>Fasting Blood Sugar > 120</label><select name="fasting_blood_sugar" value={formData.fasting_blood_sugar} onChange={handleChange}><option value={0}>No</option><option value={1}>Yes</option></select></div>
                                    <div className="form-group"><label>Resting ECG</label><select name="rest_ecg" value={formData.rest_ecg} onChange={handleChange}><option value={0}>Normal</option><option value={1}>ST-T Abnormality</option><option value={2}>LV Hypertrophy</option></select></div>
                                    <div className="form-group"><label>Max Heart Rate</label><input type="number" name="max_heart_rate" value={formData.max_heart_rate} onChange={handleChange}/></div>
                                    <div className="form-group"><label>Exercise Angina</label><select name="exercise_angina" value={formData.exercise_angina} onChange={handleChange}><option value={0}>No</option><option value={1}>Yes</option></select></div>
                                    <div className="form-group"><label>ST Depression (Oldpeak)</label><input type="number" step="0.1" name="oldpeak" value={formData.oldpeak} onChange={handleChange}/></div>
                                    <div className="form-group"><label>Slope of ST Segment</label><select name="slope" value={formData.slope} onChange={handleChange}><option value={0}>Upsloping</option><option value={1}>Flat</option><option value={2}>Downsloping</option></select></div>
                                    <div className="form-group"><label>Major Vessels Colored</label><select name="ca" value={formData.ca} onChange={handleChange}><option value={0}>0</option><option value={1}>1</option><option value={2}>2</option><option value={3}>3</option></select></div>
                                    <div className="form-group"><label>Thalassemia</label><select name="thal" value={formData.thal} onChange={handleChange}><option value={0}>Normal</option><option value={1}>Fixed</option><option value={2}>Reversible</option><option value={3}>Unknown</option></select></div>
                                </div>
                            )}
                            {activeTab === 'stroke' && (
                                <div className="form-grid">
                                    <div className="form-group"><label>Hypertension</label><select name="hypertension" value={formData.hypertension} onChange={handleChange}><option value={0}>No</option><option value={1}>Yes</option></select></div>
                                    <div className="form-group"><label>Heart Disease History</label><select name="heart_disease_history" value={formData.heart_disease_history} onChange={handleChange}><option value={0}>No</option><option value={1}>Yes</option></select></div>
                                    <div className="form-group"><label>Ever Married</label><select name="ever_married" value={formData.ever_married} onChange={handleChange}><option>Yes</option><option>No</option></select></div>
                                    <div className="form-group"><label>Work Type</label><select name="work_type" value={formData.work_type} onChange={handleChange}><option>Private</option><option>Self-employed</option><option>Govt_job</option><option>children</option><option>Never_worked</option></select></div>
                                    <div className="form-group"><label>Residence Type</label><select name="residence_type" value={formData.residence_type} onChange={handleChange}><option>Urban</option><option>Rural</option></select></div>
                                    <div className="form-group"><label>Smoking Status</label><select name="smoking_status" value={formData.smoking_status} onChange={handleChange}><option>formerly smoked</option><option>never smoked</option><option>smokes</option><option>Unknown</option></select></div>
                                </div>
                            )}
                        </>
                        )}
                        
                        <div className="form-buttons">
                            <button type="button" className="reset-button" onClick={handleReset}>Reset</button>
                            <button type="submit" className="submit-button" disabled={loading}>
                                {loading ? 'Analyzing...' : 'Run Full Assessment'}
                            </button>
                        </div>
                    </form>
                </SkeletonTheme>

                {/* --- Right Column: Comprehensive Results --- */}
                <div className="output-panel">
                    {loading ? (
                        <div className="output-placeholder"><p>Analyzing all metrics...</p></div>
                    ) : result ? (
                        <div className="result">
                            <h3 className="comp-result-title">Overall Cardiovascular Risk</h3>
                            <h1 className="comp-result-score" style={{color: getRiskColor(result.cardiovascular_risk.score)}}>
                                {result.cardiovascular_risk.score}/100
                            </h1>
                            <div className="comp-risk-factors">
                                <strong>Contributing Factors:</strong>
                                <ul>
                                    {result.cardiovascular_risk.factors.length > 0 ?
                                        result.cardiovascular_risk.factors.map(factor => <li key={factor}>{factor}</li>) :
                                        <li>No Major Risk Factors Detected</li>
                                    }
                                </ul>
                            </div>
                            <div className="comp-chart-container">
                                <Bar data={chartData} options={{ indexAxis: 'y', responsive: true, plugins: { legend: { display: false } } }} />
                            </div>
                        </div>
                    ) : (
                         <div className="output-placeholder">
                            <p>Your comprehensive results will appear here.</p>
                        </div>
                    )}
                </div>
            </div>
        </section>
    );
}

export default ComprehensiveAssessment;