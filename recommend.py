import folium
import pandas as pd

def recommend_restaurants(df, borough, cuisine, weight_of_review, weight_of_inspection):
    # Filter restaurants based on the user's preferences
    filtered_df = df[
        (df['BORO'] == borough) &
        (df['CUISINE DESCRIPTION'].isin(cuisine))
    ]
    
    if filtered_df.empty:
        return pd.DataFrame(), "No results found for the selected criteria."

    # Map letter grades to numerical values
    mapping = {"A": 5, "B": 3, "C": 1}
    filtered_df["Inspection Score"] = filtered_df["final_grade"].map(mapping)
    
    # Calculate the user preference score based on weightage of inspection and review
    filtered_df["user_preference"] = (
        filtered_df["Inspection Score"] * (weight_of_inspection / 10) +
        filtered_df["rating"] * (weight_of_review / 10)
    )
    filtered_df["user_preference"] = filtered_df["user_preference"] * 10

    # Sort by user preference score
    top_restaurants = filtered_df.sort_values('user_preference', ascending=False).reset_index()
    results = top_restaurants[['name', 'address', 'latitude', 'longitude', 'CUISINE DESCRIPTION', 'BORO', 'user_preference', 'reviews', "rating", "final_grade"]]

    # Create a Folium map
    avg_lat = results['latitude'].mean()
    avg_lon = results['longitude'].mean()
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)

    # Loop through the rows of results to plot each point
    for index, row in results.iterrows():
        latitude = row['latitude']
        longitude = row['longitude']
        name = row['name']
        address = row['address']
        user_preference = row['user_preference']

        marker_color = 'green' if index < 5 else 'blue'
        marker_icon = 'star' if index < 5 else 'info-sign'

        folium.Marker(
            location=[latitude, longitude],
            icon=folium.Icon(color=marker_color, icon=marker_icon),
            popup=folium.Popup(
                f"Name: {name}<br>Address: {address}<br>Cuisine: {row['CUISINE DESCRIPTION']}<br>User Preference: {user_preference:.2f}%",
                max_width=200
            )
        ).add_to(m)

    map_html = m._repr_html_()



    # Return the results and the HTML representation of the map
    return results.head(5), map_html

