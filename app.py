import os
from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai
from datetime import datetime
import json

app = Flask(__name__)

# Configure Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-commerce Behavior Analysis</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 p-8">
    <div class="max-w-4xl mx-auto">
        <h1 class="text-3xl font-bold mb-8">E-commerce Behavior Analysis</h1>
        
        <div class="bg-white p-6 rounded-lg shadow-md mb-8">
            <h2 class="text-xl font-semibold mb-4">Upload JSON Data</h2>
            <textarea id="jsonInput" class="w-full h-48 p-4 border rounded-md mb-4" placeholder="Paste your JSON data here..."></textarea>
            <button onclick="analyzeData()" class="bg-blue-500 text-white px-6 py-2 rounded-md hover:bg-blue-600">Analyze</button>
        </div>

        <div id="results" class="bg-white p-6 rounded-lg shadow-md hidden">
            <h2 class="text-xl font-semibold mb-4">Analysis Results</h2>
            
            <div class="grid grid-cols-3 gap-4 mb-6">
                <div class="bg-gray-50 p-4 rounded-md">
                    <h3 class="font-medium text-gray-700">Total Views</h3>
                    <p id="totalViews" class="text-2xl font-bold text-blue-600">-</p>
                </div>
                <div class="bg-gray-50 p-4 rounded-md">
                    <h3 class="font-medium text-gray-700">Unique Customers</h3>
                    <p id="uniqueCustomers" class="text-2xl font-bold text-blue-600">-</p>
                </div>
                <div class="bg-gray-50 p-4 rounded-md">
                    <h3 class="font-medium text-gray-700">Unique Products</h3>
                    <p id="uniqueProducts" class="text-2xl font-bold text-blue-600">-</p>
                </div>
            </div>

            <div class="mb-6">
                <h3 class="font-semibold mb-2">AI Analysis</h3>
                <div id="aiAnalysis" class="bg-gray-50 p-4 rounded-md whitespace-pre-wrap"></div>
            </div>
        </div>
    </div>

    <script>
        async function analyzeData() {
            const jsonInput = document.getElementById('jsonInput').value;
            try {
                const data = JSON.parse(jsonInput);
                
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.error) {
                    alert('Error: ' + result.error);
                    return;
                }
                
                document.getElementById('results').classList.remove('hidden');
                document.getElementById('totalViews').textContent = result.metrics.total_views;
                document.getElementById('uniqueCustomers').textContent = result.metrics.unique_customers;
                document.getElementById('uniqueProducts').textContent = result.metrics.unique_products;
                document.getElementById('aiAnalysis').textContent = result.ai_analysis;
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
    </script>
</body>
</html>
'''

def analyze_user_behavior(data):
    # Prepare prompt for Gemini AI
    analysis_prompt = f"""
    Analyze this e-commerce user behavior data and provide insights on:
    1. User behavior patterns
    2. Funnel conversion rates
    3. Potential chatbot intervention points
    
    Data: {json.dumps(data, indent=2)}
    
    Please provide a structured analysis with specific recommendations.
    """
    
    try:
        response = model.generate_content(analysis_prompt)
        return response.text
    except Exception as e:
        return f"Error in analysis: {str(e)}"

def process_timestamps(data):
    # Convert timestamps to readable format and extract basic metrics
    metrics = {
        "total_views": 0,
        "unique_customers": set(),
        "products_viewed": set()
    }
    
    for event in data:
        if event["event"] == "product_viewed":
            metrics["total_views"] += 1
            metrics["unique_customers"].add(event["properties"]["customer_id"])
            metrics["products_viewed"].add(
                event["properties"]["payload"]["data"]["productVariant"]["product"]["title"]
            )
    
    return {
        "total_views": metrics["total_views"],
        "unique_customers": len(metrics["unique_customers"]),
        "unique_products": len(metrics["products_viewed"])
    }

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Get basic metrics
        metrics = process_timestamps(data)
        
        # Get AI analysis
        ai_analysis = analyze_user_behavior(data)
        
        return jsonify({
            "metrics": metrics,
            "ai_analysis": ai_analysis
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)), debug=True)
