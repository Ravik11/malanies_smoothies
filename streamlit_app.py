# Import python packages
import streamlit as st
import pandas as pd
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests


cnx=st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title(f"Customize Your Smoothie! :cup_with_straw:")
st.write(
  """
  Choose the fruits You want in your customize Smoothie!
  """
)

name_on_order = st.text_input("Name on Smoothie")
st.write("The Name on your smoothie :cup_with_straw: will be -", name_on_order)



my_dataframe = session.table("smoothies.public.FRUIT_OPTIONS").select(col('FRUIT_NAME'), col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

selected_ingredients = st.multiselect(
    "Choose Up To 5 Ingredients (you can choose more if needed):",
    my_dataframe,max_selections=5
)
st.success(f"You have selected: {selected_ingredients}")

if selected_ingredients:
    ingredients_string=''   
  
    for x in selected_ingredients:
        ingredients_string += x + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == x, 'SEARCH_ON'].iloc[0]
        #st.write('The search value for ', x,' is ', search_on, '.')

        st.subheader (x + 'Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)
        st.write (ingredients_string)  
        my_insert_stmt = """INSERT INTO smoothies.public.orders (ingredients, name_on_order) 
          VALUES ('""" + ingredients_string + """', '""" + name_on_order + """')"""
    
    
    time_to_order=st.button("Submit Order")
    if time_to_order:
        session.sql(my_insert_stmt).collect()
        
        st.success(f'Your Smoothie is ordered {name_on_order}!', icon="✅")


    
