# 🏥 Health AI - Multiple Disease Prediction Platform

A modern, full-stack web application that uses Machine Learning to predict the risk of four critical diseases: **Diabetes**, **Heart Disease**, **Parkinson's Disease**, and **Stroke**.

Built with a **React** frontend, **FastAPI** backend, and trained using **scikit-learn** models on real-world healthcare datasets.

---

## 🚀 Features

- **4 Individual Prediction Models**: Diabetes, Heart Disease, Parkinson's, and Stroke
- **Comprehensive Assessment**: Get predictions for all four diseases at once
- **Model Performance Comparison**: Interactive charts showing accuracy, precision, recall, and F1-scores
- **Modern, Responsive UI**: Built with React and custom CSS
- **RESTful API**: FastAPI backend with automatic documentation
- **Real-time Predictions**: Instant results with confidence scores

---

## 🛠️ Tech Stack

### Frontend

- React.js
- Chart.js & react-chartjs-2 (for visualizations)
- Modern CSS with glassmorphism effects

### Backend

- FastAPI (Python web framework)
- Uvicorn (ASGI server)
- scikit-learn (ML models)
- Pandas & NumPy (data processing)

### Machine Learning

- Logistic Regression
- Support Vector Machines (SVM)
- Random Forest
- Trained on datasets from Kaggle and UCI ML Repository

---

## 📁 Project Structure

```
MDP-Frontend-Cloud/
│
├── frontend/                          # React application
│   ├── src/
│   │   ├── App.js                     # Main app component
│   │   ├── Diabetes.js                # Diabetes prediction page
│   │   ├── Heart.js                   # Heart disease prediction page
│   │   ├── Parkinsons.js              # Parkinson's prediction page
│   │   ├── Stroke.js                  # Stroke prediction page
│   │   ├── ComprehensiveAssessment.js # All-in-one prediction
│   │   ├── ModelComparison.js         # Model performance charts
│   │   └── assets/                    # Images and charts
│   └── package.json
│
├── backend/                           # FastAPI server
│   ├── main.py                        # API endpoints
│   ├── requirements.txt               # Python dependencies
│   ├── saved_models/                  # Trained ML models
│   │   └── new/
│   │       ├── diabetes_model.sav
│   │       ├── heart_disease_model.sav
│   │       ├── parkinsons_model.sav
│   │       └── stroke_model.sav
│   └── dataset/                       # Training datasets
│
├── colab_files_to_train_models/       # Jupyter notebooks for training
├── model_comparisons/                 # Model performance data
├── Images/                            # Project images
├── app.py                             # Original Streamlit app (legacy)
├── .gitignore
└── README.md
```

---

## ⚙️ Installation & Setup

### Prerequisites

- **Python 3.8+** installed
- **Node.js 14+** and **npm** installed
- **Git** installed

### 1. Clone the Repository

```bash
git clone https://github.com/Mohit-Balachander/Health-AI-App.git
cd Health-AI-App
```

### 2. Set Up the Backend

```bash
# Navigate to the backend folder
cd backend

# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn main:app --reload
```

Your backend will now be running at `http://127.0.0.1:8000`.

### 3. Set Up the Frontend

**Important:** Open a new, separate terminal for this step.

```bash
# Navigate to the frontend folder
cd frontend

# Install Node dependencies
npm install

# Start the React development server
npm start
```

Your React app will automatically open in your browser at `http://localhost:3000` (or another port if 3000 is busy).

---

## 🎯 Usage

1. Navigate to `http://localhost:3000` in your browser
2. Select a disease from the sidebar (Diabetes, Heart, Parkinson's, or Stroke)
3. Fill in the form with the required health parameters
4. Click "Predict" to get instant results
5. View the prediction with confidence score and explanation
6. Or use the **Comprehensive Assessment** to get predictions for all four diseases at once!

---

## 📊 Model Performance

| Disease     | Model               | Accuracy | Precision | Recall | F1-Score |
| ----------- | ------------------- | -------- | --------- | ------ | -------- |
| Diabetes    | Logistic Regression | 77.27%   | 71.43%    | 62.50% | 66.67%   |
| Heart       | SVM                 | 85.25%   | 84.21%    | 88.89% | 86.49%   |
| Parkinson's | SVM                 | 89.74%   | 100.00%   | 80.00% | 88.89%   |
| Stroke      | Random Forest       | 95.12%   | 0.00%     | 0.00%  | 0.00%    |

**Note:** The stroke model shows high accuracy due to class imbalance in the dataset.

---

## 🌐 API Documentation

Once the backend is running, visit `http://127.0.0.1:8000/docs` for the interactive API documentation (Swagger UI).

### Key Endpoints:

- `GET /` - Health check
- `POST /predict/diabetes` - Diabetes prediction
- `POST /predict/heart` - Heart disease prediction
- `POST /predict/parkinsons` - Parkinson's prediction
- `POST /predict/stroke` - Stroke prediction
- `POST /predict/comprehensive` - All four predictions

---

## 📚 Data Sources & Credits

All prediction models were trained on publicly available datasets from:

- [Kaggle](https://www.kaggle.com/)
- [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/index.php)

**Datasets used:**

- Pima Indians Diabetes Database
- Cleveland Heart Disease Dataset
- Parkinson's Disease Dataset
- Stroke Prediction Dataset

---

## ⚠️ Disclaimer

**This application is for educational and demonstration purposes only** and is not a substitute for professional medical advice, diagnosis, or treatment.

Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.

---

## 👨‍💻 Author

**Mohit Balachander**

- GitHub: [@Mohit-Balachander](https://github.com/Mohit-Balachander)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

Feel free to check the [issues page](https://github.com/Mohit-Balachander/Health-AI-App/issues).

---

## 🔮 Future Enhancements

- [ ] Deploy to Google Cloud Platform
- [ ] Add user authentication
- [ ] Store prediction history
- [ ] Add more disease models
- [ ] Improve stroke model performance
- [ ] Add data visualization for input parameters
- [ ] Mobile app version

---

<div align="center">

Made with ❤️ and Machine Learning

</div>
