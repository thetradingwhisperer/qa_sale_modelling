import streamlit as st  
import numpy as np  
import pandas as pd
import matplotlib.pyplot as plt
import joblib
from train import  *
import plotly.express as px



# Load the data
car_data = pd.read_csv('model/train_car_data.csv')
car_type = car_data['car type'].unique()
year = car_data['year'].unique()
gear_type= car_data['gear_type'].unique()
cynlinder = car_data['cynlinder'].unique()

#Title of the app
st.title('Car Price Predictor App')
st.subheader('Select parameters to predict the price of the car')
st.write('This app predicts the price of a car based on the following parameters:'
             '1. Car Type '
             '2. Mileage '
             '3. Gear Type '
             '4. Cynlinder '
             '5. Year')

# Create a side bar on streamlit
car_type = st.sidebar.selectbox('Car Type', car_type)
mileage = st.sidebar.slider('Mileage', 0, 250000, 10000)
gear_type = st.sidebar.selectbox('Gear Type', gear_type)
cynlinder = st.sidebar.selectbox('Cynlinder', cynlinder)
year = st.sidebar.slider('Year', 2000, 2020, 2022)


#import ml model
model = joblib.load('model/model.pkl')
input = pd.DataFrame(np.array([car_type, mileage, gear_type, year, cynlinder]).reshape(1, -1))
input.columns = ['car type', 'mileage', 'gear_type', 'year', 'cynlinder']

#Tell the user what he has selected
st.write('You have selected the following parameters:')
st.write(input)
prediction = round(model.predict(input)[0],2)
st.write("The predicted price in USD is: ", round(model.predict(input)[0],2))


st.write('---')
st.subheader('Explore the market data on your selected car type')


# Do some data visualization on the selected car type - use plotly
car_data_viz = car_data[car_data['car type'] == car_type]
car_data_viz['type'] = 'train'

# Add the new prediction to the data
new_pred = pd.DataFrame(np.array([car_type, prediction, mileage, gear_type, year, cynlinder]).reshape(1, -1))
new_pred['type'] = 'prediction'
new_pred.columns = ['car type', 'price', 'mileage', 'gear_type', 'year', 'cynlinder', 'type']
new_car_data_viz = pd.concat([car_data_viz, new_pred], axis=0)

fig1 = px.scatter(car_data_viz, x='mileage', y='price', 
                 color='year',
                 size='cynlinder',
                 hover_data=['year'])

fig2 = px.scatter(new_pred, x='mileage', y='price', size = [10])
fig2.update_traces(marker=dict(color='green', symbol='x'))
# Add the data from the second figure to the first one
for trace in fig2.data:
    fig1.add_trace(trace)

#Add dynamic title with plotly express
fig1.update_layout(title_text='Price vs Mileage for ' + car_type)

st.plotly_chart(fig1)

# Put some space between the content in the app



