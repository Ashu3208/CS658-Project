from flask import Flask, request, render_template, jsonify
import joblib
import numpy as np
from urllib.parse import urlparse
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Load the models
models = {
    'DecisionTreeClassifier': joblib.load('models/DecisionTreeClassifier_best_model.pkl'),
    'LogisticRegression': joblib.load('models/LogisticRegression_best_model.pkl'),
    'RandomForestClassifier': joblib.load('models/RandomForestClassifier_best_model.pkl')
}

# Class label mapping (encoded integer -> human-readable label)
label_mapping = {
    0: "Defacement",
    1: "Benign",
    2: "Phishing",
    3: "Malware",
    4: "Spam"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Get the JSON data sent from the frontend
    data = request.json
    website_url = data.get('url')
    
    if not website_url:
        return jsonify({"error": "Please provide a valid URL."}), 400

    print(f"Received URL: {website_url}")
    
    # Process the URL to extract features
    features = process_url(website_url)
    
    # Make predictions using all models
    predictions = {}
    for model_name, model in models.items():
        # Predict the outcome for the given features
        prediction = model.predict(features)[0]
        
        # Convert prediction to human-readable label using the label mapping
        predictions[model_name] = {
            "encoded_prediction": int(prediction),  # Ensure the prediction is an integer
            "human_readable_label": label_mapping.get(int(prediction), "Unknown")
        }
    
    # Return the predictions in JSON format
    return jsonify(predictions)

def process_url(url):
    """
    Converts the URL into a feature vector for the model.
    
    Parameters:
    - url (str): The URL to process.
    
    Returns:
    - features (np.array): The extracted feature vector (shape: 1, 51).
    """
    # 1. Basic Features
    length = len(url)  # Length of the URL
    num_dots = url.count('.')  # Number of dots in URL
    num_slashes = url.count('/')  # Number of slashes in URL
    num_hyphens = url.count('-')  # Number of hyphens in URL
    has_https = int("https" in url)  # Whether the URL uses https
    
    # 2. Domain-Based Features
    domain = url.split('/')[2] if len(url.split('/')) > 2 else ""
    domain_length = len(domain)  # Length of domain
    num_subdomains = domain.count('.') - 1  # Number of subdomains
    
    # 3. Path-Based Features
    path = url.split('/')[3:]  # The URL path (after the domain)
    path_length = sum(len(segment) for segment in path)  # Length of the path segments
    
    # 4. Query and Special Characters
    num_question_marks = url.count('?')  # Number of query parameters
    num_hashes = url.count('#')  # Number of hashes in URL
    
    # 5. TLD and Protocol Features
    tld = domain.split('.')[-1]  # Extract the TLD (top-level domain)
    is_com = int(tld == 'com')  # Whether the TLD is .com
    is_org = int(tld == 'org')  # Whether the TLD is .org
    
    # 6. Miscellaneous Features
    num_at_symbols = url.count('@')  # Number of @ symbols (used in emails)
    num_percent_symbols = url.count('%')  # Number of percent symbols (in URLs for encoding)
    
    # Example of additional features you can consider
    # These are just placeholder features to reach 51 (you can tweak these)
    feature_list = [
        length, num_dots, num_slashes, num_hyphens, has_https, domain_length,
        num_subdomains, path_length, num_question_marks, num_hashes,
        is_com, is_org, num_at_symbols, num_percent_symbols
    ]
    
    # If the model was trained with additional, more specific features,
    # you should add those here to match the model's expected input.
    
    # Make sure the features list has exactly 51 features (this is an example)
    while len(feature_list) < 51:
        feature_list.append(0)  # Placeholder for additional features if needed
    
    # Convert the features list into a numpy array and then convert it to a native Python list for JSON serialization
    return np.array(feature_list).reshape(1, -1).tolist()  # .tolist() converts it into a regular Python list

if __name__ == '__main__':
    app.run(debug=True)
