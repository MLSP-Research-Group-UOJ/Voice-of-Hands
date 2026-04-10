#!/bin/bash
# Installation and Setup Script for SLI Detector

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  Sign Language Interpreter Detection - Setup Script             ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo "✅ Python $python_version found"
else
    echo "❌ Python 3.8 or higher required (found $python_version)"
    exit 1
fi

# Create virtual environment (optional but recommended)
echo ""
echo "📦 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo ""
echo "Activate virtual environment with:"
echo "  source venv/bin/activate  (Linux/Mac)"
echo "  venv\\Scripts\\activate    (Windows)"
echo ""

# Install requirements
echo "📥 Installing required packages..."
if [ -f "venv/bin/pip" ]; then
    venv/bin/pip install -r requirements.txt
else
    pip3 install -r requirements.txt
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  Ready to use!                                                   ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Quick Start:"
echo "  python quick_start.py your_video.mp4 output_dataset"
echo ""
echo "📖 Documentation:"
echo "  See README_SLI_DETECTOR.md for detailed usage"
echo ""
echo "💡 Examples:"
echo "  python example_extract_sli.py"
echo ""
