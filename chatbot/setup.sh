#!/bin/bash
# Quick setup script for Sparky Energy Assistant chatbot

echo "🔧 Setting up Sparky Energy Assistant..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo ""
    echo "📝 Please edit the .env file and add your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - PINECONE_API_KEY"
    echo ""
    echo "   Run: nano .env"
    echo ""
else
    echo "✅ .env file found"
fi

# Check if knowledge base exists
if [ -d "knowledge_base" ] && [ "$(ls -A knowledge_base)" ]; then
    echo ""
    echo "📚 Knowledge base directory found with files"
    echo "   To ingest knowledge base, run after setting up .env:"
    echo "   python -c \"from rag_engine import ingest_directory; chunks, files = ingest_directory('knowledge_base'); print(f'Ingested {len(files)} files')\""
else
    echo "📚 Knowledge base directory is empty"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Ingest knowledge base (see above command)"
echo "3. Run: python api.py"
echo ""
