import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.express as px
from plotly.colors import n_colors
from dash import Dash, html, dcc

# Load data
products_df = pd.read_csv('Products.csv')
sales_df = pd.read_csv('Sales.csv')

# Drop duplicates
products_df.drop_duplicates(inplace=True)
sales_df.drop_duplicates(inplace=True)

# Fix date parsing warning
sales_df['Date'] = pd.to_datetime(sales_df['Date'], format='%d/%m/%Y')
# Lollipop Chart
# Merge sales and product data to get the quantity sold per product
sales_products_df = pd.merge(sales_df, products_df, on='ProductId')

# Calculate the total quantity sold per product and get the top 5
top_selling_products = sales_products_df.groupby('ProductName')['Quantity'].sum().nlargest(5).reset_index()

# Create a horizontal lollipop chart for the top 5 selling products
top_selling_fig = go.Figure()

# Add dots for the top selling products
top_selling_fig.add_trace(go.Scatter(
    x=top_selling_products['Quantity'],
    y=top_selling_products['ProductName'],
    marker=dict(color='rgba(9, 9, 116, 1)', size=12),
    mode='markers',
    name='Sales number'
))

# Add lines for each product
for idx, row in top_selling_products.iterrows():
    top_selling_fig.add_trace(go.Scatter(
        x=[0, row['Quantity']],
        y=[row['ProductName'], row['ProductName']],
        mode='lines',
        line=dict(color='rgba(9, 9, 116, 1)', width=2),
        showlegend=False
    ))

# Update the layout for the top selling products figure
top_selling_fig.update_layout(
    plot_bgcolor='rgba(179,179,255,0.5)',  
    title='Top 5 Selling Products',
    xaxis_title='Quantity Sold',
    yaxis=dict(autorange="reversed"), 
    xaxis=dict(side='bottom'), 
    margin=dict(l=20, r=20, t=100, b=100),  
)
#Accompanying code for section 6
# Histogram
# Remove duplicates based on ProductId and create a copy to avoid SettingWithCopyWarning
unique_prices = sales_df.drop_duplicates(subset=['ProductId']).copy()

# Create a histogram
histogram_fig = go.Figure(data=[
    go.Histogram(
        x=unique_prices['UnitPrice'],
        xbins=dict(start=0, end=25, size=0.5),
        marker=dict(color='rgba(9, 9, 116, 1)'),
        hoverinfo='x+y',  #label text
        hovertemplate='Price: %{x}<br>Count: %{y}', 
    )
])

# Update layout for the histogram
histogram_fig.update_layout(
    plot_bgcolor='rgba(179,179,255,0.5)',
    title_text='Price Per Unit Distribution',
    xaxis_title='Price Range (USD)',
    yaxis_title='Count of Unique Prices per Unit',
    bargap=0.2
)

# Convert 'Date' to datetime in sales_df and extract the month name and number
sales_df['Date'] = pd.to_datetime(sales_df['Date'])
sales_df['Month'] = sales_df['Date'].dt.strftime('%B')
sales_df['MonthNum'] = sales_df['Date'].dt.month


# Calculate the monthly sales volume
sales_volume = sales_df.groupby(sales_df['Date'].dt.to_period('M'))['Quantity'].sum().reset_index()
sales_volume['Date'] = sales_volume['Date'].dt.to_timestamp()

# Calculate the monthly turnover
sales_df['Revenue'] = sales_df['UnitPrice'] * sales_df['Quantity']
turnover = sales_df.groupby(sales_df['Date'].dt.to_period('M')).agg({'Revenue': 'sum'}).reset_index()
turnover['Date'] = turnover['Date'].dt.to_timestamp()

# Calculate the monthly profit
merged_df = pd.merge(sales_df, products_df, on='ProductId', how='left')
merged_df['Profit'] = (merged_df['UnitPrice'] - merged_df['ProductCost']) * merged_df['Quantity']
profit_df = merged_df.groupby(merged_df['Date'].dt.to_period('M')).agg({'Profit': 'sum'}).reset_index()
profit_df['Date'] = profit_df['Date'].dt.to_timestamp()

