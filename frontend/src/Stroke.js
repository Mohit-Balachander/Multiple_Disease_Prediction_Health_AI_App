import React, { useState, useEffect } from "react";
import axios from "axios";
import { FiHelpCircle } from "react-icons/fi";
import Skeleton, { SkeletonTheme } from "react-loading-skeleton";
import { Tooltip } from "react-tooltip";
import ModelSelector from "./ModelSelector";
import OutputPanel from "./OutputPanel";

const API_URL = "http://127.0.0.1:8000";
const initialFormState = {
  age: "67",
  hypertension: 0,
  heart_disease: 1,
  avg_glucose_level: "228.69",
  bmi: "36.6",
  gender: "Male",
  ever_married: "Yes",
  work_type: "Private",
  Residence_type: "Urban",
  smoking_status: "formerly smoked",
};

function Stroke() {
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
    const numericFields = ["age", "avg_glucose_level", "bmi"];
    if (numericFields.includes(name)) {
      if (value === "" || isNaN(value) || value < 0) {
        return `This field must be a non-negative number.`;
      }
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
    const parsedFormData = { ...formData };

    Object.keys(formData).forEach((key) => {
      const value = formData[key];
      const error = validateField(key, value);
      if (error) {
        newErrors[key] = error;
        hasError = true;
      }
      // Parse numeric fields for the API call
      if (
        !isNaN(value) &&
        typeof value !== "boolean" &&
        key.match(/age|hypertension|heart_disease|avg_glucose_level|bmi/)
      ) {
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
        `${API_URL}/predict/stroke`,
        requestBody
      );
      setResult(response.data);
    } catch (err) {
      setResult({ prediction: -1, result_message: "An error occurred." });
    } finally {
      setLoading(false);
    }
  };

  const renderField = (name, type = "number") => {
    const options = {
      hypertension: [
        { label: "Yes", value: 1 },
        { label: "No", value: 0 },
      ],
      heart_disease: [
        { label: "Yes", value: 1 },
        { label: "No", value: 0 },
      ],
      gender: [
        { label: "Male", value: "Male" },
        { label: "Female", value: "Female" },
      ],
      ever_married: [
        { label: "Yes", value: "Yes" },
        { label: "No", value: "No" },
      ],
      work_type: [
        { label: "Private", value: "Private" },
        { label: "Self-employed", value: "Self-employed" },
        { label: "Govt Job", value: "Govt_job" },
        { label: "Child", value: "children" },
        { label: "Never Worked", value: "Never_worked" },
      ],
      Residence_type: [
        { label: "Urban", value: "Urban" },
        { label: "Rural", value: "Rural" },
      ],
      smoking_status: [
        { label: "Formerly Smoked", value: "formerly smoked" },
        { label: "Never Smoked", value: "never smoked" },
        { label: "Smokes", value: "smokes" },
        { label: "Unknown", value: "Unknown" },
      ],
    };

    return (
      <div className="form-group" key={name}>
        <div className="form-group-label">
          <label>{name.replace(/_/g, " ")}</label>
          {name === "bmi" && (
            <FiHelpCircle
              className="tooltip-icon"
              data-tooltip-id="bmi-tooltip"
              data-tooltip-content="Body Mass Index. Normal range is 18.5-24.9."
            />
          )}
        </div>
        {loading ? (
          <Skeleton height={48} />
        ) : type === "select" ? (
          <select name={name} value={formData[name]} onChange={handleChange}>
            {options[name].map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        ) : (
          <input
            type="number"
            name={name}
            value={formData[name]}
            onChange={handleChange}
            step="any"
            required
            className={errors[name] ? "input-error" : ""}
          />
        )}
        {errors[name] && <p className="error-message">{errors[name]}</p>}
      </div>
    );
  };

  return (
    <section id="stroke" className="section">
      <h2 className="section-title">Stroke Prediction</h2>
      <div className="prediction-layout">
        <ModelSelector
          metadata={modelMetadata}
          selected={selectedModel}
          onSelect={setSelectedModel}
          diseaseName="Stroke"
        />
        <SkeletonTheme
          baseColor="var(--border-color)"
          highlightColor="var(--bg-color)"
        >
          <form onSubmit={handleSubmit} className="prediction-form">
            <div className="form-grid">
              {renderField("age")}
              {renderField("bmi")}
              {renderField("avg_glucose_level")}
              {renderField("hypertension", "select")}
              {renderField("heart_disease", "select")}
              {renderField("gender", "select")}
              {renderField("ever_married", "select")}
              {renderField("work_type", "select")}
              {renderField("Residence_type", "select")}
              {renderField("smoking_status", "select")}
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
      <Tooltip id="bmi-tooltip" className="custom-tooltip" />
    </section>
  );
}

export default Stroke;
