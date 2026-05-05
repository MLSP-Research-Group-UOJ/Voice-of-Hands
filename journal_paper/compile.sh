#!/bin/bash

# Voice-of-Hands LaTeX Compilation Script
# This script compiles the research paper with XeLaTeX for Unicode support

set -e  # Exit on error

echo "=========================================="
echo "Voice-of-Hands Paper Compilation Script"
echo "(Using XeLaTeX for Sinhala/Tamil Unicode)"
echo "=========================================="
echo ""

# Check if xelatex is installed
if ! command -v xelatex &> /dev/null; then
    echo "ERROR: xelatex not found. Please install a LaTeX distribution:"
    echo "  Ubuntu/Debian: sudo apt-get install texlive-full"
    echo "  macOS: brew install --cask mactex"
    exit 1
fi

# Check if bibtex is installed
if ! command -v bibtex &> /dev/null; then
    echo "ERROR: bibtex not found. Please install a LaTeX distribution."
    exit 1
fi

MAIN_FILE="voice_of_hands_paper"

echo "Step 1/4: First xelatex compilation..."
xelatex -interaction=nonstopmode ${MAIN_FILE}.tex > /dev/null 2>&1 || {
    echo "ERROR: First xelatex compilation failed. Check ${MAIN_FILE}.log for details."
    exit 1
}
echo "✓ First compilation complete"

echo ""
echo "Step 2/4: Running bibtex..."
bibtex ${MAIN_FILE} > /dev/null 2>&1 || {
    echo "ERROR: bibtex compilation failed. Check ${MAIN_FILE}.blg for details."
    exit 1
}
echo "✓ Bibliography processed"

echo ""
echo "Step 3/4: Second xelatex compilation..."
xelatex -interaction=nonstopmode ${MAIN_FILE}.tex > /dev/null 2>&1 || {
    echo "ERROR: Second xelatex compilation failed."
    exit 1
}
echo "✓ Second compilation complete"

echo ""
echo "Step 4/4: Final xelatex compilation..."
xelatex -interaction=nonstopmode ${MAIN_FILE}.tex > /dev/null 2>&1 || {
    echo "ERROR: Final xelatex compilation failed."
    exit 1
}
echo "✓ Final compilation complete"

echo ""
echo "=========================================="
echo "Compilation successful!"
echo "Output: ${MAIN_FILE}.pdf"
echo "=========================================="

# Show file size
if [ -f "${MAIN_FILE}.pdf" ]; then
    SIZE=$(du -h "${MAIN_FILE}.pdf" | cut -f1)
    echo "PDF size: ${SIZE}"
fi

echo ""
echo "To clean auxiliary files, run: ./compile.sh clean"
echo ""

# Check if clean argument is provided
if [ "$1" == "clean" ]; then
    echo "Cleaning auxiliary files..."
    rm -f *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot
    echo "✓ Cleanup complete"
fi
