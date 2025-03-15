# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

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

# Convert the Snowpark dataframe to a Pandas dataframe
pd_df = my_dataframe.to_pandas()

# Add a multiselect widget for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].unique(),
    max_selections=5
)

# Process the selected ingredients
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'].str.lower() == fruit_chosen.lower(), 'SEARCH_ON'].iloc[0]
        
        # Fetch and display nutrition information
        try:
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
            fruityvice_response.raise_for_status()
            st.subheader(f"{fruit_chosen} Nutrition Information")
            st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch nutrition information for {fruit_chosen}: {e}")

    # Construct the SQL statement
    my_insert_stmt = """
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES (:1, :2)
    """

    # Add a button to submit the order
    time_to_insert = st.button('Submit Order')

    # Execute the SQL statement
    if time_to_insert:
        session.sql(my_insert_stmt, (ingredients_string.strip(), name_on_order)).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
else:
    st.warning("Please select at least one ingredient!")
