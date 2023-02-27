# Description: This script downloads car data from QatarSale.com and saves it to gcp bigquery
import numpy as np
import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from lazypredict.Supervised import LazyRegressor
import joblib
import matplotlib.pyplot as plt

#load data from sqlite db
def load_data_from_db(db_name):
    """
    This function loads data from a sqlite db and returns a pandas dataframe.
    """
    # Connect to the database
    conn = sqlite3.connect(db_name)
    # Load the data into a dataframe
    df = pd.read_sql_query("SELECT * FROM car_sale", conn)
    # Close the connection
    conn.close()
    return df


#Some key parameters
num_features = ["cynlinder", "year","mileage"]
cat_features = ["gear_type", "car type"]
target = "price"

def preprocessor_pipeline(num_features, cat_features):
    """
    This function defines the pipeline.
    """

    # Create the pipeline
    num_transformer = make_pipeline(SimpleImputer(strategy="median"), StandardScaler())
    cat_transformer = make_pipeline(SimpleImputer(strategy="constant", fill_value="missing"), OrdinalEncoder())

    # create a ColumnTransformer object to preprocess the data
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_transformer, num_features),  # apply StandardScaler to numerical features
            ('cat', cat_transformer, cat_features)  # apply OneHotEncoder to categorical features
        ])
    
    return preprocessor
    
def train_model(df):
    """
    This function trains a model.
    """
    
    #clean the data
    df = df.dropna()
    df = df[df['cynlinder'] <12]
    # Filter when year is above 2000 and below 2022
    df = df[(df['year'] > 2000) & (df['year'] < 2022)]
    # Filter when mileage is above 0 and below 500000
    df = df[(df['mileage'] > 0) & (df['mileage'] < 500000)]
    # Filter when price is above 0 and below 1000000
    df = df[(df['price'] > 0) & (df['price'] < 1000000)]
    
    # Split the data into training and test sets
    drop_col = ["date", "price"]
    X = df.drop(drop_col, axis=1)
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    lazy = False
    if lazy:
        #Define the lazypredict model
        reg = LazyRegressor(verbose=0, ignore_warnings=True, custom_metric=None)
        models, predictions = reg.fit(X_train, X_test, y_train, y_test)
        print(models)

        return models, predictions
    
    else:
        # Define the model
        reg = RandomForestRegressor(n_estimators=100, random_state=42)

        # Create the pipeline
        pipeline = make_pipeline(preprocessor_pipeline(num_features, cat_features), 
                                reg)
        
        # Fit the pipeline to the training data
        pipeline.fit(X_train, y_train)

        # check prediction on x_train
        print("Training score: ", pipeline.score(X_train, y_train))

        #Save Figure of the predicted train data vs actual price
        fig = plt.scatter(pipeline.predict(X_train), y_train)
        plt.xlabel("Predicted Price")
        plt.ylabel("Actual Price")
        plt.title("Predicted vs Actual Price")
        plt.savefig("Predicted_vs_Actual_Price.png")

        #Save in a dataframe the predicted price vs actual price
        pd_df = pd.DataFrame([pipeline.predict(X_train), y_train])
        print(X_train)

        return pipeline

def main():
    """
    This function runs the main program.
    """
    # Load the data
    df = load_data_from_db('QatarCarSale.db')
    # Train the model
    pipeline = train_model(df)

    # Save the model
    joblib.dump(pipeline, 'model/model.pkl')



if __name__ == "__main__":
    main()

