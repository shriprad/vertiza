import os
import json
from flask import Flask, request, jsonify, render_template_string
import openai

# Initialize Flask app
app = Flask(__name__)

# Configure OpenAI API key
openai.api_key = os.getenv('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')

# HTML Template for File Upload
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload and Analyze JSON</title>
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
        
        # Convert data to string for GPT input
        data_str = json.dumps(data, indent=2)

        # Prompt for ChatGPT
        prompt = f"""
        The following is JSON data from an e-commerce store describing user behaviors. Analyze the data for user behavior patterns, funnel conversion rates, and potential AI chatbot interventions.
        
        {data_str}
        
        Provide insights in a concise format:
        """

        # Query ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data analyst."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract GPT response
        analysis = response['choices'][0]['message']['content']
        
        return jsonify({"analysis": analysis})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))
