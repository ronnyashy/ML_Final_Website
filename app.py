import os
import joblib
import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- Load Content-Based Assets ---
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Exact filenames from your mate's files
    model = joblib.load(os.path.join(BASE_DIR, 'models', 'ridge_regressor.pkl'))
    scaler = joblib.load(os.path.join(BASE_DIR, 'models', 'feature_scaler.pkl'))
    cols = joblib.load(os.path.join(BASE_DIR, 'models', 'feature_columns.pkl'))
    print(f"✅ AI Engine Online. Features Loaded: {len(cols)}")
except Exception as e:
    print(f"❌ Critical Load Error: {e}")
    model = scaler = cols = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend')
def recommend_page():
    return render_template('recommendations.html')

@app.route('/api/predict', methods=['POST'])
def predict_rating():
    if not model:
        return jsonify({"error": "AI Model not initialized"}), 500

    try:
        data = request.json
        # Create a zero-filled vector for all 1,151 features
        input_df = pd.DataFrame(0.0, index=[0], columns=cols)
        
        # Mapping inputs to the exact feature names in feature_columns.pkl
        input_df['release_year'] = float(data.get('year', 2024))
        input_df['rating_count'] = float(data.get('popularity', 5000))
        
        # Setting the specific genre feature to 1.0 (hot-encoding)
        genre = data.get('genre')
        if genre in cols:
            input_df[genre] = 1.0

        # Perform AI Inference
        scaled_features = scaler.transform(input_df)
        prediction = model.predict(scaled_features)[0]
        
        # Clamp result to MovieLens star range (0.5 to 5.0)
        final_score = max(0.5, min(5.0, round(float(prediction), 2)))
        
        return jsonify({
            "status": "success",
            "predicted_rating": final_score,
            "business_impact": "High Priority" if final_score >= 3.8 else "Standard Acquisition"
        })
    except Exception as e:
        print(f"❌ Inference Error: {e}")
        return jsonify({"error": "Prediction failed. Check backend logs."}), 400

if __name__ == '__main__':
    app.run(debug=True)