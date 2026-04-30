"""Flask web application for Study-Time Predictor."""

from flask import Flask, render_template, request, jsonify, send_file
import os
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from study_predictor import StudyTimePredictor

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads folder if it doesn't exist
os.makedirs('uploads', exist_ok=True)

# Global predictor instance
predictor = None


@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/train', methods=['POST'])
def train():
    """Train model with uploaded CSV."""
    global predictor
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Please upload a CSV file'}), 400
    
    try:
        # Save uploaded file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'dataset.csv')
        file.save(filepath)
        
        # Train model
        predictor = StudyTimePredictor(k=5)
        X, y = predictor.load_data(filepath)
        mae = predictor.train(X, y)
        
        # Save model
        predictor.save('study_model.joblib')
        
        # Generate statistics
        stats = generate_statistics(X, y)
        
        return jsonify({
            'success': True,
            'message': f'Model trained successfully!',
            'samples': len(X),
            'mae': round(mae, 2),
            'stats': stats
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def generate_statistics(X, y):
    """Generate dataset statistics."""
    stats = {
        'total_samples': len(X),
        'avg_books': round(y.mean(), 1),
        'min_books': int(y.min()),
        'max_books': int(y.max()),
        'avg_screen_time': round(X['screen_time'].mean(), 1),
        'avg_gaming_hours': round(X['gaming_hours'].mean(), 1),
        'genre_distribution': X['book_genre'].value_counts().head(5).to_dict()
    }
    return stats


@app.route('/predict', methods=['POST'])
def predict():
    """Make a prediction."""
    global predictor
    
    # Load model if not already loaded
    if predictor is None:
        try:
            predictor = StudyTimePredictor.load('study_model.joblib')
        except FileNotFoundError:
            return jsonify({'error': 'Model not trained yet. Please upload and train a dataset first.'}), 400
    
    try:
        data = request.json
        screen_time = float(data.get('screen_time', 0))
        book_genre = data.get('book_genre', '').strip()
        gaming_hours = float(data.get('gaming_hours', 0))
        
        if not book_genre:
            return jsonify({'error': 'Book genre is required'}), 400
        
        if screen_time < 0 or gaming_hours < 0:
            return jsonify({'error': 'Hours must be non-negative'}), 400
        
        # Make prediction
        prediction, neighbors = predictor.predict(screen_time, book_genre, gaming_hours)
        
        # Generate comparison chart
        chart_data = generate_comparison_chart(prediction, neighbors)
        
        return jsonify({
            'success': True,
            'prediction': round(prediction, 1),
            'neighbors': [
                {
                    'books_read': int(n['books_read']),
                    'screen_time': int(n['screen_time']),
                    'book_genre': n['book_genre'],
                    'gaming_hours': int(n['gaming_hours']),
                    'distance': round(n['distance'], 2)
                }
                for n in neighbors
            ],
            'chart': chart_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def generate_comparison_chart(prediction, neighbors):
    """Generate comparison chart as base64 image."""
    plt.figure(figsize=(10, 5))
    
    # Prepare data
    labels = ['Your\nPrediction'] + [f'Neighbor {i+1}' for i in range(len(neighbors))]
    values = [prediction] + [n['books_read'] for n in neighbors]
    colors = ['#667eea'] + ['#48bb78'] * len(neighbors)
    
    # Create bar chart
    bars = plt.bar(labels, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    plt.xlabel('Students', fontsize=12, fontweight='bold')
    plt.ylabel('Books Read per Year', fontsize=12, fontweight='bold')
    plt.title('Prediction vs Nearest Neighbors', fontsize=14, fontweight='bold', pad=20)
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    # Convert to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return image_base64


@app.route('/status')
def status():
    """Check if model is trained."""
    model_exists = os.path.exists('study_model.joblib')
    return jsonify({
        'model_trained': model_exists
    })


if __name__ == '__main__':
    # Try to load existing model
    if os.path.exists('study_model.joblib'):
        try:
            predictor = StudyTimePredictor.load('study_model.joblib')
            print("✓ Loaded existing model")
        except:
            print("⚠ Could not load existing model")
    
    print("\n" + "=" * 60)
    print("🚀 Study-Time Predictor Web App")
    print("=" * 60)
    print("\n📱 Open your browser and go to: http://localhost:5001")
    print("\n" + "=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
