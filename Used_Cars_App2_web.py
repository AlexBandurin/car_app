import pandas as pd
import numpy as np
import dash
from dash import ctx
from dash import html
#import dash_html_components as html
from dash import dcc
#import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
#import xgboost as xgb
import pickle


#import copy

# Read the airline data into pandas dataframe
df = pd.read_csv('car_data_sorted_Full.csv')
df_info = pd.read_csv('df_info.csv')
clicks = 0
price_old = 0
Flag = False

#bst = xgb.Booster()
#bst.load_model("xgb_model.txt")
bst = pickle.load(open('xgb_model.pkl', "rb"))

#condition_vals = {'New': 5, 'Like New': 4, 'Excellent': 3, 'Good': 2, 'Fair': 1, 'Salvage': 0}
transmission_vals = {'Automatic': 1, 'Manual': 0}
frame = pd.DataFrame(np.zeros([1,df_info.shape[1]]), columns = df_info.columns)

year_vals = sorted(df.Year.value_counts().index, reverse = True)
dropdown_year = []
for year in year_vals:
    dropdown_year.append({'label': year, 'value': int(year)})
make_vals = df.Make.value_counts().index
dropdown_make = []
for make in make_vals:
    dropdown_make.append({'label': make, 'value': make})
model_vals = df.Model.value_counts().index
#model_vals = df[df.Make == selected_make].Model.value_counts().index
dropdown_model = []
for model in model_vals:
    dropdown_model.append({'label': model, 'value': model})
condition_vals = ['New','Like New','Excellent', 'Good', 'Fair', 'Salvage']
dropdown_condition = []
for condition in condition_vals:
    dropdown_condition.append({'label': condition, 'value': condition})
color_vals = df.Color.value_counts().index
dropdown_color = []
for color in color_vals:
    dropdown_color.append({'label': color, 'value': color})
title_vals = df.Title.value_counts().index
dropdown_title = []
for title in title_vals:
    dropdown_title.append({'label': title, 'value': title})
fuel_vals = df.Fuel.unique()
#fuel_vals = df[df.Make == selected_make].Fuel.value_counts().index
dropdown_fuel = []
for fuel in fuel_vals:
    dropdown_fuel.append({'label': fuel, 'value': fuel})

cylinder_index = sorted(df.Cylinders.value_counts().index.tolist())
cylinders_vals = [str(i) for i in cylinder_index]
dropdown_cylinders = []
for cylinders in cylinders_vals:
    if cylinders == '0':
        dropdown_cylinders.append({'label': 'N/A', 'value': 'N/A'})
    else:
        dropdown_cylinders.append({'label': cylinders, 'value': cylinders})

drive_vals = df.Drive.value_counts().index
#drive_vals = df[df.Make == selected_make].Drive.value_counts().index
dropdown_drive = []
for drive in drive_vals:
    dropdown_drive.append({'label': drive, 'value': drive})
