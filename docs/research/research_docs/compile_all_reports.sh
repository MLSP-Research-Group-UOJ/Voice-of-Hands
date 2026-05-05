#!/bin/bash

# Compile all Voice-of-Hands research reports
# This script compiles all LaTeX reports in the research_docs folder

echo "============================================"
echo "Voice-of-Hands Research Reports Compilation"
echo "============================================"
echo ""

# Check if pdflatex is installed
if ! command -v pdflatex &> /dev/null; then
    echo "ERROR: pdflatex not found. Please install texlive:"
    echo "  sudo apt-get install texlive-full"
    exit 1
fi

# Array of report files
reports=(
    "01_pip_detection_development_report.tex"
    "02_sign_activity_detection_report.tex"
    "03_temporal_segmentation_strategy_report.tex"
    "04_latex_unicode_compilation_report.tex"
    "05_audio_extraction_synchronization_report.tex"
    "06_whisper_asr_integration_report.tex"
)

# Counters
total=${#reports[@]}
success=0
failed=0

# Compile each report
for report in "${reports[@]}"; do
    if [ ! -f "$report" ]; then
        echo "⚠  Skipping $report (file not found)"
        ((failed++))
        continue
    fi
    
    echo "Compiling: $report"
    
    # First pass
    pdflatex -interaction=nonstopmode "$report" > /dev/null 2>&1
    
    # Second pass (for table of contents)
    pdflatex -interaction=nonstopmode "$report" > /dev/null 2>&1
    
    # Check if PDF was generated
    pdf_name="${report%.tex}.pdf"
    if [ -f "$pdf_name" ]; then
        size=$(ls -lh "$pdf_name" | awk '{print $5}')
        echo "✓ Generated $pdf_name ($size)"
        ((success++))
    else
        echo "✗ Failed to generate $pdf_name"
        echo "  Run: pdflatex $report"
        echo "  to see detailed error messages"
        ((failed++))
    fi
    
    echo ""
done

# Cleanup auxiliary files
echo "Cleaning up auxiliary files..."
rm -f *.aux *.log *.out *.toc *.lof *.lot

echo "============================================"
echo "Compilation Summary"
echo "============================================"
echo "Total reports: $total"
echo "Successful: $success"
echo "Failed: $failed"

if [ $failed -eq 0 ]; then
    echo ""
    echo "✓ All reports compiled successfully!"
    echo ""
    echo "Generated PDFs:"
    ls -lh *.pdf 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
    exit 0
else
    echo ""
    echo "⚠ Some reports failed to compile."
    echo "Check individual error messages above."
    exit 1
fi
