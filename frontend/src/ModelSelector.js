import React from "react";
// THE FIX: Added the missing import for the Skeleton component
import Skeleton from "react-loading-skeleton";

const ModelSelector = ({ metadata, selected, onSelect, diseaseName }) => {
  // Check if metadata for the specific disease is available
  const diseaseMetadata = metadata ? metadata[diseaseName] : null;

  return (
    <div className="model-selector">
      <h3>Choose Model</h3>
      {/* If metadata is not loaded yet, show skeletons */}
      {!diseaseMetadata ? (
        <>
          <Skeleton height={60} style={{ marginBottom: "10px" }} />
          <Skeleton height={60} />
        </>
      ) : (
        Object.keys(diseaseMetadata).map((version) => {
          const model = diseaseMetadata[version];
          if (!model) return null;
          return (
            <div
              key={version}
              className={`model-option ${
                selected === version ? "selected" : ""
              }`}
              onClick={() => onSelect(version)}
            >
              <div className="algorithm">{model.algorithm}</div>
              <div className="accuracy">
                Accuracy: {(model.accuracy * 100).toFixed(2)}%
              </div>
            </div>
          );
        })
      )}
    </div>
  );
};

export default ModelSelector;
