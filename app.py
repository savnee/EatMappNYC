import os
import sys
import pandas as pd
import webbrowser
from flask import Flask, render_template, request
from recommend import recommend_restaurants
import threading

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def borough_selection():
    boroughs = ["Manhattan", "Brooklyn", "Queens", "The Bronx", "Staten Island"]
    
    if request.method == 'POST':
        # Get the selected borough
        selected_borough = request.form.get('borough')
        
        # Get the list of selected cuisines from checkboxes
        selected_cuisines = request.form.getlist('cuisine')  # This is a list of selected cuisines
        
        # Check if both borough and cuisines are selected
        if selected_borough and selected_cuisines:
            # Pass the selected borough and cuisines to the next page (score_input.html)
            return render_template('score_input.html', borough=selected_borough, cuisines=selected_cuisines)
        else:
            # If either borough or cuisines are not selected, show an error message
            return render_template('borough_selection.html', boroughs=boroughs, error="Please select both a borough and cuisines.")
    
    # When the request is GET (i.e., first time visiting the page), just render the borough selection page
    return render_template('borough_selection.html', boroughs=boroughs)



@app.route('/input_scores', methods=['GET', 'POST'])
def score_input():
    if request.method == 'POST':
        borough = request.form.get('borough')
        cuisines = request.form.getlist('cuisines')
        cuisines = cuisines[0].split(',') if cuisines else []

        # Add check if borough or cuisines are not selected or empty
        if not borough or not cuisines:
            return render_template('score_input.html', error="Please select both a borough and cuisines.")
        
        # Get the Inspection Score and Review Score from the form
        try:
            inspection_score = float(request.form.get('inspection_score'))
            review_score = float(request.form.get('review_score'))
        except ValueError:
            return render_template('score_input.html', error="Please provide valid numeric values for scores.")

        # Adjust file path handling for both regular and bundled app
        if getattr(sys, 'frozen', False):
            # Running as a bundled executable
            base_path = sys._MEIPASS  # Temporary folder for bundled app
        else:
            # Running from source code
            base_path = os.getcwd()  # Current working directory
        
        file_path = os.path.join(base_path, 'data', 'final_reviews_df.csv')
        
        # Debugging log to check file path and data loading
        print(f"Attempting to load CSV file from: {file_path}")
        try:
            df = pd.read_csv(file_path)
            print("CSV file loaded successfully.")
        except FileNotFoundError:
            print("Error: CSV file not found.")
            return render_template('score_input.html', error="Data file not found.")

        # Get restaurant recommendations and map HTML
        recommendations, map_html = recommend_restaurants(df, borough, cuisines, inspection_score, review_score)

        if recommendations.empty:
            return render_template('score_input.html', error="No restaurants match your criteria.")
        
        # Convert the DataFrame to a list of dictionaries
        output_list = recommendations.to_dict(orient='records')

        # Render the result page with the output and map HTML
        return render_template('result.html', borough=borough, cuisines=cuisines, 
                               inspection_score=inspection_score, review_score=review_score, 
                               output=output_list, map_html=map_html)

    return render_template('score_input.html')


def open_browser():
    import time
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000/")


if __name__ == '__main__':
    threading.Thread(target=open_browser).start()
    app.run(debug=True, use_reloader=False, threaded=True)
