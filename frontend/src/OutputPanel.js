import React from "react";
import { FiCheckCircle, FiAlertTriangle, FiBarChart2 } from "react-icons/fi";
import Skeleton from "react-loading-skeleton"; // Import Skeleton

const OutputPanel = ({ result, loading }) => (
  <div className="output-panel">
    {loading ? (
      <div className="output-placeholder">
        <Skeleton circle={true} height={60} width={60} />
        <Skeleton height={30} width={200} />
        <Skeleton height={20} width={150} />
      </div>
    ) : result ? (
      <div
        className={`result ${
          result.prediction === 1 || result.prediction === -1
            ? "negative"
            : "positive"
        }`}
      >
        <div className="result-icon">
          {result.prediction === 1 || result.prediction === -1 ? (
            <FiAlertTriangle />
          ) : (
            <FiCheckCircle />
          )}
        </div>
        <p className="message">{result.result_message}</p>
        {result.accuracy && (
          <p className="confidence">
            Model Accuracy: {(result.accuracy * 100).toFixed(2)}%
          </p>
        )}
        {result.confidence && (
          <p className="confidence">
            <strong>Prediction Confidence:</strong>{" "}
            {result.confidence.toFixed(2)}%
          </p>
        )}
      </div>
    ) : (
      <div className="output-placeholder">
        <FiBarChart2 className="output-placeholder-icon" />
        <p>Your prediction result will appear here.</p>
      </div>
    )}
  </div>
);

export default OutputPanel;
