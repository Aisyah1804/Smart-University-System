from flask import Flask, render_template
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, '..', 'data', 'student.csv')
    file_path = os.path.abspath(file_path)

    df = pd.read_csv(file_path)

    return render_template(
        'index.html',
        # Set index=False here to fix the column shift!
        tables=[df.to_html(classes='data', index=False, border=0)], 
        titles=df.columns.values,
        year=datetime.now().year
    )

if __name__ == '__main__':
    app.run(debug=True)