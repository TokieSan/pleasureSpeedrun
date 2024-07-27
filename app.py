from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import pandas as pd
from io import StringIO
import markdown2

app = Flask(__name__)

pleasures = pd.read_csv('pleasures.tsv', sep='|')
pleasures = list(zip(pleasures['name'], pleasures['description']))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_pleasure/<int:index>')
def get_pleasure(index):
    if 0 <= index < len(pleasures):
        pleasure, description = pleasures[index]
        return jsonify({
            'name': pleasure,
            'description': description,
            'total': len(pleasures)
        })
    return jsonify({'error': 'Invalid index'}), 404

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    total_score = sum(1 for item in data if item['fulfilled'])
    
    # Write results to a text file
    with open('pleasure_results.txt', 'w') as f:
        for item in data:
            f.write(f"{item['name']}\t{'Yes' if item['fulfilled'] else 'No'}\t{item['comment']}\n")
    
    return jsonify({'total_score': total_score})

@app.route('/results/<int:total_score>')
def results(total_score):
    return render_template('results.html', total_score=total_score)

@app.route('/download_results')
def download_results():
    # Read the results from the text file
    with open('pleasure_results.txt', 'r') as f:
        results = f.readlines()
    
    # Create a Markdown string
    markdown_content = "# Pleasures Tracker Results\n\n"
    markdown_content += f"Total Pleasures Fulfilled: {sum(1 for line in results if 'Yes' in line)}\n\n"
    markdown_content += "## Detailed Responses\n\n"
    
    for line in results:
        parts = line.strip().split('\t')
        pleasure = parts[0]
        fulfilled = parts[1] if len(parts) > 1 else 'Unknown'
        comment = parts[2] if len(parts) > 2 else ''
        
        markdown_content += f"### {pleasure}\n\n"
        markdown_content += f"Fulfilled: {fulfilled}\n\n"
        if comment:
            markdown_content += f"Comment: {comment}\n\n"
    
    # Convert Markdown to HTML
    html_content = markdown2.markdown(markdown_content)
    
    # Create a response with the HTML content
    response = app.response_class(
        response=html_content,
        status=200,
        mimetype='text/html'
    )
    
    # Set the Content-Disposition header to make the browser download the file
    response.headers["Content-Disposition"] = "attachment; filename=pleasure_results.html"
    
    return response

if __name__ == '__main__':
    app.run(debug=True)
