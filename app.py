import os
import json
import openai
from flask import Flask, request, jsonify, render_template_string

# Initialize Flask app
app = Flask(__name__)

# Set the OpenAI API key using environment variables directly
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configure OpenAI with the API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# HTML Template for File Upload
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload and Analyze JSON</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            text-align: center;
            margin-top: 50px;
        }
        form {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            margin: 0 auto;
        }
        input[type="file"] {
            margin: 20px 0;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 5px;
        }
        button:hover {
            background-color: #45a049;
        }
        h1 {
            color: #333;
        }
    </style>
</head>
<body>
    <h1>Upload JSON File for Analysis</h1>
    <form action="/analyze" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept=".json" required>
        <button type="submit">Upload and Analyze</button>
    </form>
</body>
</html>
"""

# Home route with upload form
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

# Route to handle file upload and analysis
@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400

    try:
        # Parse JSON file
        data = json.load(file)
        
        # Convert data to string for AI input
        data_str = json.dumps(data, indent=2)

        # Prompt for GPT-4 (OpenAI) analysis
        prompt = f"""
        The following is JSON data from an e-commerce store describing user behaviors. Analyze the data for user behavior patterns, funnel conversion rates, and potential AI chatbot interventions.

        {data_str}

        Provide insights in a concise format:
        """

        # Query OpenAI GPT-4 API
        response = openai.Completion.create(
            model="gpt-4",
            prompt=prompt,
            max_tokens=500
        )

        # Extract GPT response
        analysis = response.choices[0].text.strip()
        
        return jsonify({"analysis": analysis, "message": "Upload Complete!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))
