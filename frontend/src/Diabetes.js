import React, { useState, useEffect } from "react";
import axios from "axios";
import { FiHelpCircle } from "react-icons/fi";
import Skeleton, { SkeletonTheme } from "react-loading-skeleton";
import { Tooltip } from "react-tooltip";
import ModelSelector from "./ModelSelector";
import OutputPanel from "./OutputPanel";

const API_URL = "http://127.0.0.1:8000";
const initialFormState = {
  Pregnancies: "6",
  Glucose: "148",
  BloodPressure: "72",
  SkinThickness: "35",
  Insulin: "0",
  BMI: "33.6",
  DiabetesPedigreeFunction: "0.627",
  Age: "50",
};

function Diabetes() {
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
      return `${name
        .replace(/([A-Z])/g, " $1")
        .trim()} is required and must be a non-negative number.`;
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
        `${API_URL}/predict/diabetes`,
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
    <section id="diabetes" className="section">
      <h2 className="section-title">Diabetes Prediction</h2>
      <div className="prediction-layout">
        <ModelSelector
          metadata={modelMetadata}
          selected={selectedModel}
          onSelect={setSelectedModel}
          diseaseName="Diabetes"
        />
        <SkeletonTheme
          baseColor="var(--border-color)"
          highlightColor="var(--bg-color)"
        >
          <form onSubmit={handleSubmit} className="prediction-form">
            <div className="form-grid">
              {Object.keys(formData).map((key) => (
                <div className="form-group" key={key}>
                  <div className="form-group-label">
                    <label htmlFor={key}>
                      {key.replace(/([A-Z])/g, " $1").trim()}
                    </label>
                    {key === "DiabetesPedigreeFunction" && (
                      <FiHelpCircle
                        className="tooltip-icon"
                        data-tooltip-id="dpf-tooltip"
                        data-tooltip-content="A function that scores likelihood of diabetes based on family history."
                      />
                    )}
                  </div>
                  {loading ? (
                    <Skeleton height={48} />
                  ) : (
                    <input
                      type="number"
                      id={key}
                      name={key}
                      value={formData[key]}
                      onChange={handleChange}
                      step="any"
                      required
                      className={errors[key] ? "input-error" : ""}
                    />
                  )}
                  {errors[key] && (
                    <p className="error-message">{errors[key]}</p>
                  )}
                </div>
              ))}
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
      <Tooltip id="dpf-tooltip" className="custom-tooltip" />
    </section>
  );
}

export default Diabetes;
