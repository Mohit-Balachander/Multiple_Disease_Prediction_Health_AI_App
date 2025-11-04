import React, { useState, useEffect } from "react";
import axios from "axios";
import { FiHelpCircle } from "react-icons/fi";
import Skeleton, { SkeletonTheme } from "react-loading-skeleton";
import { Tooltip } from "react-tooltip";
import ModelSelector from "./ModelSelector";
import OutputPanel from "./OutputPanel";
import { API_URL } from "./config";
const initialFormState = {
  fo: "119.992",
  fhi: "157.302",
  flo: "74.997",
  Jitter_percent: "0.00784",
  Jitter_Abs: "0.00007",
  RAP: "0.0037",
  PPQ: "0.00554",
  DDP: "0.01109",
  Shimmer: "0.04374",
  Shimmer_dB: "0.426",
  APQ3: "0.02182",
  APQ5: "0.0313",
  APQ: "0.02971",
  DDA: "0.06545",
  NHR: "0.02211",
  HNR: "21.033",
  RPDE: "0.414783",
  DFA: "0.815285",
  spread1: "-4.813031",
  spread2: "0.266482",
  D2: "2.301442",
  PPE: "0.284654",
};

function Parkinsons() {
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
    if (value === "" || isNaN(value)) return `This field must be a number.`;
    // spread1 and spread2 can be negative, so we only check other fields
    if (name !== "spread1" && name !== "spread2" && value < 0) {
      return `This value must be non-negative.`;
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
        `${API_URL}/predict/parkinsons`,
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
    <section id="parkinsons" className="section">
      <h2 className="section-title">Parkinson's Prediction</h2>
      <div className="prediction-layout">
        <ModelSelector
          metadata={modelMetadata}
          selected={selectedModel}
          onSelect={setSelectedModel}
          diseaseName="Parkinsons"
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
                      {key.replace("_", " ").replace("percent", "(%)")}
                    </label>
                    <FiHelpCircle
                      className="tooltip-icon"
                      data-tooltip-id="parkinsons-tooltip"
                      data-tooltip-content="These are various measures of voice dysfunction used to detect Parkinson's."
                    />
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
      <Tooltip id="parkinsons-tooltip" className="custom-tooltip" />
    </section>
  );
}

export default Parkinsons;