dropdown_transmission = []
for transmission in transmission_vals:
    dropdown_transmission.append({'label': transmission, 'value': transmission_vals.get(transmission)})

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(children=[html.H1('Used Car Price Prediction',
                                        style={'textAlign': 'center', 'color': '#503D36','font-size': 50}), 
                                    html.H1('Please fill all fields before calculating, starting with "Vehicle Type"',
                                        style={'textAlign': 'left','font-size': 23}), 
                                    html.H1('Note: Refresh page after each calculation for best results',
                                        style={'textAlign': 'left','font-size': 23}),     
                                html.Br(),
                                html.H1('Vehicle Type',
                                        style={'textAlign': 'left','font-size': 25}), 
                                html.Div([
                                    html.Div([
                                        html.P('Please Select Vehicle Year')
                                        ], style={'display':'inline-block', 'margin-right': '150px'}),  
                                    html.Div([
                                        html.P('Please Select Vehicle Make')
                                        ], style={'display':'inline-block', 'margin-right': '145px'}),
                                    html.Div([
                                        html.P('Please Select Vehicle Model')
                                        ], style={'display':'inline-block'})  
                                        ]),
                                html.Div([
                                    html.Div([
                                        dcc.Dropdown(
                                            id = 'dropdown_year',
                                            options=dropdown_year,
                                            placeholder= 'Select Year')
                                        ], style={'width': '150px','display': 'inline-block', 'margin-right': '170px'}),
                                    html.Div([                             
                                        dcc.Dropdown(
                                            id = 'dropdown_make',
                                            options=dropdown_make,
                                            placeholder='Select Make')
                                        ], style={'width': '150px','display': 'inline-block', 'margin-right': '170px'}),
                                    html.Div([       
                                            dcc.Dropdown(
                                            id = 'dropdown_model',
                                            options=dropdown_model,
                                            placeholder='Select Model')
                                        ], style={'width': '150px','display': 'inline-block',})
                                        ]),    
                                html.Br(), 
                                html.H1('Vehicle Condition',
                                        style={'textAlign': 'left','font-size': 25}), 
                                html.P('Please Input Vehicle Mileage'),
                                html.Br(), 
                                dcc.Input(
                                    id='input_odometer',
                                    type='number',
                                    placeholder = 'Enter Mileage',
                                    style={'width': 142, 'height': 32, 'font-size': '15px'}),     
                                html.Br(),     
                                html.Br(), 
                                html.P('Please Select Vehicle Condition'),
                                dcc.Dropdown(
                                    id = 'dropdown_condition',
                                    options=dropdown_condition,
                                    value= 'Excellent', 
                                    style={'width': '150px'}),                 
                                html.Br(),
                                html.H1('Vehicle Specs',
                                        style={'textAlign': 'left','font-size': 25}), 
                                html.Div([
                                    html.Div([
                                        html.P('Please Select Vehicle Color')
                                        ], style={'display':'inline-block', 'margin-right': '145px'}),  
                                    html.Div([
                                        html.P('Please Select Cylinder Count')
                                        ], style={'display':'inline-block', 'margin-right': '135px'}), 
                                    html.Div([
                                        html.P('Please Select Vehicle Drivetrain')
                                        ], style={'display':'inline-block'})
                                        ]),
                                html.Div([     
                                    html.Div([                          
                                        dcc.Dropdown(
                                            id = 'dropdown_color',
                                            options=dropdown_color,
                                            placeholder= 'Select Color')
                                        ], style={'width': '150px','display': 'inline-block', 'margin-right': '170px'}),
                                    html.Div([       
                                        dcc.Dropdown(
                                            id = 'dropdown_cylinders',
                                            options=dropdown_cylinders,
                                            placeholder= 'Select Cylinders')
                                        ], style={'width': '150px','display': 'inline-block','margin-right': '170px'}), 
                                    html.Div([       
                                        dcc.Dropdown(
                                            id = 'dropdown_drive',
                                            options=dropdown_drive,
                                            placeholder= 'Select Drivetrain')
                                        ], style={'width': '150px','display': 'inline-block'})
                                        ]),    
                                html.Br(),
                                html.Div([  
                                    html.Div([
                                        html.P('Please Select Vehicle Transmission')
                                        ], style={'display':'inline-block', 'margin-right': '95px'}),
                                    html.Div([
                                        html.P('Please Select Vehicle Fuel Type')
                                        ], style={'display':'inline-block'})  
                                        ]),              
                                html.Div([     
                                    html.Div([       
                                        dcc.Dropdown(
                                            id = 'dropdown_transmission',
                                            options=dropdown_transmission,
                                            placeholder= 'Select Transmission')
                                        ], style={'width': '150px','display': 'inline-block','margin-right': '170px'}),     
                                    html.Div([       
                                        dcc.Dropdown(
                                            id = 'dropdown_fuel',
                                            options=dropdown_fuel,
                                            placeholder= 'Select Fuel Type')
                                        ], style={'width': '150px','display': 'inline-block'})
                                        ]),    
                                html.Br(),
                                html.H1('Title Status',
                                        style={'textAlign': 'left','font-size': 25}), 
                                html.P('Please Select Vehicle Title Status'),                               
                                dcc.Dropdown(
                                    id = 'dropdown_title',
                                    options=dropdown_title,
                                    value= 'Clean',
                                    style={'width': '150px'}),
                                html.Br(),
                                html.Br(),
                                html.Button('Calculate', id='button', n_clicks=0, 
                                            style={'marginLeft': '45%','textAlign': 'center','width': '150px','height': '76px','font-size': '25px',\
                                                    'backgroundColor': '#40a9de',"color": "black"}),
                                html.Br(),
                                html.Br(),
                                html.Br(),
                                html.H1(id='result',
                                        style={'textAlign': 'center', 'color': '#18c429',
                                               'font-size': 44}), 
                                html.Br(),
                                html.Br(),
                                html.Br(),
                                html.Br(),
                                html.Br()
                                ])
@app.callback(
            [Output(component_id='dropdown_model', component_property='options'),
            Output(component_id='dropdown_condition', component_property='options'),
            Output(component_id='dropdown_condition', component_property='value'),
            Output(component_id='dropdown_color', component_property='options'),
            Output(component_id='dropdown_color', component_property='value'),
            Output(component_id='dropdown_drive', component_property='options'),
            Output(component_id='dropdown_drive', component_property='value'),
            Output(component_id='dropdown_fuel', component_property='options'),
            Output(component_id='dropdown_fuel', component_property='value'),
            Output(component_id='dropdown_title', component_property='options'),
            Output(component_id='dropdown_title', component_property='value'),           
            Output(component_id='dropdown_cylinders', component_property='options'),
            Output(component_id='dropdown_cylinders', component_property='value'),
            Output(component_id='dropdown_transmission', component_property='options'),
            Output(component_id='dropdown_transmission', component_property='value')],
            [Input(component_id='dropdown_make', component_property='value'),
            Input(component_id='dropdown_model', component_property='value')])

