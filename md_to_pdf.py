#!/usr/bin/env python3
"""
Convert Markdown to PDF
Simple converter for documentation files
"""

import os
import sys
import subprocess
import markdown
import tempfile

def markdown_to_html(md_file):
    """Convert markdown to HTML"""
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML with tables, fenced code, and other extensions
    html_content = markdown.markdown(
        md_content,
        extensions=[
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
            'markdown.extensions.nl2br'
        ]
    )
    
    # Create a complete HTML document with styling
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Voice-of-Hands Project Documentation</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 40px auto;
            padding: 0 20px;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 40px;
        }}
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 8px;
            margin-top: 30px;
        }}
        h3 {{
            color: #555;
            margin-top: 25px;
        }}
        h4 {{
            color: #666;
            margin-top: 20px;
        }}
        h5 {{
            color: #777;
            font-size: 1.1em;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        pre {{
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin-left: 0;
            color: #666;
            font-style: italic;
        }}
        hr {{
            border: none;
            border-top: 2px solid #eee;
            margin: 30px 0;
        }}
        .emoji {{
            font-size: 1.2em;
        }}
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        li {{
            margin: 8px 0;
        }}
        strong {{
            color: #2c3e50;
        }}
        @media print {{
            body {{
                max-width: 100%;
                margin: 0;
            }}
            h1, h2, h3 {{
                page-break-after: avoid;
            }}
            pre, blockquote {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
    
    return full_html

def html_to_pdf_chromium(html_content, output_pdf):
    """Convert HTML to PDF using Chromium/Chrome"""
    chromium_paths = [
        'google-chrome',
        'google-chrome-stable',
        'chromium-browser',
        'chromium',
        '/usr/bin/google-chrome',
        '/usr/bin/chromium-browser',
    ]
    
    chrome_cmd = None
    for path in chromium_paths:
        try:
            subprocess.run([path, '--version'], capture_output=True, check=True)
            chrome_cmd = path
            break
        except:
            continue
    
    if not chrome_cmd:
        return False
    
    # Create temporary HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        temp_html = f.name
        f.write(html_content)
    
    try:
        subprocess.run([
            chrome_cmd,
            '--headless',
            '--disable-gpu',
            '--no-sandbox',
            '--print-to-pdf=' + os.path.abspath(output_pdf),
            '--print-to-pdf-no-header',
            f'file://{os.path.abspath(temp_html)}'
        ], check=True, timeout=30)
        return True
    except Exception as e:
        print(f"Chromium conversion failed: {e}")
        return False
    finally:
        if os.path.exists(temp_html):
            os.remove(temp_html)

def main():
    if len(sys.argv) < 2:
        print("Usage: python md_to_pdf.py <markdown_file>")
        print("Example: python md_to_pdf.py PROJECT_DEVELOPMENT_TIMELINE.md")
        sys.exit(1)
    
    md_file = sys.argv[1]
    if not os.path.exists(md_file):
        print(f"Error: File '{md_file}' not found")
        sys.exit(1)
    
    # Generate output PDF name
    pdf_file = os.path.splitext(md_file)[0] + '.pdf'
    
    print(f"Converting '{md_file}' to PDF...")
    print()
    
    # Convert markdown to HTML
    print("Step 1: Converting Markdown to HTML...")
    try:
        html_content = markdown_to_html(md_file)
        print("✅ HTML generated")
    except Exception as e:
        print(f"❌ Failed to convert Markdown: {e}")
        sys.exit(1)
    
    # Convert HTML to PDF
    print("Step 2: Converting HTML to PDF...")
    if html_to_pdf_chromium(html_content, pdf_file):
        if os.path.exists(pdf_file):
            size = os.path.getsize(pdf_file)
            print(f"\n✅ Successfully created PDF!")
            print(f"   Input:  {md_file}")
            print(f"   Output: {pdf_file}")
            print(f"   Size:   {size / 1024:.1f} KB")
            return 0
    
    print("\n❌ Failed to convert to PDF")
    print("Please install chromium or google-chrome")
    return 1

if __name__ == '__main__':
    sys.exit(main())
