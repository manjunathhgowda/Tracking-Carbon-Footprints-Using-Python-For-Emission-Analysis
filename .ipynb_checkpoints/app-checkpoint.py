import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Load dataset
file_path = "Cleaned_Carbon_Emissions.csv"
df = pd.read_csv(file_path)

# Initialize Dash app with external stylesheets
app = dash.Dash(__name__, external_stylesheets=[
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'
])

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Carbon Emissions Dashboard", className="text-center text-white mb-4 fw-bold"),
    ], className="bg-primary py-4 shadow-sm"),

    # Main content
    html.Div([
        # Debug info section to show available carbon types
        html.Div([
            html.H4("Available Carbon Types:", className="mb-2"),
            html.Div(id="available-carbon-types", className="mb-3 p-2 bg-light border rounded")
        ], className="mb-4 p-3 bg-white rounded shadow-sm"),

        # Stat Cards
        html.Div([
            html.Div([
                html.Div([
                    html.H3("Total Emissions", className="m-0 fs-5"),
                    html.P("XX Metric Tons", id="total-emissions", className="fs-4 fw-bold m-0"),
                ], className="card-body text-center")
            ], className="card p-3 shadow-sm", style={"background": "linear-gradient(135deg, #42b0ff, #4c8bf5)", "color": "white"}),

            html.Div([
                html.Div([
                    html.H3("Average Yearly", className="m-0 fs-5"),
                    html.P("XX Metric Tons", id="avg-emissions", className="fs-4 fw-bold m-0"),
                ], className="card-body text-center")
            ], className="card p-3 shadow-sm", style={"background": "linear-gradient(135deg, #42b0ff, #4c8bf5)", "color": "white"}),

            html.Div([
                html.Div([
                    html.H3("Year-over-Year", className="m-0 fs-5"),
                    html.P("XX%", id="yoy-change", className="fs-4 fw-bold m-0"),
                ], className="card-body text-center")
            ], className="card p-3 shadow-sm", style={"background": "linear-gradient(135deg, #42b0ff, #4c8bf5)", "color": "white"}),
        ], className="d-flex justify-content-around mb-4 gap-4"),

        # Filters
        html.Div([
            html.Div([
                html.Label("Select State:", className="fw-bold mb-2"),
                dcc.Dropdown(
                    id='state-dropdown',
                    options=[{'label': state, 'value': state} for state in df['state'].unique()],
                    value=df['state'].unique()[0],
                    className='form-control'
                ),
            ], className="col-md-4"),

            html.Div([
                html.Label("Filter by Year:", className="fw-bold mb-2"),
                dcc.RangeSlider(
                    id='year-slider',
                    min=df['year'].min(),
                    max=df['year'].max(),
                    marks={str(year): str(year) for year in range(df['year'].min(), df['year'].max()+1, 5)},
                    value=[df['year'].min(), df['year'].max()],
                    className="mt-2"
                ),
            ], className="col-md-4"),

            html.Div([
                html.Label("Select Carbon Types:", className="fw-bold mb-2"),
                dcc.Checklist(
                    id='carbon-type-checklist',
                    options=[{'label': ct, 'value': ct} for ct in sorted(df['carbon_type'].unique())],
                    value=sorted(df['carbon_type'].unique()),  # All selected by default
                    inline=True,
                    className="mt-2"
                ),
            ], className="col-md-4"),
        ], className="row mb-4 p-3 bg-white rounded shadow-sm"),

        # All emissions trend chart
        html.Div([
            dcc.Graph(id='emission-trend', className='bg-white p-3 rounded shadow-sm'),
        ], className="mb-4"),

        # Graphs row 2
        html.Div([
            html.Div([
                dcc.Graph(id='sector-wise-emission', className='bg-white p-3 rounded shadow-sm'),
            ], className="col-md-6"),

            html.Div([
                dcc.Graph(id='carbon-type-pie', className='bg-white p-3 rounded shadow-sm'),
            ], className="col-md-6"),
        ], className="row mb-4"),

        # Graphs row 3
        html.Div([
            dcc.Graph(id='emissions-map', className='bg-white p-3 rounded shadow-sm'),
        ], className="mb-4"),

    ], className="container-fluid p-4 bg-light")
], style={"minHeight": "100vh"})

