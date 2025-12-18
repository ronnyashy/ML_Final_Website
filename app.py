import os
import joblib
import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# --- Load Assets ---
try:
    # Content-Based Models
    model_reg = joblib.load(os.path.join(MODELS_DIR, 'ridge_regressor.pkl'))
    scaler = joblib.load(os.path.join(MODELS_DIR, 'feature_scaler.pkl'))
    cols = joblib.load(os.path.join(MODELS_DIR, 'feature_columns.pkl'))
    
    # Collaborative Model (SVD)
    svd_model = joblib.load(os.path.join(MODELS_DIR, 'svd_personalized.pkl'))
    
    # Title Mapping
    movies_df = pd.read_csv(os.path.join(BASE_DIR, 'movies.csv'))
    
    print("✅ All AI Modules & Data Loaded Successfully")
except Exception as e:
    print(f"❌ Error Loading Assets: {e}")
    model_reg = scaler = cols = svd_model = movies_df = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend')
def recommend_page():
    return render_template('recommendations.html')

# --- Feature 1: Content-Based Prediction (Restored Popularity) ---
@app.route('/api/predict', methods=['POST'])
def predict_rating():
    data = request.json
    input_df = pd.DataFrame(0.0, index=[0], columns=cols)
    
    # Map inputs to model features
    input_df['release_year'] = float(data.get('year', 2024))
    input_df['rating_count'] = float(data.get('popularity', 5000))
    
    genre = data.get('genre')
    if genre in cols:
        input_df[genre] = 1.0

    try:
        scaled_features = scaler.transform(input_df)
        prediction = model_reg.predict(scaled_features)[0]
        final_score = max(0.5, min(5.0, round(float(prediction), 2)))
        return jsonify({
            "status": "success",
            "predicted_rating": final_score,
            "impact": "High Potential" if final_score >= 3.8 else "Standard Performance"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# --- Feature 2: Collaborative Filtering (Fixed for Unique Recommendations) ---
@app.route('/api/user-recommend/<user_id>')
def get_user_picks(user_id):
    if not svd_model or movies_df is None:
        return jsonify({"error": "SVD Model not loaded"}), 500
    
    try:
        # Convert user_id to int because Surprise usually trains on integers
        uid = int(user_id)
        
        # We'll take a sample of 1000 movies to find the best ones
        sample_movies = movies_df.sample(min(1000, len(movies_df)))
        
        predictions = []
        for _, row in sample_movies.iterrows():
            m_id = int(row['movieId'])
            # SVD Prediction - passing the integer ID
            pred = svd_model.predict(uid, m_id)
            
            predictions.append({
                "title": row['title'],
                "score": round(pred.est, 2),
                "genres": row['genres']
            })
        
        # Sort and take Top 5
        predictions.sort(key=lambda x: x['score'], reverse=True)
        return jsonify(predictions[:5])
    except Exception as e:
        # Fallback for string IDs if the model was trained on strings
        print(f"Retry with string IDs due to: {e}")
        try:
            predictions = []
            for _, row in movies_df.head(500).iterrows():
                pred = svd_model.predict(str(user_id), str(row['movieId']))
                predictions.append({
                    "title": row['title'], "score": round(pred.est, 2), "genres": row['genres']
                })
            predictions.sort(key=lambda x: x['score'], reverse=True)
            return jsonify(predictions[:5])
        except:
            return jsonify({"error": "Failed to generate personalized picks"}), 400

if __name__ == '__main__':
    app.run(debug=True)