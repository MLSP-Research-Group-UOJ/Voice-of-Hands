#!/usr/bin/env python3
"""
Convert Mermaid Flowchart HTML to PDF
Uses weasyprint or playwright for conversion
"""

import os
import sys
import subprocess

def check_command(cmd):
    """Check if a command is available"""
    try:
        subprocess.run([cmd, '--version'], capture_output=True, check=True)
        return True
    except:
        return False

def convert_with_weasyprint():
    """Try converting with weasyprint"""
    try:
        from weasyprint import HTML
        print("Using weasyprint for conversion...")
        HTML('flowchart.html').write_pdf('SLI_Detection_Process_Flowchart.pdf')
        return True
    except ImportError:
        print("weasyprint not available")
        return False
    except Exception as e:
        print(f"weasyprint conversion failed: {e}")
        return False

def convert_with_wkhtmltopdf():
    """Try converting with wkhtmltopdf"""
    if check_command('wkhtmltopdf'):
        print("Using wkhtmltopdf for conversion...")
        try:
            subprocess.run([
                'wkhtmltopdf',
                '--enable-local-file-access',
                '--page-size', 'A3',
                '--orientation', 'Portrait',
                '--margin-top', '10',
                '--margin-bottom', '10',
                '--margin-left', '10',
                '--margin-right', '10',
                '--javascript-delay', '3000',
                'flowchart.html',
                'SLI_Detection_Process_Flowchart.pdf'
            ], check=True)
            return True
        except Exception as e:
            print(f"wkhtmltopdf conversion failed: {e}")
            return False
    else:
        print("wkhtmltopdf not available")
        return False

def convert_with_chromium():
    """Try converting with chromium headless"""
    chromium_paths = [
        'chromium-browser',
        'chromium',
        'google-chrome',
        'google-chrome-stable',
        '/usr/bin/chromium-browser',
        '/usr/bin/chromium',
        '/usr/bin/google-chrome',
    ]
    
    chrome_cmd = None
    for path in chromium_paths:
        if check_command(path) or os.path.exists(path):
            chrome_cmd = path
            break
    
    if chrome_cmd:
        print(f"Using {chrome_cmd} for conversion...")
        try:
            html_path = os.path.abspath('flowchart.html')
            pdf_path = os.path.abspath('SLI_Detection_Process_Flowchart.pdf')
            
            subprocess.run([
                chrome_cmd,
                '--headless',
                '--disable-gpu',
                '--no-sandbox',
                '--print-to-pdf=' + pdf_path,
                '--print-to-pdf-no-header',
                f'file://{html_path}'
            ], check=True, timeout=30)
            return True
        except Exception as e:
            print(f"Chromium conversion failed: {e}")
            return False
    else:
        print("Chromium/Chrome not available")
        return False

def main():
    print("Converting Mermaid flowchart to PDF...\n")
    
    # Try different methods in order of preference
    methods = [
        convert_with_chromium,     # Best quality for Mermaid
        convert_with_wkhtmltopdf,  # Good alternative
        convert_with_weasyprint,   # May not support Mermaid JS
    ]
    
    for method in methods:
        if method():
            if os.path.exists('SLI_Detection_Process_Flowchart.pdf'):
                size = os.path.getsize('SLI_Detection_Process_Flowchart.pdf')
                print(f"\n✅ Successfully created PDF!")
                print(f"   File: SLI_Detection_Process_Flowchart.pdf")
                print(f"   Size: {size / 1024:.1f} KB")
                return 0
    
    print("\n❌ Failed to convert to PDF using available tools.")
    print("\nAlternative: Open flowchart.html in a browser and use 'Print to PDF'")
    print("   File location: " + os.path.abspath('flowchart.html'))
    return 1

if __name__ == '__main__':
    sys.exit(main())