# Callbacks
@app.callback(
    [Output('emission-trend', 'figure'),
     Output('sector-wise-emission', 'figure'),
     Output('carbon-type-pie', 'figure'),
     Output('emissions-map', 'figure'),
     Output('total-emissions', 'children'),
     Output('avg-emissions', 'children'),
     Output('yoy-change', 'children'),
     Output('available-carbon-types', 'children')],
    [Input('state-dropdown', 'value'),
     Input('year-slider', 'value'),
     Input('carbon-type-checklist', 'value')]
)
def update_graphs(selected_state, selected_years, selected_carbon_types):
    # Filter data based on selections
    state_data = df[(df['state'] == selected_state) &
                    (df['year'] >= selected_years[0]) &
                    (df['year'] <= selected_years[1]) &
                    (df['carbon_type'].isin(selected_carbon_types))]

    # Debug info - show available carbon types in the filtered data
    carbon_types_in_data = sorted(state_data['carbon_type'].unique())
    carbon_types_text = "Found in data: " + ", ".join(carbon_types_in_data)

    if state_data.empty:
        # Return empty figures if no data
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="No Data Available",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        return empty_fig, empty_fig, empty_fig, empty_fig, "0 Metric Tons", "0 Metric Tons", "0%", carbon_types_text

    # 1. Enhanced Line Chart for Emission Trends with 3D styling
    yearly_data = state_data.groupby(['year', 'carbon_type'])['emission_(metric_tons)'].sum().reset_index()

    fig1 = px.line(
        yearly_data,
        x='year',
        y='emission_(metric_tons)',
        color='carbon_type',
        markers=True,
        title=f"<b>Emission Trends in {selected_state}</b>",
        color_discrete_sequence=px.colors.qualitative.Bold,
        line_shape="spline",  # Makes the lines curved for 3D effect
        hover_data={'emission_(metric_tons)': ':.2f'}
    )

    fig1.update_traces(
        line=dict(width=4),
        marker=dict(size=10, line=dict(width=2, color='white')),
        mode="lines+markers"
    )

    fig1.update_layout(
        height=500,
        legend_title="Carbon Type",
        hovermode="x unified",
        plot_bgcolor='rgba(240,240,240,0.8)',
        xaxis=dict(
            title="Year",
            gridcolor='white',
            gridwidth=2,
        ),
        yaxis=dict(
            title="Emissions (Metric Tons)",
            gridcolor='white',
            gridwidth=2,
        ),
        font=dict(size=14),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Add shadows for 3D effect
    for i, trace in enumerate(fig1.data):
        fig1.add_trace(
            go.Scatter(
                x=trace.x,
                y=[y*0.98 for y in trace.y],
                mode='lines',
                line=dict(width=8, color='rgba(0,0,0,0.1)'),
                showlegend=False,
                hoverinfo='skip'
            )
        )

    # 2. Enhanced Bar Chart for Sector-wise Emission
    sector_data = state_data.groupby(['sector', 'carbon_type'])['emission_(metric_tons)'].sum().reset_index()

    fig2 = px.bar(
        sector_data,
        x='sector',
        y='emission_(metric_tons)',
        color='carbon_type',
        title=f"<b>Sector-wise Emissions in {selected_state}</b>",
        color_discrete_sequence=px.colors.qualitative.Vivid,
        barmode='group',
        text_auto='.2s'
    )

    fig2.update_traces(
        marker_line_width=1.5,
        marker_line_color='white',
        opacity=0.9,
        textposition='outside'
    )

    fig2.update_layout(
        height=500,
        legend_title="Carbon Type",
        plot_bgcolor='rgba(240,240,240,0.8)',
        xaxis_title="Sector",
        yaxis_title="Emissions (Metric Tons)",
        font=dict(size=14),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # 3. Enhanced Pie Chart with 3D effect for Carbon Type Distribution
    carbon_type_data = state_data.groupby('carbon_type')['emission_(metric_tons)'].sum().reset_index()

    fig3 = go.Figure()

    fig3.add_trace(go.Pie(
        labels=carbon_type_data['carbon_type'],
        values=carbon_type_data['emission_(metric_tons)'],
        textinfo='label+percent',
        textposition='inside',
        textfont=dict(size=14, color='white'),
        marker=dict(
            colors=px.colors.qualitative.Vivid[:len(carbon_type_data)],
            line=dict(color='white', width=2)
        ),
        hoverinfo='label+value+percent',
        hole=0.4,  # Creates a donut chart for 3D effect
        pull=[0.05 if ct == 'CH4' else 0.02 for ct in carbon_type_data['carbon_type']]  # Pull CH4 out more
    ))

    fig3.update_layout(
        title=dict(
            text=f"<b>Carbon Type Distribution in {selected_state}</b>",
            font=dict(size=18)
        ),
        height=500,
        annotations=[
            dict(
                text='Carbon<br>Types',
                x=0.5, y=0.5,
                font_size=16,
                showarrow=False
            )
        ]
    )

    # 4. 3D-style heatmap for emissions over time and carbon type
    # Create a pivot table for the heatmap
    years = sorted(state_data['year'].unique())
    carbon_types = sorted(state_data['carbon_type'].unique())

    emission_matrix = pd.pivot_table(
        state_data,
        values='emission_(metric_tons)',
        index='year',
        columns='carbon_type',
        aggfunc='sum',
        fill_value=0
    )

    fig4 = px.imshow(
        emission_matrix,
        labels=dict(x="Carbon Type", y="Year", color="Emissions (Metric Tons)"),
        x=emission_matrix.columns,
        y=emission_matrix.index,
        color_continuous_scale='Viridis',
        aspect="auto"
    )

    fig4.update_layout(
        title=f"<b>Emissions Heatmap for {selected_state}</b>",
        height=500,
        xaxis=dict(side="bottom"),
        coloraxis_colorbar=dict(
            title="Emissions<br>(Metric Tons)",
            thicknessmode="pixels", thickness=20,
            lenmode="pixels", len=300
        )
    )

    # Add contour lines for 3D effect
    fig4.add_trace(
        go.Contour(
            z=emission_matrix.values,
            x=emission_matrix.columns,
            y=emission_matrix.index,
            contours=dict(
                showlabels=True,
                labelfont=dict(size=12, color='white')
            ),
            line=dict(width=1, color='rgba(255,255,255,0.5)'),
            showscale=False
        )
    )

    # Calculate stats
    total_emissions = f"{state_data['emission_(metric_tons)'].sum():,.2f} Metric Tons"
    avg_emissions = f"{state_data['emission_(metric_tons)'].mean():,.2f} Metric Tons"

    # Calculate year-over-year change
    if len(years) > 1:
        yearly_totals = state_data.groupby('year')['emission_(metric_tons)'].sum().sort_index()
        if len(yearly_totals) >= 2:
            latest_year = yearly_totals.index[-1]
            previous_year = yearly_totals.index[-2]
            yoy_change = ((yearly_totals[latest_year] - yearly_totals[previous_year]) / yearly_totals[previous_year]) * 100
            yoy_text = f"{yoy_change:+.2f}%"
        else:
            yoy_text = "N/A"
    else:
        yoy_text = "N/A"

    return fig1, fig2, fig3, fig4, total_emissions, avg_emissions, yoy_text, carbon_types_text

# Run app
if __name__ == '__main__':
    app.run_server(debug=True)