import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output

# Load the dataset
data = pd.read_csv('moviesdata.csv')


# Preprocessing: Clean the dataset
data['Gross'] = data['Gross'].replace(',', '', regex=True).replace('$', '', regex=True).astype(float, errors='ignore')
data['No_of_Votes'] = pd.to_numeric(data['No_of_Votes'], errors='coerce')
data['Runtime'] = data['Runtime'].str.replace(' min', '').astype(float, errors='ignore')
data['Released_Year'] = pd.to_numeric(data['Released_Year'], errors='coerce')
data = data.dropna(subset=['Released_Year', 'Gross'])  

# Generate Decade column safely
data['Decade'] = (data['Released_Year'] // 10) * 10  

# Define a consistent vibrant color scheme
color_scheme = px.colors.qualitative.Vivid

# Custom color mapping for genres
genre_colors = {
    'Action': '#FF5733',
    'Adventure': '#33FF57',
    'Drama': '#337BFF',
    'Comedy': '#F39C12',
    'Horror': '#8E44AD',
    'Thriller': '#C0392B',
    'Animation': '#1ABC9C',
    'Sci-Fi': '#9B59B6',
    'Crime': '#34495E',
    'Romance': '#E74C3C'
}

# Filter dataset to include only genres with sufficient data for faceting
genre_counts = data['Genre'].value_counts()
selected_genres = genre_counts[genre_counts > 10].index.tolist()  
data_filtered = data[data['Genre'].isin(selected_genres)]

# 1. Treemap: Genre-wise Gross and Number of Movies
treemap = px.treemap(
    data,
    path=['Genre'],
    values='Gross',
    color='No_of_Votes',
    color_continuous_scale='Viridis',
    title="Genre-wise Gross and Number of Votes",
)
treemap.update_layout(
    title_font_size=22,
    title_x=0.4,
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white'),
    height=400,
)

# 2. Dynamic Scatterplot with Animation and Buttons
scatterplot = px.scatter(
    data,
    x='Runtime',
    y='IMDB_Rating',
    size='No_of_Votes',
    color='Gross',
    hover_data=['Series_Title', 'Director'],
    color_continuous_scale='Viridis',
    title="IMDB Rating vs Runtime",
    labels={'Runtime': 'Runtime (minutes)', 'IMDB_Rating': 'IMDB Rating'},
    animation_frame='Released_Year',
    animation_group='Series_Title',
)
scatterplot.update_layout(
    title_font_size=22, 
    title_x=0.4, 
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white'),
    height=400,
)
scatterplot.update_traces(marker=dict(line=dict(width=0.5, color='white')))

# 3. Facet Grid by Genre and Decade (using filtered data)
def create_facet_chart(selected_genre):
    filtered_data = data_filtered[data_filtered['Genre'] == selected_genre]
    
    selected_color = genre_colors.get(selected_genre, '#337BFF')  # Fallback to Drama color if missing

    # Use explicit color with `update_traces` instead of color_discrete_sequence
    facet_chart = px.bar(
        filtered_data,
        x='Decade',
        y='IMDB_Rating',
        hover_data=['Series_Title'],
        title=f"IMDB Rating by Decade for {selected_genre}",
        labels={'Decade': 'Decade', 'IMDB_Rating': 'Average IMDB Rating'},
    )
    
    # Update traces to apply the color dynamically
    facet_chart.update_traces(marker_color=selected_color)
    
    # Update layout
    facet_chart.update_layout(
        title_font_size=18, 
        title_x=0.4, 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        margin=dict(t=40, b=30, l=30, r=30),
        height=400, 
    )
    return facet_chart


# 4. Interactive Parallel Coordinates Plot
parallel_coordinates = px.parallel_coordinates(
    data,
    dimensions=['Runtime', 'IMDB_Rating', 'Gross', 'Meta_score', 'No_of_Votes'],
    color='IMDB_Rating',
    color_continuous_scale='Viridis',
    title="Relationships Among Attributes",
)
parallel_coordinates.update_layout(
    title_font_size=22, 
    title_x=0.4, 
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white'),
    height=400,
)

# 5. Dashboard Composition with Genre Filter
app = Dash(__name__)

app.layout = html.Div(
    style={
        'backgroundColor': 'black',
        'color': 'white',
        'font-family': 'Arial',
        'padding': '10px'
    },
    children=[
        html.H1("\ud83c\udfa5 IMDB Movie Analysis \ud83c\udfc6", style={'textAlign': 'center', 'fontSize': '32px', 'color': 'white'}),
        
        html.Div([
            dcc.Graph(figure=treemap, style={'width': '50%', 'display': 'inline-block', 'marginRight': '4px'}),
            dcc.Graph(figure=scatterplot, style={'width': '50%', 'display': 'inline-block'}),
        ], style={'display': 'flex', 'justify-content': 'space-between'}),

        html.Div([
            html.Label(" ", style={'fontSize': '18px', 'color': 'white'}),
            dcc.Dropdown(
                id='genre-dropdown',
                options=[{'label': genre, 'value': genre} for genre in selected_genres],
                value=selected_genres[0],
                style={
                    'width': '20%',
                    'marginBottom': '10px',
                    'fontSize': '14px',
                    'color': 'black', 
                }
            ),
        ], style={'textAlign': 'center'}),

        html.Div([
            dcc.Graph(id='facet-chart', style={'width': '48%', 'display': 'inline-block', 'marginRight': '4px'}),
            dcc.Graph(figure=parallel_coordinates, style={'width': '48%', 'display': 'inline-block'}),
        ], style={'display': 'flex', 'justify-content': 'space-between'}),
    ]
)

@app.callback(
    Output('facet-chart', 'figure'),
    Input('genre-dropdown', 'value')
)
def update_facet_chart(selected_genre):
    return create_facet_chart(selected_genre)

if __name__ == '__main__':
    app.run_server(debug=True)
