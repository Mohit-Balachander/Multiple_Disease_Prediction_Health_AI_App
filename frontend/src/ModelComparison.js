import React from "react";

// You can keep this image if you have one, or remove it.
import ModelAccuracyComparisonImg from "./assets/model_accuracy_comparison.png";

// The static data from your screenshot
const performanceData = [
  {
    Disease: "Diabetes",
    Algorithm: "LogisticRegression",
    Accuracy: 0.7143,
    Precision: 0.6087,
    Recall: 0.5185,
    F1Score: 0.56,
  },
  {
    Disease: "Diabetes",
    Algorithm: "RandomForest",
    Accuracy: 0.7013,
    Precision: 0.5625,
    Recall: 0.6667,
    F1Score: 0.6102,
  },
  {
    Disease: "Heart",
    Algorithm: "DecisionTree",
    Accuracy: 0.6885,
    Precision: 0.7059,
    Recall: 0.7273,
    F1Score: 0.7164,
  },
  {
    Disease: "Heart",
    Algorithm: "GradientBoosting",
    Accuracy: 0.7705,
    Precision: 0.7714,
    Recall: 0.8182,
    F1Score: 0.7941,
  },
  {
    Disease: "Parkinsons",
    Algorithm: "SVM",
    Accuracy: 0.9231,
    Precision: 0.9062,
    Recall: 1.0,
    F1Score: 0.9508,
  },
  {
    Disease: "Parkinsons",
    Algorithm: "AdaBoost",
    Accuracy: 0.8718,
    Precision: 0.9,
    Recall: 0.931,
    F1Score: 0.9153,
  },
  {
    Disease: "Stroke",
    Algorithm: "LogisticRegression",
    Accuracy: 0.7397,
    Precision: 0.1351,
    Recall: 0.8,
    F1Score: 0.2312,
  },
  {
    Disease: "Stroke",
    Algorithm: "RandomForest",
    Accuracy: 0.9364,
    Precision: 0.1739,
    Recall: 0.08,
    F1Score: 0.1096,
  },
];

function ModelComparison() {
  return (
    <section id="comparison" className="section">
      <h2 className="section-title">Model Performance</h2>
      <p className="section-subtitle">
        An overview of the performance metrics for our prediction models on a
        test dataset.
      </p>
      <div className="comparison-container">
        {/* You can keep your main comparison image here */}
        <img
          src={ModelAccuracyComparisonImg}
          alt="Model Accuracy Comparison Chart"
          className="main-comparison-image"
        />

        <h3 className="subsection-title">Detailed Performance Metrics</h3>
        <div className="metrics-table-container">
          <table className="metrics-table">
            <thead>
              <tr>
                <th>Disease</th>
                <th>Algorithm</th>
                <th>Accuracy</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1-Score</th>
              </tr>
            </thead>
            <tbody>
              {performanceData.map((metric, index) => (
                <tr key={index}>
                  <td>{metric.Disease}</td>
                  <td>{metric.Algorithm}</td>
                  <td>{metric.Accuracy.toFixed(4)}</td>
                  <td>{metric.Precision.toFixed(4)}</td>
                  <td>{metric.Recall.toFixed(4)}</td>
                  <td>{metric.F1Score.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

export default ModelComparison;
