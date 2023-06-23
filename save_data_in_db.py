# Description: This script downloads car data from QatarSale.com and saves it to gcp bigquery
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import re



def download_page_old():
    """
    This function downloads a web page and returns the response.
    """
    # Send a request to the website
    url_base = "https://qatarsale.com/en/products/cars_for_sale"
    url_list = [url_base + "?page=" + str(x) for x in range(1, 30)]

    car_sale_df = pd.DataFrame()

    for i in url_list:

        response = requests.get(i)
        # Send a request to the website
         # Check if the request was successful
        if response.status_code != 200:
            print("Failed to download page {}".format(i))
            return None

        # Parse the HTML response
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all the car listings on the page
        car_listings = soup.find_all("div", class_="product-list")

        # Iterate over each car listing
        titles = car_listings[0].find_all("a", class_="product-details")
        prices = car_listings[0].find_all("div", class_="product-price-info")
        parameters = car_listings[0].find_all("a", class_="product-definitions")

        titles_list = [titles[x] for x in range(0,len(titles),2)]

        data = []

        for title, price, parameter in zip(titles_list, prices, parameters):

            parameter_list = parameter.find_all("span", class_="def-value")

            # Print the title and price 
            data.append({"car type": title.text.strip(),
                        "price": price.text.strip().replace(' Q.R','').replace(',',''),
                        "mileage": parameter_list[0].text.strip().replace(' Km','').replace(',',''),
                        "gear_type": parameter_list[1].text.strip(),
                        "year": parameter_list[2].text.strip(),
                        "cynlinder": parameter_list[3].text.strip(),              
                        })

        page_df = pd.DataFrame(data)
        car_sale_df = pd.concat([car_sale_df, page_df])


    return car_sale_df

#New code to download data since old code is not working
def download_page():
    """
    This function downloads a web page and returns the response.
    """
    # Send a request to the website
    url_base = "https://qatarsale.com/en/products/cars_for_sale"
    url_list = [url_base + "?page=" + str(x) for x in range(1, 15)]

    car_sale_df = pd.DataFrame()
    
    for i in url_list:

        response = requests.get(i)
        # Send a request to the website
         # Check if the request was successful
        if response.status_code != 200:
            print("Failed to download page {}".format(i))
            return None

        # Parse the HTML response
        soup = BeautifulSoup(response.text, "html.parser")


        # Find all the car listings on the page
        soup = soup.find_all("div", class_="product-list")
        car_cards = soup[0].find_all('qs-product-card-v2')
        data = []
        for i, car_card in enumerate(car_cards):
            title_section = car_card.find('div', class_='title-section')
            car_name_parts = [tag.get_text(strip=True) for tag in title_section.find_all('p')]
            car_name = ' '.join(car_name_parts)

            car_price_tag = car_card.find('p', class_='p1')
            price = re.sub(r'[^\d.]', '', car_price_tag.get_text(strip=True))

            car_year_tag = car_card.find('span', class_='def-name', text='Year')
            year = car_year_tag.find_next('span', class_='def-value').get_text(strip=True)

            car_mileage_tag = car_card.find('span', class_='def-name', text='Mileage')
            mileage = car_mileage_tag.find_next('span', class_='def-value').get_text(strip=True)
            mileage = float(re.sub(r'[^\d.]', '', mileage))


            car_cylinder_tag = car_card.find('span', class_='def-name', text='Cylinder')
            cylinder = car_cylinder_tag.find_next('span', class_='def-value').get_text(strip=True)

            car_gear_type_tag = car_card.find('span', class_='def-name', text='Gear Type')
            gear_type = car_gear_type_tag.find_next('span', class_='def-value').get_text(strip=True)

            # Print the title and price 
            data.append({"car type": car_name,
                        "price": price,
                        "mileage": mileage,
                        "gear_type": gear_type,
                        "year": year,
                        "cynlinder": cylinder,              
                        })

            page_df = pd.DataFrame(data)
            car_sale_df = pd.concat([car_sale_df, page_df]).drop_duplicates()



    return car_sale_df


# function to remove non-numeric characters from a column in a dataframe
def remove_non_numeric(df, column):
    """
    This function removes non-numeric characters from a column in a dataframe.
    """
    df[column] = df[column].str.replace(r'\D+', '')
    return df

#function to add the current ingestion date to a dataframe
def add_date_to_df(df):
    """
    This function adds the current date to a dataframe.
    """
    df["date"] = pd.to_datetime('today').normalize()
    return df


"""
   Create a function that does the following:
   1. Create a database using sqlite if it doesn't exist
   2. Append the dataframe to the database
"""
def save_df_to_db(df, db_name):
    """
    This function saves a dataframe to a sqlite database.
    """
    # Create a database connection
    conn = sqlite3.connect(db_name)

    # Append the dataframe to the database
    df.to_sql("car_sale", conn, if_exists="append", index=False)

    # Close the database connection
    conn.close()




if __name__ == "__main__":
    # Download the page
    print("Downloading page from qatarsale.com")
    car_sale_df = download_page()
    print("Download completed")

    print("Cleaning the data")
    # Remove non-numeric characters from the price and mileage columns
    print(car_sale_df.head())
    for column in ["cynlinder", "year"]:
        car_sale_df = remove_non_numeric(car_sale_df, column)
    car_sale_df= car_sale_df[~(car_sale_df['year'] == 'Automatic')]
    car_sale_df= car_sale_df[~(car_sale_df['year'] == 'Manual')]

    # Convert the columns to the correct data types
    car_sale_df["car type"] = car_sale_df["car type"].astype('string')
    car_sale_df["price"] = car_sale_df["price"].astype(float)
    car_sale_df["mileage"] = car_sale_df["mileage"].astype(float)
    car_sale_df["gear_type"] = car_sale_df["gear_type"].astype('string')
    car_sale_df["year"] = car_sale_df["year"].astype(int)
    car_sale_df["cynlinder"] = car_sale_df["cynlinder"].astype(int)

    # Add the current date to the dataframe
    car_sale_df = add_date_to_df(car_sale_df)

    # Save the dataframe to a database
    save_df_to_db(car_sale_df, "QatarCarSale.db")


    



