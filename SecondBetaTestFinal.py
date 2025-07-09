import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Load data
benzene = pd.read_csv("Suffolk County Benzene Trends 2000-2024.csv")
no2 = pd.read_csv("Suffolk County NO2 Trends 2000-2024.csv")
ozone = pd.read_csv("Suffolk County Ozone Trends 2000-2024.csv")
asthma_df = pd.read_csv("Suffolk County Asthma Hospitalizations 2000-2021.csv")

# Extract relevant columns and standardize

def prep(df, name):
    df = df[['date_local', 'arithmetic_mean']].copy()
    df['date_local'] = pd.to_datetime(df['date_local'])
    df['year'] = df['date_local'].dt.year
    df = df.groupby('year')['arithmetic_mean'].mean().reset_index()
    df['pollutant'] = name
    return df

benzene_df = prep(benzene, 'Benzene')
no2_df = prep(no2, 'NO2')
ozone_df = prep(ozone, 'Ozone')

# Combine all pollutants
all_data = pd.concat([benzene_df, no2_df, ozone_df], ignore_index=True)

# Filter asthma data for all ages and aggregate by year
asthma_df = asthma_df[['Year', 'Case Count']].copy()
asthma_df = asthma_df.groupby('Year')['Case Count'].sum().reset_index()
asthma_df.rename(columns={'Year': 'year', 'Case Count': 'hospitalizations'}, inplace=True)

# Dash app
app = Dash(__name__)
app.title = "Air Quality & Asthma Trends"

app.layout = html.Div([
    html.H1("Suffolk County Air Quality & Asthma Trends", style={"textAlign": "center", "marginBottom": "20px"}),

    html.Div([
        html.Div([
            dcc.Graph(id='pollutant-graph', config={'displayModeBar': False}),
            html.Label("Select Pollutant:", style={"fontWeight": "bold", "fontSize": "14px", "textAlign": "center", "display": "block", "marginTop": "10px"}),
            html.Div([
                dcc.Dropdown(
                    id='pollutant-dropdown',
                    options=[
                        {'label': 'Benzene', 'value': 'Benzene'},
                        {'label': 'NO2', 'value': 'NO2'},
                        {'label': 'Ozone', 'value': 'Ozone'}
                    ],
                    value='Ozone',
                    clearable=False,
                    style={"fontSize": "12px", "width": "60%", "margin": "0 auto"}
                )
            ], style={"textAlign": "center"})
        ], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),

        html.Div([
            dcc.Graph(
                id='asthma-graph',
                figure=px.line(
                    asthma_df,
                    x='year', y='hospitalizations',
                    title='Annual Asthma Hospitalizations in Suffolk County (2000–2021)',
                    markers=True,
                    labels={'year': 'Year', 'hospitalizations': 'Hospitalizations'},
                    line_shape='linear'
                ).update_traces(line_color='red').update_layout(
                    margin=dict(t=40), height=400, xaxis=dict(dtick=2), yaxis_title='Hospitalizations'
                ),
                config={'displayModeBar': False}
            )
        ], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'})
    ], style={"display": "flex", "justifyContent": "center"})
])

@app.callback(
    Output('pollutant-graph', 'figure'),
    Input('pollutant-dropdown', 'value')
)
def update_graph(pollutant):
    filtered = all_data[all_data['pollutant'] == pollutant]
    fig = px.line(
        filtered,
        x='year', y='arithmetic_mean',
        title=f'Average {pollutant} Concentration (2000–2024)',
        markers=True,
        labels={'year': 'Year', 'arithmetic_mean': 'Avg Concentration'},
        line_shape='linear'
    )
    fig.update_traces(line_color='green')
    fig.update_layout(margin=dict(t=40), height=400, xaxis=dict(dtick=2), yaxis_title='Concentration')
    return fig

if __name__ == '__main__':
    app.run(debug=True)