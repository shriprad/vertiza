import os
from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai
from datetime import datetime
import json
from urllib.parse import parse_qs, urlparse

app = Flask(__name__)

# Configure Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# Enhanced HTML Template with better styling and more detailed results
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
    <div class="max-w-6xl mx-auto">
        <h1 class="text-3xl font-bold mb-8">E-commerce Behavior Analysis</h1>
        
        <div class="bg-white p-6 rounded-lg shadow-md mb-8">
            <h2 class="text-xl font-semibold mb-4">Upload JSON Data</h2>
            <textarea id="jsonInput" class="w-full h-48 p-4 border rounded-md mb-4" placeholder="Paste your JSON data here..."></textarea>
            <button onclick="analyzeData()" class="bg-blue-500 text-white px-6 py-2 rounded-md hover:bg-blue-600">Analyze</button>
        </div>

        <div id="results" class="bg-white p-6 rounded-lg shadow-md hidden">
            <h2 class="text-xl font-semibold mb-6">Analysis Results</h2>
            
            <div class="grid grid-cols-4 gap-4 mb-8">
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
                <div class="bg-gray-50 p-4 rounded-md">
                    <h3 class="font-medium text-gray-700">UTM Sources</h3>
                    <p id="utmSources" class="text-2xl font-bold text-blue-600">-</p>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-8">
                <div>
                    <h3 class="font-semibold mb-4">Basic Metrics</h3>
                    <div id="basicMetrics" class="bg-gray-50 p-4 rounded-md"></div>
                </div>
                <div>
                    <h3 class="font-semibold mb-4">Cohort Analysis</h3>
                    <div id="cohortAnalysis" class="bg-gray-50 p-4 rounded-md"></div>
                </div>
            </div>

            <div class="mt-8">
                <h3 class="font-semibold mb-4">AI Analysis</h3>
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
                document.getElementById('utmSources').textContent = result.metrics.utm_sources;
                document.getElementById('basicMetrics').innerHTML = result.metrics.basic_metrics_html;
                document.getElementById('cohortAnalysis').innerHTML = result.metrics.cohort_analysis_html;
                document.getElementById('aiAnalysis').textContent = result.ai_analysis;
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
    </script>
</body>
</html>
'''

def extract_utm_data(href):
    """Extract UTM parameters from URL"""
    try:
        parsed_url = urlparse(href)
        query_params = parse_qs(parsed_url.query)
        return {
            'utm_source': query_params.get('utm_source', [None])[0],
            'utm_medium': query_params.get('utm_medium', [None])[0],
            'utm_campaign': query_params.get('utm_campaign', [None])[0]
        }
    except:
        return {'utm_source': None, 'utm_medium': None, 'utm_campaign': None}

def analyze_user_behavior(data):
    """Enhanced analysis using Gemini AI"""
    analysis_prompt = """
    As an expert e-commerce data analyst and product manager, analyze the following JSON data for a skincare e-commerce website with an AI chatbot (Verifast). Provide a comprehensive analysis covering:

    1. Current Value Analysis
    - How is the AI chatbot currently adding value?
    - Identify key interaction points in the customer journey
    - Analyze patterns in chatbot engagement

    2. Cohort Analysis
    - Analyze cohorts based on:
      * UTM sources/marketing channels
      * Visit frequency (first-time vs returning)
      * Cart behavior (especially abandonment)
    - For each cohort, analyze:
      * Engagement patterns
      * Conversion rates
      * Chatbot interaction rates

    3. Proactive Engagement Opportunities
    - Which cohorts could benefit from AI intervention?
    - What are the optimal trigger points?
    - Expected impact of interventions

    4. Experiment Design
    - Detailed A/B test design including:
      * Clear hypothesis
      * Test/control groups
      * Success metrics
      * Duration
      * Sample size

    5. Additional Recommendations
    - New data points to capture
    - New AI intervention methods
    - Success metrics for each intervention

    Format as a clear report with actionable insights.

    Data: {data}
    """
    
    try:
        response = model.generate_content(analysis_prompt.format(data=json.dumps(data, indent=2)))
        return response.text
    except Exception as e:
        return f"Error in analysis: {str(e)}"

def process_data(data):
    """Enhanced data processing with more detailed metrics"""
    metrics = {
        "total_views": 0,
        "unique_customers": set(),
        "products_viewed": set(),
        "utm_sources": set(),
        "events_by_type": {},
        "customer_journey": {}
    }
    
    for event in data:
        # Basic event counting
        event_type = event["event"]
        metrics["events_by_type"][event_type] = metrics["events_by_type"].get(event_type, 0) + 1
        
        # Customer tracking
        customer_id = event["properties"]["customer_id"]
        metrics["unique_customers"].add(customer_id)
        
        # Product tracking
        if event_type == "product_viewed":
            metrics["total_views"] += 1
            product_title = event["properties"]["payload"]["data"]["productVariant"]["product"]["title"]
            metrics["products_viewed"].add(product_title)
            
            # Extract UTM data
            href = event["properties"]["payload"]["context"].get("href", "")
            utm_data = extract_utm_data(href)
            if utm_data["utm_source"]:
                metrics["utm_sources"].add(utm_data["utm_source"])
            
            # Track customer journey
            if customer_id not in metrics["customer_journey"]:
                metrics["customer_journey"][customer_id] = []
            metrics["customer_journey"][customer_id].append({
                "event": event_type,
                "time": event["properties"]["time"],
                "product": product_title
            })
    
    # Generate HTML for basic metrics
    basic_metrics_html = f"""
        <ul class="space-y-2">
            <li>Total Events: {sum(metrics["events_by_type"].values())}</li>
            <li>Product Views: {metrics["total_views"]}</li>
            <li>Average Views per Customer: {metrics["total_views"] / len(metrics["unique_customers"]):.2f}</li>
        </ul>
    """
    
    # Generate HTML for cohort analysis
    cohort_analysis_html = f"""
        <ul class="space-y-2">
            <li>Total UTM Sources: {len(metrics["utm_sources"])}</li>
            <li>Customers with Multiple Views: {sum(1 for journey in metrics["customer_journey"].values() if len(journey) > 1)}</li>
        </ul>
    """
    
    return {
        "total_views": metrics["total_views"],
        "unique_customers": len(metrics["unique_customers"]),
        "unique_products": len(metrics["products_viewed"]),
        "utm_sources": len(metrics["utm_sources"]),
        "basic_metrics_html": basic_metrics_html,
        "cohort_analysis_html": cohort_analysis_html
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
        
        # Get enhanced metrics
        metrics = process_data(data)
        
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