# Create the figure with a secondary y-axis
sales_volume_fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add line for the sales volume (primary y-axis)
sales_volume_fig.add_trace(go.Scatter(
    x=sales_volume['Date'],
    y=sales_volume['Quantity'],
    mode='lines',
    name='Sales Volume',
    line=dict(color='black'),
), secondary_y=False)

# Add area for the turnover (secondary y-axis)
sales_volume_fig.add_trace(go.Scatter(
    x=turnover['Date'],
    y=turnover['Revenue'],
    fill='tozeroy',
    mode='none',
    name='Turnover',
    fillcolor='rgba(179,179,255,0.5)'
), secondary_y=True)




# Add line for the profit (secondary y-axis)
sales_volume_fig.add_trace(go.Scatter(
    x=profit_df['Date'],
    y=profit_df['Profit'],
    fill='tozeroy',
    mode='none',
    name='Profit',
    fillcolor='rgba(102, 102, 204, 0.5)'
), secondary_y=True)

sales_volume_fig.update_layout(
    title='Monthly Sales, Turnover, and Profit Trends',
    xaxis_title='Date',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(
        tickformat='%b %Y',  # Format the date as 'AbbreviatedMonth Year'
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(visible=True),
        type="date"
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
     )
)

# Set y-axes titles
sales_volume_fig.update_yaxes(title_text="Sales Number", secondary_y=False)
sales_volume_fig.update_yaxes(title_text="Turnover & Profit (USD)", secondary_y=True)
# Box plot
# Convert 'Date' in sales_df to datetime format and add a 'Month' column
sales_df['Date'] = pd.to_datetime(sales_df['Date'])
sales_df['Month'] = sales_df['Date'].dt.strftime('%B')

# Merge sales_df with products_df
merged_df = pd.merge(sales_df, products_df, on='ProductId', how='left')

# Calculate profit per sale
merged_df['Profit'] = (merged_df['UnitPrice'] - merged_df['ProductCost']) * merged_df['Quantity']

# Group by Supplier and ProductId, then sum the profits
productId_profit_per_supplier = merged_df.groupby(['Supplier', 'ProductId'])['Profit'].sum().reset_index()

# Calculate total profit per supplier
profit_per_supplier = productId_profit_per_supplier.groupby(['Supplier'])['Profit'].sum().reset_index()

# Sort suppliers by total profit
sorted_suppliers = profit_per_supplier.sort_values(by='Profit', ascending=False)['Supplier']

# Create a box plot with suppliers sorted by total profit
supplier_fig = px.box(productId_profit_per_supplier, y='Profit', x='Supplier', points=None,
                      category_orders={'Supplier': sorted_suppliers},  # Order suppliers by sum profit
                      color_discrete_sequence=['rgba(102, 102, 255, 0.5)'],  # Set colour as purple
                      title='Profit Distribution per Supplier (Sorted by Sum Profit)')

# Update the layout to set the plot's background color to transparent
supplier_fig.update_layout(
    plot_bgcolor='rgba(179,179,255,0.5)'
)
# Note: Different products have various product IDs from different suppliers. 
# Therefore, for supplier analysis, I use 'Group by ProductId' instead of 'Group by ProductName' to better understand each supplier's situation.

# Bubble chart 1
# Calculate profit for each sale
merged_df['Profit'] = (merged_df['UnitPrice'] - merged_df['ProductCost']) * merged_df['Quantity']
# Group by ProductId to aggregate total quantity and cumulative profit
product_Id_profit = merged_df.groupby(['ProductId','ProductName']).agg({'Quantity': 'sum', 'Profit': 'sum'}).reset_index()
product_profit = product_Id_profit.groupby(['ProductName']).agg({'Quantity': 'sum', 'Profit': 'sum'}).reset_index()
# Corrected section for creating the bubble chart
bubble_chart_fig = go.Figure(data=[
    go.Scatter(
        x=product_profit['Quantity'],
        y=product_profit['Profit'],
        text=product_profit['ProductName'],  
        mode='markers',
        marker=dict(
            size=abs(product_profit['Profit']) / product_profit['Profit'].abs().max() * 100,  # Use absolute value for size
            color=product_profit['Profit'],  # Colour can represent profit values
            showscale=True,
            sizemode='area'  #This ensures the size of the marker corresponds to area, not diameter
        )
    )
])

