# %% [markdown]
# ### Assignment #4: Basic UI
# 
# DS4003 | Spring 2024
# 
# Objective: Practice buidling basic UI components in Dash. 
# 
# Task: Build an app that contains the following components user the gapminder dataset: `gdp_pcap.csv`. [Info](https://www.gapminder.org/gdp-per-capita/)
# 
# UI Components:
# A dropdown menu that allows the user to select `country`
# -   The dropdown should allow the user to select multiple countries
# -   The options should populate from the dataset (not be hard-coded)
# A slider that allows the user to select `year`
# -   The slider should allow the user to select a range of years
# -   The range should be from the minimum year in the dataset to the maximum year in the dataset
# A graph that displays the `gdpPercap` for the selected countries over the selected years
# -   The graph should display the gdpPercap for each country as a line
# -   Each country should have a unique color
# -   Graph DOES NOT need to interact with dropdown or slider
# -   The graph should have a title and axis labels in reader friendly format  
# 
# Layout:  
# - Use a stylesheet
# - There should be a title at the top of the page
# - There should be a description of the data and app below the title (3-5 sentences)
# - The dropdown and slider should be side by side above the graph and take up the full width of the page
# - The graph should be below the dropdown and slider and take up the full width of the page
# 
# Submission: 
# - There should be only one app in your submitted work
# - Comment your code
# - Submit the html file of the notebook save as `DS4003_A4_LastName.html`
# 
# 
# **For help you may use the web resources and pandas documentation. No co-pilot or ChatGPT.**

# %%
# import dependencies

from dash import Dash, html, dcc, Input, Output, callback 
import pandas as pd
import plotly.express as px
import re

# %%
# read in dataframe, indexing by country

gdp = pd.read_csv('gdp_pcap.csv',index_col='country')

# %%
# import external stylesheets

stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# %%
# clean data

gdp_stack = gdp.stack().reset_index() # stacking to make the year a column, allowing easier subsetting
gdp_stack.rename({'level_1':'year',0:'gdp'},axis=1,inplace=True) # changing column names to easier understand in later code
gdp_stack['year'] = gdp_stack['year'].astype(int) # converting year from a string to an int for later boolean comparisons

gdp_stack['gdp'] = [re.sub(r'(\d)\.(\d)k',r'\1\2\\00',str(x)) for x in gdp_stack['gdp']] # Replace A.Bk with AB\00
gdp_stack['gdp'] = [re.sub(r'k',r'000',str(x)) for x in gdp_stack['gdp']] # Replace Ak with A000
gdp_stack['gdp'] = [re.sub(r'\\',r'',str(x)) for x in gdp_stack['gdp']] # Remove \ from strings
gdp_stack['gdp'] = gdp_stack['gdp'].astype(int) # Convert gdp to an integer

# %%
# initialize app
app = Dash(__name__,external_stylesheets=stylesheets)
server = app.server # Make app accessible as server for Render

# Get list of years as integers
years = list(gdp.columns)
years = [int(i) for i in years]


# Reset gdp index to pull country names from a column later
gdp.reset_index(inplace=True)

# define layout and elements
app.layout = html.Div([
    html.Div(children = [ # Creates the Title and Explanatory Paragraph
        html.H2('''Understanding Different Countries\' GDP per Capita over Time'''),
        html.H6('''This is an interactive graph designed to allow users to visualize GDP per capita trends in different countries. 
        The data comes from a dataframe that has collected each countries GDP per capita in from the years 1800-2100. 
        Users can select the countries they want to evaluate from the dropdown (by default, all countries are shown). 
        Additionally, users can select the timespan they want to view from the slider (by default, uses the full range).
        ''')
    ]),
    html.Div(children = [ # Contains the row with the dropdown and the slider
        html.Div(children = [
            dcc.Dropdown( # Create dropdown
                id = 'country_dropdown',
                options = gdp['country'].unique(), # Takes all countries in gdp['country'] that are unique as options
                multi=True, # Allows for multiple countries to be selected
                placeholder='Select Countries' # placeholder instructional text
                ),
            
        ], className='six columns'),
        html.Div(children = [
            dcc.RangeSlider( # Create RangeSlider
                min = min(years), # Takes minimum year (dynamic)
                max = max(years), # Takes maximum year (dynamic)
                step=1, # Allow users to select any whole number year
                value = [min(years),max(years)], # Default value to entire range
                marks={i: '{}'.format(i) for i in range(min(years),max(years)+50,50)}, # put marks every 50 years on the slider
                tooltip={ # Use tooltips to see selected years
                    "placement": "bottom",
                    "always_visible": True,
                },
                id = 'year_slider'
            )
        ], className='six columns'),
    ], className='row'),
    html.Div([ # Creates the graph
        dcc.Graph(
        id='gdp_Graph'
        )
    ])
])

@callback( # Callback that takes input from the dropdown and slider to output the graph
    Output('gdp_Graph', 'figure'),
    Input('country_dropdown', 'value'),
    Input('year_slider','value')
)
def update_figure(selected_countries,selected_years): # function to update the figure
    if not selected_countries: # Scenario where no countries are selected (breaks the isin if selected countries is []). Defaults to all countries
        ncfilter1 = gdp_stack['year'].le(selected_years[1]) # Only keep data from years less than or equal to the slider maximum
        ncfiltered_gdp = gdp_stack[ncfilter1]
        ncfilter2 = ncfiltered_gdp['year'].ge(selected_years[0]) # Only keep data from years greater than or equal to the slider minimum
        ncfiltered_gdp = ncfiltered_gdp[ncfilter2] 
        fig = px.line(ncfiltered_gdp, x='year', y='gdp',color='country', # Plot the figure using year, gdp, coloring by country
            title='Per Capita GDP of Selected Countries over Time',
            labels={'year':'Year','country':'Countries','gdp':'Per Capita GDP'}) # Change to best title and axis names

        return fig
    filter1 = gdp_stack['country'].isin(selected_countries) # Only keep data from selected countries
    filtered_gdp = gdp_stack[filter1]
    filter2 = filtered_gdp['year'].le(selected_years[1]) # Only keep data from years less than or equal to the slider maximum
    filtered_gdp = filtered_gdp[filter2]
    filter3 = filtered_gdp['year'].ge(selected_years[0]) # Only keep data from years greater than or equal to the slider minimum
    filtered_gdp = filtered_gdp[filter3]

    fig = px.line(filtered_gdp, x='year', y='gdp',color='country', # Plot the figure using year, gdp, coloring by country
        title='Per Capita GDP of Selected Countries over Time',
        labels={'year':'Year','country':'Countries','gdp':'Per Capita GDP'}) # Change to best title and axis names

    fig.update_layout(transition_duration = 500) # Set a brief transition duration for smoother use

    return fig

# %%
# run app
if __name__ == '__main__':
    app.run(debug=True, port=8049)


