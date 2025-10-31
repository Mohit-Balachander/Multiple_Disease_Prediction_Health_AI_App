import React, { useState, useEffect } from "react";
import axios from "axios";
import { FiHelpCircle } from "react-icons/fi";
import Skeleton, { SkeletonTheme } from "react-loading-skeleton";
import { Tooltip } from "react-tooltip";
import ModelSelector from "./ModelSelector";
import OutputPanel from "./OutputPanel";

const API_URL = "http://127.0.0.1:8000";
const initialFormState = {
  age: "63",
  sex: "1",
  cp: "3",
  trestbps: "145",
  chol: "233",
  fbs: "1",
  restecg: "0",
  thalach: "150",
  exang: "0",
  oldpeak: "2.3",
  slope: "0",
  ca: "0",
  thal: "1",
};

function Heart() {
  const [formData, setFormData] = useState(initialFormState);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [modelMetadata, setModelMetadata] = useState({}); // Initialize as empty object
  const [selectedModel, setSelectedModel] = useState("new");

  useEffect(() => {
    axios
      .get(`${API_URL}/models-metadata`)
      .then((response) => {
        if (response.data) {
          setModelMetadata(response.data);
        }
      })
      .catch((error) =>
        console.error("Failed to fetch model metadata:", error)
      );
  }, []);

  const validateField = (name, value) => {
    if (value === "" || isNaN(value) || value < 0) {
      return `This field must be a non-negative number.`;
    }
    return "";
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    const error = validateField(name, value);
    setErrors((prev) => ({ ...prev, [name]: error }));
  };

  const handleReset = () => {
    setFormData(initialFormState);
    setResult(null);
    setErrors({});
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newErrors = {};
    let hasError = false;
    const parsedFormData = {};
    Object.keys(formData).forEach((key) => {
      const value = formData[key];
      const error = validateField(key, value);
      if (error) {
        newErrors[key] = error;
        hasError = true;
      } else {
        parsedFormData[key] = parseFloat(value);
      }
    });
    setErrors(newErrors);
    if (hasError) return;

    setLoading(true);
    setResult(null);
    try {
      const requestBody = {
        model_version: selectedModel,
        form_data: parsedFormData,
      };
      const response = await axios.post(
        `${API_URL}/predict/heart`,
        requestBody
      );
      setResult(response.data);
    } catch (err) {
      setResult({ prediction: -1, result_message: "An error occurred." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <section id="heart" className="section">
      <h2 className="section-title">Heart Disease Prediction</h2>
      <div className="prediction-layout">
        <ModelSelector
          metadata={modelMetadata}
          selected={selectedModel}
          onSelect={setSelectedModel}
          diseaseName="Heart"
        />
        <SkeletonTheme
          baseColor="var(--border-color)"
          highlightColor="var(--bg-color)"
        >
          <form onSubmit={handleSubmit} className="prediction-form">
            <div className="form-grid">
              <div className="form-group">
                <div className="form-group-label">
                  <label>Age</label>
                </div>
                {loading ? (
                  <Skeleton height={48} />
                ) : (
                  <input
                    type="number"
                    name="age"
                    value={formData.age}
                    onChange={handleChange}
                    className={errors.age ? "input-error" : ""}
                  />
                )}
                {errors.age && <p className="error-message">{errors.age}</p>}
              </div>
              <div className="form-group">
                <div className="form-group-label">
                  <label>Sex</label>
                </div>
                {loading ? (
                  <Skeleton height={48} />
                ) : (
                  <select
                    name="sex"
                    value={formData.sex}
                    onChange={handleChange}
                  >
                    <option value={1}>Male</option>
                    <option value={0}>Female</option>
                  </select>
                )}
              </div>
              <div className="form-group">
                <div className="form-group-label">
                  <label>Chest Pain Type</label>
                  <FiHelpCircle
                    className="tooltip-icon"
                    data-tooltip-id="cp-tooltip"
                    data-tooltip-content="0: Typical Angina, 1: Atypical Angina, 2: Non-anginal Pain, 3: Asymptomatic"
                  />
                </div>
                {loading ? (
                  <Skeleton height={48} />
                ) : (
                  <input
                    type="number"
                    name="cp"
                    value={formData.cp}
                    onChange={handleChange}
                    className={errors.cp ? "input-error" : ""}
                  />
                )}
                {errors.cp && <p className="error-message">{errors.cp}</p>}
              </div>
              <div className="form-group">
                <div className="form-group-label">
                  <label>Resting Blood Pressure</label>
                </div>
                {loading ? (
                  <Skeleton height={48} />
                ) : (
                  <input
                    type="number"
                    name="trestbps"
                    value={formData.trestbps}
                    onChange={handleChange}
                    className={errors.trestbps ? "input-error" : ""}
                  />
                )}
                {errors.trestbps && (
                  <p className="error-message">{errors.trestbps}</p>
                )}
              </div>
              <div className="form-group">
                <div className="form-group-label">
                  <label>Cholesterol (mg/dl)</label>
                </div>
                {loading ? (
                  <Skeleton height={48} />
                ) : (
                  <input
                    type="number"
                    name="chol"
                    value={formData.chol}
                    onChange={handleChange}
                    className={errors.chol ? "input-error" : ""}
                  />
                )}
                {errors.chol && <p className="error-message">{errors.chol}</p>}
              </div>
              <div className="form-group">
                <div className="form-group-label">
                  <label>Fasting Blood Sugar > 120 mg/dl</label>
                </div>
                {loading ? (
                  <Skeleton height={48} />
                ) : (
                  <select
                    name="fbs"
                    value={formData.fbs}
                    onChange={handleChange}
                  >
                    <option value={1}>Yes</option>
                    <option value={0}>No</option>
                  </select>
                )}
              </div>
              <div className="form-group">
                <div className="form-group-label">
                  <label>Resting ECG</label>
                </div>
                {loading ? (
                  <Skeleton height={48} />
                ) : (
                  <input
                    type="number"
                    name="restecg"
                    value={formData.restecg}
                    onChange={handleChange}
                    className={errors.restecg ? "input-error" : ""}
                  />
                )}
                {errors.restecg && (
                  <p className="error-message">{errors.restecg}</p>
                )}
              </div>
              <div className="form-group">
                <div className="form-group-label">
                  <label>Max Heart Rate</label>
                </div>
                {loading ? (
                  <Skeleton height={48} />
                ) : (
                  <input
                    type="number"
                    name="thalach"
                    value={formData.thalach}
                    onChange={handleChange}
                    className={errors.thalach ? "input-error" : ""}
                  />
                )}
                {errors.thalach && (
                  <p className="error-message">{errors.thalach}</p>
                )}
              </div>
              <div className="form-group">
                <div className="form-group-label">
                  <label>Exercise Induced Angina</label>
                </div>
                {loading ? (
                  <Skeleton height={48} />
                ) : (
                  <select
                    name="exang"
                    value={formData.exang}
                    onChange={handleChange}
                  >
                    <option value={1}>Yes</option>
                    <option value={0}>No</option>
                  </select>
                )}
              </div>
              <div className="form-group">
                <div className="form-group-label">
                  <label>ST Depression (Oldpeak)</label>
                </div>
                {loading ? (
                  <Skeleton height={48} />
                ) : (
                  <input
                    type="number"
                    step="0.1"
                    name="oldpeak"
                    value={formData.oldpeak}
                    onChange={handleChange}
                    className={errors.oldpeak ? "input-error" : ""}
                  />
                )}
                {errors.oldpeak && (
                  <p className="error-message">{errors.oldpeak}</p>
                )}
              </div>
              <div className="form-group">
                <div className="form-group-label">
                  <label>Slope of ST Segment</label>
                </div>
                {loading ? (
                  <Skeleton height={48} />
                ) : (
                  <input
                    type="number"
                    name="slope"
                    value={formData.slope}
                    onChange={handleChange}
                    className={errors.slope ? "input-error" : ""}
                  />
                )}
                {errors.slope && (
                  <p className="error-message">{errors.slope}</p>
                )}
              </div>
              <div className="form-group">
                <div className="form-group-label">
                  <label>Major Vessels Colored</label>
                  <FiHelpCircle
                    className="tooltip-icon"
                    data-tooltip-id="ca-tooltip"
                    data-tooltip-content="Number of major vessels (0-3) colored by flourosopy."
                  />
                </div>
                {loading ? (
                  <Skeleton height={48} />
                ) : (
                  <input
                    type="number"
                    name="ca"
                    value={formData.ca}
                    onChange={handleChange}
                    className={errors.ca ? "input-error" : ""}
                  />
                )}
                {errors.ca && <p className="error-message">{errors.ca}</p>}
              </div>
              <div className="form-group">
                <div className="form-group-label">
                  <label>Thalassemia</label>
                  <FiHelpCircle
                    className="tooltip-icon"
                    data-tooltip-id="thal-tooltip"
                    data-tooltip-content="1: normal; 2: fixed defect; 3: reversable defect."
                  />
                </div>
                {loading ? (
                  <Skeleton height={48} />
                ) : (
                  <input
                    type="number"
                    name="thal"
                    value={formData.thal}
                    onChange={handleChange}
                    className={errors.thal ? "input-error" : ""}
                  />
                )}
                {errors.thal && <p className="error-message">{errors.thal}</p>}
              </div>
            </div>
            <div className="form-buttons">
              <button
                type="button"
                className="reset-button"
                onClick={handleReset}
              >
                Reset
              </button>
              <button
                type="submit"
                className="submit-button"
                disabled={loading}
              >
                {loading ? "Predicting..." : "Get Prediction"}
              </button>
            </div>
          </form>
        </SkeletonTheme>
        <OutputPanel result={result} loading={loading} />
      </div>
      <Tooltip id="cp-tooltip" className="custom-tooltip" />
      <Tooltip id="ca-tooltip" className="custom-tooltip" />
      <Tooltip id="thal-tooltip" className="custom-tooltip" />
    </section>
  );
}

export default Heart;