bubble_chart_fig.update_layout(
    plot_bgcolor='rgba(179,179,255,0.5)', 
    title_text='Product Profit and Quantity Sold(2017-2020)',
    xaxis_title='Total Quantity Sold',
    yaxis_title='Cumulative Profit Value',
)

# Note: Different products have various product IDs from different suppliers. 
# Therefore, Fro products analysis, I use 'Group by Productname' to better understand the situation of each product. 
# Bubble chart 2
#incorporate a slider to select a specific year to better compare with bubble chart 1.

from dash.dependencies import Input, Output
# Assuming sales_df is your sales data DataFrame and it has a 'Date' column
sales_df['Year'] = pd.to_datetime(sales_df['Date']).dt.year

# Merge and calculate profit as before
merged_df = pd.merge(sales_df, products_df, on='ProductId')
merged_df['Profit'] = (merged_df['UnitPrice'] - merged_df['ProductCost']) * merged_df['Quantity']

# Group by ProductId ProductName and Year
product_year_Id_profit = merged_df.groupby(['ProductId', 'ProductName', 'Year']).agg({'Quantity': 'sum', 'Profit': 'sum'}).reset_index()
product_year_profit = product_year_Id_profit.groupby(['ProductName','Year']).agg({'Quantity': 'sum', 'Profit': 'sum'}).reset_index()
# Create a function to generate the bubble chart for a given year
def create_bubble_chart(selected_year):
    filtered_data = product_year_profit[product_year_profit['Year'] == selected_year]
    fig = go.Figure(data=[
        go.Scatter(
            x=filtered_data['Quantity'],
            y=filtered_data['Profit'],
            text=filtered_data['ProductName'],
            mode='markers',
            marker=dict(
                size=abs(filtered_data['Profit']) / filtered_data['Profit'].abs().max() * 100,
                color=filtered_data['Profit'],
                showscale=True,
                sizemode='area'
            )
        )
    ])
    fig.update_layout(
        plot_bgcolor='rgba(179,179,255,0.5)',
        title_text=f'Product Profit and Quantity Sold in {selected_year}',
        xaxis_title='Quantity Sold',
        yaxis_title='Cumulative Profit Value',
    )
    return fig

# Initialize the Dash app
app = Dash(__name__)

# Define the app layout
app.layout = html.Div([
    html.H1("Walmart Sales Dashboard", style={'text-align': 'center'}),
    
    html.Div([
        dcc.Graph(figure=bubble_chart_fig)  # Bubble chart 1
    ], style={'width': '50%', 'display': 'inline-block'}),

    # Bubble chart 2 and slider
        html.Div([
            dcc.Graph(id='bubble-chart', figure=create_bubble_chart(product_year_profit['Year'].min())),
            
            # Year Slider under the right plot
            dcc.Slider(
                id='year-slider',
                min=product_year_profit['Year'].min(),
                max=product_year_profit['Year'].max(),
                value=product_year_profit['Year'].min(),
                marks={str(year): str(year) for year in product_year_profit['Year'].unique()},
                step=None
            )
        ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
    
# Lollipop Chart
    html.Div([
        dcc.Graph(figure=top_selling_fig)  # Top 5 Selling Products plot
    ], style={'width': '50%', 'display': 'inline-block'}),
# line-area chart
    html.Div([
        dcc.Graph(figure=sales_volume_fig)  # Combined Sales Volume and Turnover plot
    ], style={'width': '50%', 'display': 'inline-block'}),
# Violin Plot
    html.Div([
        dcc.Graph(figure=supplier_fig)  # Suppliers analysis
    ], style={'width': '50%', 'display': 'inline-block'}),
# Histogram
        html.Div([
        dcc.Graph(figure=histogram_fig)  # Distrebution of product price range
    ], style={'width': '50%', 'display': 'inline-block'}),
])
# Add slider for bubble chart 2
# Callback to update bubble chart 2 based on slider value
@app.callback(
    Output('bubble-chart', 'figure'),
    [Input('year-slider', 'value')]
)
def update_chart(selected_year):
    return create_bubble_chart(selected_year)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)

# I added a slider in bubble_chart 2 to select each year, which can be used to compare the each year and total data over four years.
# I added a slider in line and area chart to select specific period.




