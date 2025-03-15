# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Get the name for the order
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Get the active Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()
# Query the fruit_options table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Add a multiselect widget for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe.select(col('FRUIT_NAME')).distinct().collect(),
    max_selections=5
)

# Process the selected ingredients
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen+'Nutrition Information')
        smoothie_froot_response = request.get("https://my.smoothiefroot/api/fruit/"+fruit_chosen)
        sd_df = st.dataframe(data = smoothiefroot_response.json(),use_container_width=True)
        # Fetch the SEARCH_ON value for the chosen fruit
        search_on_value = my_dataframe.filter(col('FRUIT_NAME') == fruit_chosen).select(col('SEARCH_ON')).collect()[0][0]
        
        # Fetch and display nutrition data for each chosen fruit
        st.subheader(f"{fruit_chosen} Nutrition Information")
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on_value}")
        if smoothiefroot_response.status_code == 200:
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.write(f"Could not fetch data for {fruit_chosen}.")

    # Construct the SQL statement
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """

    # Add a button to submit the order
    time_to_insert = st.button('Submit Order')

    # Execute the SQL statement
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
