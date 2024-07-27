from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

app = Flask(__name__)


pleasures = pd.read_csv('pleasures.tsv', sep='|')
pleasures = zip(pleasures['name'], pleasures['description'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Process the form submission
        pleasure_results = []
        for pleasure, description in pleasures:
            fulfilled = request.form.get(f'{pleasure}_fulfilled') == 'on'
            comment = request.form.get(f'{pleasure}_comment', '')
            pleasure_results.append((pleasure, fulfilled, comment))

        # Calculate total score (count of fulfilled pleasures)
        total_score = sum(1 for _, fulfilled, _ in pleasure_results if fulfilled)

        # Write results to a text file
        with open('pleasure_results.txt', 'w') as f:
            for pleasure, fulfilled, comment in pleasure_results:
                f.write(f'{pleasure}\t{"Yes" if fulfilled else "No"}\t{comment}\n')

        # Redirect to results page
        return redirect(url_for('results', total_score=total_score))

    return render_template('index.html', pleasures=pleasures)

# Route for the results page
@app.route('/results/<int:total_score>')
def results(total_score):
    return render_template('results.html', total_score=total_score)

if __name__ == '__main__':
    app.run(debug=True)
