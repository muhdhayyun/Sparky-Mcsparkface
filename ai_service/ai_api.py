"""
Flask API for AI Service
Provides endpoints for appliance consumption lookup and recommendations
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from ai_service import ApplianceAIService

app = Flask(__name__)
CORS(app)

# Initialize AI service
ai_service = ApplianceAIService()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "AI Service"})

@app.route('/api/ai/appliance-consumption', methods=['POST'])
def get_appliance_consumption():
    """
    Get energy consumption data for an appliance
    
    Request body:
    {
        "appliance_name": "Air Conditioner",
        "hours": 3,
        "date": "2026-03-08"
    }
    """
    try:
        data = request.json
        appliance_name = data.get('appliance_name')
        hours = data.get('hours', 1)
        date = data.get('date')
        user_id = data.get('user_id')
        
        if not appliance_name:
            return jsonify({"error": "Missing appliance_name"}), 400
        
        result = ai_service.process_new_appliance(appliance_name, hours, date)
        result["user_id"] = user_id
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai/recommendations', methods=['GET'])
def get_recommendations():
    """
    Get personalized energy-saving recommendations
    
    Returns AI-generated recommendations based on user's appliance usage
    """
    try:
        dataset_id = request.args.get('dataset')

        # Get user appliances from backend API
        appliance_context = ai_service.get_backend_appliance_context(dataset_id)
        user_appliances = appliance_context.get('appliances', [])
        
        # Generate recommendations
        recommendations = ai_service.generate_personalized_recommendations(
            user_appliances,
            appliance_context.get('summary'),
            ai_service.calculate_dataset_comparison(dataset_id)
        )
        
        return jsonify({
            "recommendations": recommendations,
            "appliance_count": len(user_appliances),
            "based_on": user_appliances[:5],  # Show first 5 for context
            "context_summary": appliance_context.get('summary', {}),
            "dataset": dataset_id,
            "user_id": appliance_context.get('user_id', dataset_id)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai/datasets', methods=['GET'])
def list_datasets():
    """List available processed datasets for manual selection."""
    try:
        return jsonify({
            "datasets": ai_service.list_available_datasets()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai/search-appliance', methods=['POST'])
def search_appliance():
    """
    Search for appliance energy consumption data
    
    Request body:
    {
        "appliance_name": "Washing Machine"
    }
    """
    try:
        data = request.json
        appliance_name = data.get('appliance_name')
        
        if not appliance_name:
            return jsonify({"error": "Missing appliance_name"}), 400
        
        result = ai_service.search_appliance_consumption(appliance_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai/sync-knowledge', methods=['POST'])
def sync_knowledge():
    """
    Sync all appliances from database to Pinecone
    Useful for initial setup or re-indexing
    """
    try:
        user_appliances = ai_service.get_user_appliances()
        
        synced_count = 0
        for appliance in user_appliances:
            consumption_data = ai_service.search_appliance_consumption(appliance['appliance_name'])
            ai_service.store_appliance_knowledge({
                **consumption_data,
                "hours_used": appliance['hours'],
                "date": appliance['date']
            })
            synced_count += 1
        
        return jsonify({
            "success": True,
            "synced_count": synced_count,
            "message": f"Synced {synced_count} appliances to Pinecone"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("="*80)
    print("AI Service API Starting...")
    print("="*80)
    print("Endpoints:")
    print("  GET  /health                         - Health check")
    print("  POST /api/ai/appliance-consumption   - Get consumption & store in Pinecone")
    print("  GET  /api/ai/recommendations         - Get personalized recommendations")
    print("  POST /api/ai/search-appliance        - Search appliance data")
    print("  POST /api/ai/sync-knowledge          - Sync DB to Pinecone")
    print("="*80)
    print("Note: Using port 5001 (port 5000 is used by macOS AirPlay Receiver)")
    print("="*80)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
