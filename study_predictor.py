"""Simple Python ML Study-Time Predictor using k-NN."""

import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import cross_val_score
import joblib


class StudyTimePredictor:
    """Simple k-NN predictor for study time estimation."""
    
    def __init__(self, k=5):
        """Initialize predictor with k neighbors."""
        self.k = k
        self.model = KNeighborsRegressor(n_neighbors=k, weights='distance')
        self.scaler = StandardScaler()
        self.encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
        self.X_train_raw = None
        self.y_train = None
        
    def load_data(self, csv_path):
        """Load and clean data from CSV."""
        # Read CSV
        df = pd.read_csv(csv_path)
        
        # Normalize column names
        df.columns = [col.replace('\n', ' ').strip().lower() for col in df.columns]
        
        # Find the right columns
        screen_col = [c for c in df.columns if 'screen time' in c and 'movies' in c][0]
        genre_col = [c for c in df.columns if 'book genre top' in c][0]
        gaming_col = [c for c in df.columns if 'gaming hours' in c][0]
        books_col = [c for c in df.columns if 'books read past year' in c][0]
        
        # Extract data
        df['screen_time'] = pd.to_numeric(df[screen_col], errors='coerce')
        df['book_genre'] = df[genre_col].astype(str).str.strip().str.lower()
        df['gaming_hours'] = pd.to_numeric(df[gaming_col], errors='coerce').fillna(0)
        df['reads_books'] = pd.to_numeric(df[books_col], errors='coerce')
        
        # Clean data
        df = df[df['reads_books'].notna()]
        df = df[df['reads_books'] >= 0]
        df = df[df['book_genre'] != '']
        df = df[df['book_genre'] != 'nan']
        
        print(f"✓ Loaded {len(df)} valid samples")
        
        # Prepare features and target
        X = df[['screen_time', 'book_genre', 'gaming_hours']].copy()
        y = df['reads_books'].values
        
        return X, y
    
    def train(self, X, y):
        """Train the model."""
        # Store raw training data for neighbor analysis
        self.X_train_raw = X.copy()
        self.y_train = y.copy()
        
        # Prepare features
        X_processed = self._prepare_features(X, fit=True)
        
        # Train model
        self.model.fit(X_processed, y)
        
        # Evaluate with cross-validation
        scores = cross_val_score(self.model, X_processed, y, cv=5, 
                                scoring='neg_mean_absolute_error')
        mae = -scores.mean()
        
        print(f"✓ Model trained on {len(X)} samples")
        print(f"✓ Cross-validation MAE: {mae:.2f} books/year")
        
        return mae
    
    def _prepare_features(self, X, fit=False):
        """Prepare features for model."""
        # Separate numeric and categorical
        numeric = X[['screen_time', 'gaming_hours']].copy()
        
        # Fill any remaining NaN values with 0
        numeric = numeric.fillna(0).values
        
        categorical = X[['book_genre']].values
        
        # Scale numeric features
        if fit:
            numeric_scaled = self.scaler.fit_transform(numeric)
            categorical_encoded = self.encoder.fit_transform(categorical)
        else:
            numeric_scaled = self.scaler.transform(numeric)
            categorical_encoded = self.encoder.transform(categorical)
        
        # Combine features
        X_processed = np.hstack([numeric_scaled, categorical_encoded])
        
        return X_processed
    
    def predict(self, screen_time, book_genre, gaming_hours=0):
        """Make a prediction."""
        # Create input dataframe
        X_input = pd.DataFrame({
            'screen_time': [screen_time],
            'book_genre': [book_genre.lower()],
            'gaming_hours': [gaming_hours]
        })
        
        # Prepare features
        X_processed = self._prepare_features(X_input, fit=False)
        
        # Predict
        prediction = self.model.predict(X_processed)[0]
        
        # Find nearest neighbors
        distances, indices = self.model.kneighbors(X_processed)
        
        neighbors = []
        for dist, idx in zip(distances[0], indices[0]):
            neighbors.append({
                'distance': dist,
                'books_read': self.y_train[idx],
                'screen_time': self.X_train_raw.iloc[idx]['screen_time'],
                'book_genre': self.X_train_raw.iloc[idx]['book_genre'],
                'gaming_hours': self.X_train_raw.iloc[idx]['gaming_hours']
            })
        
        return prediction, neighbors
    
    def save(self, filepath='model.joblib'):
        """Save the trained model."""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'encoder': self.encoder,
            'X_train_raw': self.X_train_raw,
            'y_train': self.y_train,
            'k': self.k
        }, filepath)
        print(f"✓ Model saved to {filepath}")
    
    @staticmethod
    def load(filepath='model.joblib'):
        """Load a trained model."""
        data = joblib.load(filepath)
        predictor = StudyTimePredictor(k=data['k'])
        predictor.model = data['model']
        predictor.scaler = data['scaler']
        predictor.encoder = data['encoder']
        predictor.X_train_raw = data['X_train_raw']
        predictor.y_train = data['y_train']
        print(f"✓ Model loaded from {filepath}")
        return predictor


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Python ML Study-Time Predictor")
    print("=" * 60)
    
    # Train model
    print("\n1. Training model...")
    predictor = StudyTimePredictor(k=5)
    X, y = predictor.load_data('Test Data.csv')
    predictor.train(X, y)
    
    # Save model
    print("\n2. Saving model...")
    predictor.save('study_model.joblib')
    
    # Make predictions
    print("\n3. Making predictions...")
    print("\nExample 1: Fiction reader, 10 hrs screen time, 5 hrs gaming")
    pred, neighbors = predictor.predict(
        screen_time=10,
        book_genre='fiction',
        gaming_hours=5
    )
    print(f"   Predicted: {pred:.1f} books/year")
    print(f"   Nearest neighbors:")
    for i, n in enumerate(neighbors[:3], 1):
        print(f"     {i}. {n['books_read']:.0f} books (genre: {n['book_genre']}, "
              f"screen: {n['screen_time']:.0f}h, gaming: {n['gaming_hours']:.0f}h)")
    
    print("\nExample 2: Sci-Fi reader, 20 hrs screen time, 10 hrs gaming")
    pred, neighbors = predictor.predict(
        screen_time=20,
        book_genre='sci-fi',
        gaming_hours=10
    )
    print(f"   Predicted: {pred:.1f} books/year")
    
    print("\n" + "=" * 60)
    print("✓ Complete! Use study_model.joblib for predictions")
    print("=" * 60)
