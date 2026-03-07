"""
AI Service for Appliance Energy Analysis and Recommendations
Uses Pinecone for vector storage and RAG-based recommendations
"""
import os
import sqlite3
import requests
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Tuple
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv

from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

load_dotenv()

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Configuration
INDEX_NAME = "appliance-energy"
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
DB_PATH = "../backend/appliances.db"
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")  # Optional: for web search
PROCESSED_DATA_DIR = Path("../data/processed")

class ApplianceAIService:
    """AI service for appliance energy analysis and recommendations"""
    
    def __init__(self):
        self.setup_pinecone()
        
    def setup_pinecone(self):
        """Initialize Pinecone index"""
        try:
            # Check if index exists
            existing_indexes = pc.list_indexes().names()
            
            if INDEX_NAME not in existing_indexes:
                print(f"Creating new Pinecone index: {INDEX_NAME}")
                pc.create_index(
                    name=INDEX_NAME,
                    dimension=1536,  # Dimension for text-embedding-3-small
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                print(f"✓ Index {INDEX_NAME} created")
            else:
                print(f"✓ Using existing index: {INDEX_NAME}")
            
            self.index = pc.Index(INDEX_NAME)
        except Exception as e:
            print(f"Error setting up Pinecone: {e}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI"""
        try:
            response = openai_client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
    
    def search_appliance_consumption_online(self, appliance_name: str) -> Dict[str, Any]:
        """
        Search online for appliance energy consumption using Tavily API
        Falls back to GPT-based search if Tavily is not configured
        """
        try:
            if TAVILY_API_KEY:
                # Use Tavily API for web search
                search_query = f"{appliance_name} average energy consumption kwh per hour"
                
                response = requests.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": TAVILY_API_KEY,
                        "query": search_query,
                        "search_depth": "basic",
                        "max_results": 5
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    search_results = response.json()
                    
                    # Combine search results into context
                    context = ""
                    for result in search_results.get("results", [])[:3]:
                        context += f"Source: {result.get('url', 'N/A')}\n"
                        context += f"{result.get('content', '')}\n\n"
                    
                    # Use GPT to extract structured data from search results
                    extraction_prompt = f"""Extract the average energy consumption for {appliance_name} from the following search results.

Search Results:
{context}

Extract and return ONLY a JSON object with this exact format (no markdown, no explanation):
{{
    "appliance": "{appliance_name}",
    "kwh_per_hour": <number>,
    "source": "<brief source citation>",
    "found": true
}}

If you cannot find specific data, return:
{{
    "appliance": "{appliance_name}",
    "kwh_per_hour": 1.0,
    "source": "Estimated - data not found",
    "found": false
}}"""

                    extraction_response = openai_client.chat.completions.create(
                        model=CHAT_MODEL,
                        messages=[
                            {"role": "system", "content": "You are a data extraction assistant. Return only valid JSON, no markdown formatting."},
                            {"role": "user", "content": extraction_prompt}
                        ],
                        temperature=0.1,
                        max_tokens=200
                    )
                    
                    import json
                    result_text = extraction_response.choices[0].message.content.strip()
                    # Remove markdown code blocks if present
                    if result_text.startswith("```"):
                        result_text = result_text.split("```")[1]
                        if result_text.startswith("json"):
                            result_text = result_text[4:]
                        result_text = result_text.strip()
                    
                    result = json.loads(result_text)
                    print(f"✓ Found online data for {appliance_name}: {result['kwh_per_hour']} kWh/hour")
                    return result
                else:
                    print(f"Tavily API error: {response.status_code}")
                    return self._fallback_search(appliance_name)
            else:
                # Fallback: Use GPT with its knowledge
                return self._fallback_search(appliance_name)
                
        except Exception as e:
            print(f"Error in online search: {e}")
            return self._fallback_search(appliance_name)
    
    def _fallback_search(self, appliance_name: str) -> Dict[str, Any]:
        """
        Fallback method using GPT's knowledge when web search is unavailable
        """
        try:
            prompt = f"""What is the average energy consumption of a {appliance_name} in kWh per hour?

Return ONLY a JSON object with this exact format (no markdown, no explanation):
{{
    "appliance": "{appliance_name}",
    "kwh_per_hour": <number>,
    "source": "GPT Knowledge Base",
    "found": true
}}

Base your answer on typical residential appliances."""

            response = openai_client.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "You are an energy efficiency expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=150
            )
            
            import json
            result_text = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
                result_text = result_text.strip()
            
            result = json.loads(result_text)
            print(f"✓ Used GPT fallback for {appliance_name}: {result['kwh_per_hour']} kWh/hour")
            return result
        except Exception as e:
            print(f"Error in fallback search: {e}")
            # Last resort: return default estimate
            return {
                "appliance": appliance_name,
                "kwh_per_hour": 1.0,
                "source": "Default estimate",
                "found": False,
                "note": "Could not determine consumption. Using default estimate."
            }
    
    def search_appliance_consumption(self, appliance_name: str) -> Dict[str, Any]:
        """
        Main method to search for appliance energy consumption
        Tries online search first, falls back to GPT knowledge
        """
        return self.search_appliance_consumption_online(appliance_name)
    
    def store_appliance_knowledge(self, appliance_data: Dict[str, Any]):
        """Store appliance consumption data in Pinecone"""
        try:
            # Create rich text for embedding
            text = f"""
            Appliance: {appliance_data['appliance']}
            Energy Consumption: {appliance_data['kwh_per_hour']} kWh per hour
            Source: {appliance_data['source']}
            Date: {datetime.now().isoformat()}
            """
            
            embedding = self.get_embedding(text)
            
            # Store in Pinecone
            self.index.upsert(
                vectors=[{
                    "id": f"appliance_{appliance_data['appliance'].lower().replace(' ', '_')}_{datetime.now().timestamp()}",
                    "values": embedding,
                    "metadata": appliance_data
                }]
            )
            
            print(f"✓ Stored {appliance_data['appliance']} knowledge in Pinecone")
        except Exception as e:
            print(f"Error storing appliance knowledge: {e}")
    
    def get_user_appliances(self) -> List[Dict[str, Any]]:
        """Fetch appliances from SQLite database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM appliance_usage ORDER BY date DESC")
            rows = cursor.fetchall()
            
            appliances = [dict(row) for row in rows]
            conn.close()
            
            return appliances
        except Exception as e:
            print(f"Error fetching appliances from database: {e}")
            return []
    
    def calculate_peak_grid_hours(self) -> Tuple[List[int], Dict[str, Any]]:
        """
        Calculate actual peak grid hours from household CSV data
        Returns peak hours and usage statistics
        """
        try:
            print("Analyzing household data to determine peak grid hours...")
            
            # Get all CSV files
            csv_files = list(PROCESSED_DATA_DIR.glob("*.csv"))
            
            if not csv_files:
                print("Warning: No CSV files found. Using default peak hours.")
                return ([17, 18, 19, 20], {"method": "default", "reason": "No CSV data available"})
            
            # Aggregate usage by hour across all households
            hourly_usage = defaultdict(list)
            
            for csv_file in csv_files:
                try:
                    df = pd.read_csv(csv_file)
                    
                    if len(df) == 0:
                        continue
                    
                    # Get column names
                    timestamp_col = df.columns[0]
                    energy_col = df.columns[1]
                    
                    # Parse timestamps
                    df['parsed_date'] = pd.to_datetime(df[timestamp_col], format='%d/%m/%Y %H:%M:%S')
                    df['hour'] = df['parsed_date'].dt.hour
                    df['energy_wh'] = pd.to_numeric(df[energy_col], errors='coerce')
                    
                    # Sum energy by hour for this household
                    hourly_sums = df.groupby('hour')['energy_wh'].sum()
                    
                    for hour, total_wh in hourly_sums.items():
                        hourly_usage[hour].append(total_wh)
                    
                except Exception as e:
                    print(f"Warning: Could not process {csv_file.name}: {e}")
                    continue
            
            if not hourly_usage:
                print("Warning: No valid data processed. Using default peak hours.")
                return ([17, 18, 19, 20], {"method": "default", "reason": "No valid data processed"})
            
            # Calculate average usage per hour across all households
            hourly_averages = {}
            for hour, usage_list in hourly_usage.items():
                hourly_averages[hour] = sum(usage_list) / len(usage_list)
            
            # Sort by usage (highest first)
            sorted_hours = sorted(hourly_averages.items(), key=lambda x: x[1], reverse=True)
            
            # Get top 4 peak hours
            peak_hours = [hour for hour, _ in sorted_hours[:4]]
            peak_hours.sort()  # Sort chronologically
            
            # Build statistics
            stats = {
                "method": "calculated",
                "peak_hours": peak_hours,
                "peak_hours_formatted": [f"{h:02d}:00-{h+1:02d}:00" for h in peak_hours],
                "households_analyzed": len(csv_files),
                "hourly_averages_kwh": {h: round(avg / 1000, 2) for h, avg in sorted(hourly_averages.items())},
                "top_5_hours": [{"hour": h, "avg_kwh": round(avg / 1000, 2)} for h, avg in sorted_hours[:5]]
            }
            
            print(f"✓ Peak hours calculated: {stats['peak_hours_formatted']}")
            print(f"  Analyzed {stats['households_analyzed']} households")
            
            return (peak_hours, stats)
            
        except Exception as e:
            print(f"Error calculating peak hours: {e}")
            print("Falling back to default peak hours (5-9 PM)")
            return ([17, 18, 19, 20], {"method": "default", "reason": f"Error: {str(e)}"})
    
    def generate_personalized_recommendations(self, user_appliances: List[Dict[str, Any]]) -> str:
        """
        Generate personalized energy-saving recommendations using RAG
        Considers user's appliance usage and actual grid load patterns from data
        """
        try:
            # Calculate actual peak hours from CSV data
            peak_hours, peak_stats = self.calculate_peak_grid_hours()
            peak_hours_str = ", ".join([f"{h:02d}:00-{h+1:02d}:00" for h in peak_hours])
            
            # Build context from user appliances
            appliance_summary = []
            total_energy = 0
            
            # Static appliance database for fallback
            APPLIANCE_DATABASE = {
                "air conditioner": 3.5, "ac": 3.5, "cooling": 3.5,
                "washing machine": 0.5, "washer": 0.5,
                "refrigerator": 0.15, "fridge": 0.15,
                "television": 0.1, "tv": 0.1,
                "oven": 2.3, "stove": 2.3,
                "dishwasher": 1.8,
                "dryer": 3.0, "clothes dryer": 3.0,
                "microwave": 1.2,
                "water heater": 4.0, "heater": 4.0,
                "computer": 0.2, "desktop": 0.2,
                "laptop": 0.05,
            }
            
            for app in user_appliances[:10]:  # Last 10 entries
                try:
                    consumption = self.search_appliance_consumption(app['appliance_name'])
                    estimated_kwh = consumption['kwh_per_hour'] * app['hours']
                except:
                    # Fallback to static database if API fails
                    app_lower = app['appliance_name'].lower()
                    kwh_per_hour = APPLIANCE_DATABASE.get(app_lower, 1.0)
                    estimated_kwh = kwh_per_hour * app['hours']
                
                total_energy += estimated_kwh
                
                appliance_summary.append({
                    "name": app['appliance_name'],
                    "date": app['date'],
                    "hours": app['hours'],
                    "estimated_kwh": round(estimated_kwh, 2)
                })
            
            try:
                # Try to use OpenAI
                # Query Pinecone for relevant energy-saving tips
                query_text = f"Energy saving tips for appliances: {', '.join([a['name'] for a in appliance_summary])}"
                query_embedding = self.get_embedding(query_text)
                
                # Search similar knowledge
                search_results = self.index.query(
                    vector=query_embedding,
                    top_k=5,
                    include_metadata=True
                )
                
                # Build RAG context
                rag_context = "Relevant appliance energy data:\n"
                for match in search_results.matches:
                    if match.metadata:
                        rag_context += f"- {match.metadata.get('appliance', 'Unknown')}: {match.metadata.get('kwh_per_hour', 'N/A')} kWh/hour\n"
                
                # Generate recommendations using GPT
                prompt = f"""You are an energy efficiency expert providing personalized recommendations to reduce electricity usage and avoid grid strain.

User's Appliance Usage (recent):
{appliance_summary}

Total estimated energy: {round(total_energy, 2)} kWh

{rag_context}

ACTUAL PEAK GRID HOURS (calculated from real household data):
{peak_hours_str}
These are the hours when electricity demand is highest across {peak_stats['households_analyzed']} households in the dataset.

Provide 5 specific, actionable recommendations that:
1. Help reduce energy consumption
2. Avoid the ACTUAL peak grid hours listed above (not generic peak times)
3. Are tailored to their specific appliances
4. Include estimated savings
5. Reference the specific peak hours when suggesting schedule changes

Keep responses concise and practical. When suggesting time shifts, explicitly mention avoiding the peak hours: {peak_hours_str}"""

                response = openai_client.chat.completions.create(
                    model=CHAT_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an energy efficiency expert focused on practical, actionable advice based on real data."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=800
                )
                
                # Prepend peak hours info to recommendations
                recommendations = f"**Peak Grid Hours (Based on Real Data):** {peak_hours_str}\n"
                recommendations += f"*Analyzed {peak_stats['households_analyzed']} households to determine actual peak demand times*\n\n"
                recommendations += response.choices[0].message.content
                
                return recommendations
            
            except Exception as ai_error:
                # Fallback to rule-based recommendations if OpenAI is unavailable
                print(f"OpenAI unavailable, using fallback recommendations: {ai_error}")
                
                # Generate simple rule-based recommendations
                recommendations = f"**Peak Grid Hours (Based on Real Data):** {peak_hours_str}\n"
                recommendations += f"*Analyzed {peak_stats['households_analyzed']} households to determine actual peak demand times*\n\n"
                recommendations += "*Note: Using offline recommendations mode (OpenAI API unavailable)*\n\n"
                
                recs = []
                appliance_names = [a['name'].lower() for a in appliance_summary]
                
                # Generate appliance-specific recommendations
                if any('air conditioner' in name or 'ac' in name or 'cooling' in name for name in appliance_names):
                    recs.append(f"1. **Adjust AC Temperature**: Raise your thermostat by 2°C during peak hours ({peak_hours_str}). This can reduce cooling costs by 10-15% while maintaining comfort.")
                    recs.append(f"2. **Pre-cool Strategy**: Cool your home 1 hour before peak hours begin, then coast through peak times. Can save $5-8/week.")
                
                if any('washing' in name or 'washer' in name for name in appliance_names):
                    recs.append(f"3. **Shift Laundry Schedule**: Run your washing machine after peak hours end (after {peak_hours[-1]+1}:00). Use cold water to save 90% of washing energy.")
                
                if any('oven' in name or 'stove' in name or 'dishwasher' in name for name in appliance_names):
                    recs.append(f"4. **Cook During Off-Peak**: Use oven and dishwasher before {peak_hours[0]}:00 or after {peak_hours[-1]+1}:00. Consider meal prep to reduce cooking frequency.")
                
                # Generic recommendations
                if len(recs) < 5:
                    recs.append(f"5. **Unplug Phantom Loads**: Devices on standby can account for 10% of your bill. Unplug chargers and electronics when not in use. Estimated savings: $3-5/week.")
                
                if len(appliance_summary) > 3:
                    recs.append(f"6. **Monitor Your Usage**: You're tracking {len(appliance_summary)} appliances totaling {round(total_energy, 1)} kWh. Focus on high-energy items first for maximum impact.")
                
                # Take top 5
                recommendations += "\n\n".join(recs[:5])
                
                return recommendations
                
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            import traceback
            traceback.print_exc()
            return f"Error generating recommendations: {str(e)}"
    
    def process_new_appliance(self, appliance_name: str, hours: int, date: str):
        """Process newly added appliance: lookup consumption and store in Pinecone"""
        try:
            # Search for consumption data
            consumption_data = self.search_appliance_consumption(appliance_name)
            
            # Calculate estimated energy
            estimated_kwh = consumption_data['kwh_per_hour'] * hours
            
            # Store in Pinecone for future RAG
            self.store_appliance_knowledge({
                **consumption_data,
                "hours_used": hours,
                "date": date,
                "estimated_kwh": estimated_kwh
            })
            
            return {
                "success": True,
                "consumption_data": consumption_data,
                "estimated_kwh": round(estimated_kwh, 2)
            }
        except Exception as e:
            print(f"Error processing new appliance: {e}")
            return {
                "success": False,
                "error": str(e)
            }

def main():
    """Test the AI service"""
    print("="*80)
    print("AI Service for Appliance Energy Analysis")
    print("="*80)
    
    service = ApplianceAIService()
    
    # Test: Process a sample appliance
    print("\n1. Testing appliance consumption lookup...")
    result = service.process_new_appliance("Air Conditioner", 3, "2026-03-08")
    print(f"Result: {result}")
    
    # Test: Get user appliances and generate recommendations
    print("\n2. Generating personalized recommendations...")
    user_appliances = service.get_user_appliances()
    
    if user_appliances:
        recommendations = service.generate_personalized_recommendations(user_appliances)
        print("\n" + "="*80)
        print("PERSONALIZED RECOMMENDATIONS:")
        print("="*80)
        print(recommendations)
    else:
        print("No appliances found in database. Add some appliances first!")
    
    print("\n" + "="*80)
    print("✓ AI Service test completed")

if __name__ == "__main__":
    main()
