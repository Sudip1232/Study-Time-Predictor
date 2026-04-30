# 📚 Python ML Study-Time Predictor

A beautiful web application that predicts student study time (books read per year) using machine learning with interactive graphs and visualizations.

## ✨ Features

- **🌐 Web Interface**: Beautiful, responsive web UI
- **📊 Interactive Graphs**: Real-time charts and visualizations
- **📈 Dataset Statistics**: View comprehensive dataset analytics
- **🎯 k-NN Algorithm**: Distance-weighted k-Nearest Neighbors (k=5)
- **🔍 Explainable AI**: Shows nearest neighbors for each prediction
- **💾 Model Persistence**: Save and load trained models

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip3 install flask pandas numpy scikit-learn joblib matplotlib
```

### 2. Start the Web App

```bash
python3 app.py
```

### 3. Open in Browser

Go to: **http://localhost:5000**

## 📸 What You'll See

### Training Dashboard
- Upload CSV dataset
- View training progress
- **Statistics Cards**: Total samples, average books, screen time, gaming hours
- **Genre Distribution Chart**: Bar chart showing top book genres

### Prediction Interface
- Enter student information (screen time, genre, gaming hours)
- Get instant prediction
- **Comparison Chart**: Visual bar chart comparing prediction with neighbors
- **Neighbors Table**: See 5 most similar students from training data

## 📊 Screenshots

The web app includes:
- 📈 **Bar Charts** for genre distribution
- 📊 **Comparison Graphs** for predictions vs neighbors
- 💳 **Statistics Cards** with key metrics
- 📋 **Data Tables** for neighbor analysis

## 🎯 How It Works

1. **Data Loading**: Reads CSV with student survey data
2. **Feature Engineering**:
   - One-hot encoding for book genres
   - StandardScaler for numeric features (screen time, gaming hours)
3. **Model Training**: k-NN regression with distance weighting
4. **Prediction**: Finds 5 nearest neighbors and predicts based on their study time

## 📁 Files

- `app.py` - Flask web application server
- `study_predictor.py` - ML predictor class (train & predict)
- `templates/index.html` - Web interface
- `static/style.css` - Styling and animations
- `Test Data.csv` - Training data (126 student samples)
- `study_model.joblib` - Saved trained model
- `RUN_WEB_APP.md` - Quick start guide

## 🎯 Input Features

- **Screen Time**: Weekly hours watching movies/series (0-40)
- **Book Genre**: Favorite genre (fiction, sci-fi, fantasy, etc.)
- **Gaming Hours**: Weekly gaming hours (0-50, optional)

## 📈 Output

- **Prediction**: Estimated books read per year (0-50)
- **Statistics Dashboard**: Dataset overview with charts
- **Comparison Graph**: Visual bar chart of prediction vs neighbors
- **Neighbors Table**: 5 nearest training examples with their actual values

## 📝 Example Output

### Web Interface
```
Training Dashboard:
✓ Model trained successfully!
Samples: 107 | MAE: 10.03 books/year

Statistics:
📊 Total Samples: 107
📚 Avg Books/Year: 12.5
📺 Avg Screen Time: 15.2h
🎮 Avg Gaming Hours: 8.3h

[Genre Distribution Bar Chart]

Prediction Result:
📊 Prediction: 15.2 books/year

[Comparison Bar Chart showing prediction vs 5 neighbors]

Nearest Neighbors:
1. 20 books (fiction, 10h screen, 4h gaming) - Distance: 0.45
2. 5 books (fiction, 10h screen, 7h gaming) - Distance: 0.52
...
```

## 🔧 Customization

Change the number of neighbors:
```python
predictor = StudyTimePredictor(k=7)  # Use 7 neighbors instead of 5
```

## 📝 Example Output

```
============================================================
Python ML Study-Time Predictor
============================================================

1. Training model...
✓ Loaded 107 valid samples
✓ Model trained on 107 samples
✓ Cross-validation MAE: 10.03 books/year

2. Saving model...
✓ Model saved to study_model.joblib

3. Making predictions...

Example 1: Fiction reader, 10 hrs screen time, 5 hrs gaming
   Predicted: 15.2 books/year
   Nearest neighbors:
     1. 20 books (genre: fiction, screen: 10h, gaming: 4h)
     2. 5 books (genre: fiction, screen: 10h, gaming: 7h)
     3. 5 books (genre: fiction, screen: 10h, gaming: 2h)
```

## 🎓 Comparison with JavaScript Version

| Feature | JavaScript | Python Web App |
|---------|-----------|----------------|
| Interface | Browser-only | Web server + API |
| Algorithm | Manual k-NN | scikit-learn KNeighborsRegressor |
| Feature Scaling | None | StandardScaler |
| Genre Handling | Manual penalty | One-hot encoding |
| Validation | None | 5-fold cross-validation |
| Visualizations | Basic table | Interactive charts & graphs |
| Statistics | None | Full dashboard with metrics |
| Model Saving | None | joblib persistence |
| Accuracy | Basic | Professional ML practices |

## 📦 Requirements

- Python 3.8+
- flask >= 2.0.0
- pandas >= 1.3.0
- numpy >= 1.21.0
- scikit-learn >= 1.0.0
- joblib >= 1.0.0
- matplotlib >= 3.5.0

## 🤝 Contributing

This is a simple educational project. Feel free to modify and extend!

## 📄 License

MIT License - Free to use and modify
