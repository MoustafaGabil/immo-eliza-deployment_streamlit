import streamlit as st
from predict import get_prediction

# ------------------------------------ Streamlit App ------------------------------------
# App title and description

st.markdown(
    """
    <div style="text-align: center;">
        <h1>🏡 Property Price Predictor Over Belgium</h1>
        <img src="https://images.emojiterra.com/google/noto-emoji/unicode-16.0/color/1024px/1f1e7-1f1ea.png" width="100">
    </div>
    """,
    unsafe_allow_html=True
)

st.write(
    "This API predicts the price of properties (houses or apartments) based on various features "
    "Provide the necessary inputs below to get an estimate in parallel with the expected range."
)
st.markdown("""
### Usage Instructions:
- To get an accurate prediction, make sure to enter the correct location (locality) and zip code.
- Input all relevant property details and submit to receive an estimated price.
""")


# User inputs
locality_options = [
    'Aalst', 'Antwerp', 'Arlon', 'Ath',
    'Bastogne', 'Brugge', 'Brussels',
    'Charleroi', 'Dendermonde', 'Diksmuide',
    'Dinant', 'Eeklo', 'Gent',
    'Halle-vilvoorde', 'Hasselt', 'Huy',
    'Ieper', 'Kortrijk', 'Leuven',
    'Liège', 'Maaseik', 'Marche-en-Famenne',
    'Mechelen', 'Mons', 'Mouscron',
    'Namur', 'Neufchâteau', 'Nivelles',
    'Oostend', 'Oudenaarde', 'Philippeville',
    'Roeselare', 'Sint-Niklaas', 'Soignies',
    'Thuin', 'Tielt', 'Tongeren',
    'Tournai', 'Turnhout', 'Verviers',
    'Veurne', 'Virton', 'Waremme'
]
property_type = st.selectbox("Property Type", ["House", "Apartment"])
locality = st.selectbox("Locality", locality_options, index=12)
zip_code = st.number_input("Zip Code", value=9000, step=1)
construction_year = st.number_input("Construction Year", min_value=1800, max_value=2024, value=2020)
total_area_sqm = st.number_input("Total Area (sqm)", value=100.0, step=1.0)
surface_land_sqm = st.number_input("Land Surface (sqm)", value=120.0, step=1.0)
garden_sqm = st.number_input("Garden Size (sqm)", value=15.0, step=1.0)
nbr_frontages = st.number_input("Number of Frontages", value=2, step=1)
nbr_bedrooms = st.number_input("Number of Bedrooms", value=1, step=1)
kitchen_type = st.selectbox("Kitchen Type",["NOT_INSTALLED", "SEMI_EQUIPPED", "USA_SEMI_EQUIPPED", "INSTALLED", "USA_HYPER_EQUIPPED"])
building_state = st.selectbox("Building State",["TO_RESTORE", "TO_RENOVATE", "TO_BE_DONE_UP", "GOOD", "JUST_RENOVATED", "AS_NEW"])
epc = st.selectbox("Energy Class (EPC)", ["G", "F", "E", "D", "C", "B", "A", "A+", "A++"])
fl_double_glazing = st.radio("Double Glazing", [1, 0], format_func=lambda x: "Yes" if x == 1 else "No")
fl_terrace = st.radio("Terrace", [1, 0], format_func=lambda x: "Yes" if x == 1 else "No")
fl_swimming_pool = st.radio("Swimming Pool", [1, 0], format_func=lambda x: "Yes" if x == 1 else "No")
fl_floodzone = st.radio("Flood Zone", [1, 0], format_func=lambda x: "Yes" if x == 1 else "No")

# Creating a submit button
submit_button = st.button("Predict Price")

if submit_button:
    try:
        
        # Construct the payload
        property_details = {
            "property_type": property_type,
            "locality": locality,
            "zip_code": zip_code,
            "construction_year": construction_year,
            "total_area_sqm": total_area_sqm,
            "surface_land_sqm": surface_land_sqm,
            "garden_sqm": garden_sqm,
            "nbr_frontages": nbr_frontages,  # Hardcoded for now, adjust as needed
            "nbr_bedrooms": nbr_bedrooms,
            "kitchen_type": kitchen_type,
            "building_state": building_state,
            "epc": epc,
            "fl_double_glazing": fl_double_glazing,
            "fl_terrace": fl_terrace,
            "fl_swimming_pool": fl_swimming_pool,
            "fl_floodzone": fl_floodzone
        }

        # Calling prediction function 
        prediction = get_prediction(property_details)
        st.success(f"Predicted Price: €{prediction['predicted_price']}")
        st.write(f"Price Range: €{prediction['predicted_price_range']['min']} - €{prediction['predicted_price_range']['max']}")

    except ValueError as e:
        st.error(str(e))  # Display validation error message