def get_price(make, model):
        filtered_df = df[(df.Make == make) & (df.Model == model)] 
        model_vals = df[df.Make == make].Model.value_counts().index
        dropdown_model = []
        for model_ in model_vals:
            dropdown_model.append({'label': model_, 'value': model_})
        condition_vals = filtered_df.Condition.value_counts().index
        dropdown_condition = []
        for condition_ in condition_vals:
            dropdown_condition.append({'label': condition_, 'value': condition_})

        color_vals = filtered_df.Color.value_counts().index
        dropdown_color = []
        for color_ in color_vals:
            dropdown_color.append({'label': color_, 'value': color_})

        drive_vals = filtered_df.Drive.value_counts().index
        dropdown_drive = []
        for drive_ in drive_vals:
            dropdown_drive.append({'label': drive_, 'value': drive_})

        fuel_vals = filtered_df.Fuel.value_counts().index
        dropdown_fuel = []
        for fuel_ in fuel_vals:
            dropdown_fuel.append({'label': fuel_, 'value': fuel_})
        
        title_vals = filtered_df.Title.value_counts().index
        dropdown_title = []
        for title_ in title_vals:
            dropdown_title.append({'label': title_, 'value': title_})
        
        cylinder_vals = sorted(filtered_df.Cylinders.unique().tolist())
        cylinder_vals = [str(i) for i in cylinder_vals]
        dropdown_cylinders = []
        for cylinders in cylinders_vals:
            if cylinders == '0':
                dropdown_cylinders.append({'label': 'N/A', 'value': 'N/A'})
            else:
                dropdown_cylinders.append({'label': cylinders, 'value': cylinders})

        transmission_vals = sorted(filtered_df.Transmission_Automatic.unique().tolist())
        transmission_decode = {1:'Automatic', 0: 'Manual'}
        dropdown_transmission = []
        for transmission_ in transmission_vals:
            dropdown_transmission.append({'label': transmission_decode.get(transmission_), 'value': transmission_})

        return dropdown_model, dropdown_condition, '',  dropdown_color, '', dropdown_drive, '', dropdown_fuel, '',dropdown_title, '', dropdown_cylinders, '', dropdown_transmission, ''

@app.callback(
            Output(component_id='result', component_property='children'),
            [Input(component_id = 'button',component_property = 'n_clicks'),
            Input(component_id='dropdown_year', component_property='value'),
            Input(component_id='dropdown_make', component_property='value'),
            Input(component_id='dropdown_model', component_property='value'),
            Input(component_id='input_odometer', component_property='value'),
            Input(component_id='dropdown_cylinders', component_property='value'),
            Input(component_id='dropdown_condition', component_property='value'),
            Input(component_id='dropdown_color', component_property='value'),
            Input(component_id='dropdown_title', component_property='value'),
            Input(component_id='dropdown_fuel', component_property='value'),
            Input(component_id='dropdown_transmission', component_property='value'),
            Input(component_id='dropdown_drive', component_property='value')]
            )  

def get_price(clicks, year, make, model, odometer, cylinders, condition, color, title, fuel, transmission, drive):
        global frame
        global price_old
        global Flag
        global bst
        if 'button' == ctx.triggered_id:
            if (isinstance(make,str) and isinstance(model,str) and isinstance(cylinders,str) 
            and isinstance(color,str) > 0 and isinstance(title,str) > 0 and isinstance(fuel,str) and isinstance(drive,str) > 0 
            and isinstance(odometer,int) and isinstance(year,int) and isinstance(condition,str) and isinstance(transmission, int)
            and len(make) > 0 and len(model) > 0 and len(cylinders) > 0 and len(color) > 0 and len(title) > 0 and len(fuel) > 0 
            and len(drive) > 0 and len(condition) > 0):
                    Flag = True
                    #frame = pd.DataFrame(np.zeros([1,df_info.shape[1]]), columns = df_info.columns)
                    frame['Make_'+ make] = 1 
                    frame['Model_'+ model] = 1 
                    frame['Drive_'+ drive] = 1 
                    frame['Fuel_'+ fuel] = 1 
                    frame['Title_'+ title] = 1
                    frame['Color_'+ color] = 1 
                    frame['Cylinders_'+ cylinders] = 1 
                    frame['Condition_' + condition] = 1
                    frame['Year'] = year 
                    frame['Odometer'] = odometer 
                    frame['Transmission_Automatic'] = transmission
                    #len(odometer) > 0 and 
                    #len(transmission) > 0 and 
                    #len(condition) > 0 and 
                    price = int(bst.predict(frame.values)[0])
                    price_old = price
                    #return str(type(fuel))
                    return "Your Vehicle Price is:    $" + str('{:,}'.format(price))
            else: 
                Flag = False
                return 'Please Fill All Fields'
        else:
            if (Flag == True) and (clicks > 0):
                return "Your Vehicle Price is:    $" + str('{:,}'.format(price_old))
            else:
                return ' '
if __name__ == '__main__':
    app.run_server(debug=False)