import joblib
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
from fastapi import HTTPException


# Initialize geolocator
geolocator = Nominatim(user_agent="property_price_predictor")

# Load models and encoders
house_model = joblib.load(r"models and encoders/XGB_Regression_HOUSE_without_outliers.pkl")
apartment_model = joblib.load(r"models and encoders/XGB_Regression_APARTMENT_without_outliers.pkl")
locality_encoder = joblib.load(r"models and encoders/locality_encoder.joblib")
kitchen_encoder = joblib.load(r"models and encoders/encoder_kitchen_type.joblib")
building_state_encoder = joblib.load(r"models and encoders/encoder_building_state.joblib")
epc_encoder = joblib.load(r"models and encoders/encoder_epc.joblib")

# MSE values for house and apartment
MSE_VALUES = {
    "house": 50102,
    "apartment": 31681,
}

def get_lat_lon(zip_code: int, locality: str):
    try:
        location = geolocator.geocode(f"{locality}, {zip_code}")
        if location:
            return location.latitude, location.longitude
        else:
            raise HTTPException(status_code=404, detail="Location not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching location details.")


# Function to validate integer inputs
def validate_int(value, field_name):
    if not isinstance(value, int):
        raise ValueError("Invalid input, Please enter an integer values for Bedrooms and Frontages.",)
    if value <= 0:
        raise ValueError("Invalid input, Please enter an integer values for Bedrooms and Frontages.",)
    
# Function to validate logical relationships between areas
def validate_area_relationships(surface_land_sqm, total_area_sqm, garden_sqm):
    if garden_sqm > surface_land_sqm or garden_sqm > total_area_sqm:
        raise ValueError("Garden size cannot be larger than the surface land area or total area.")
    if total_area_sqm > surface_land_sqm:
        raise ValueError("Invalid input: Total area cannot be larger than the surface land.",) 
################################################ which way should we write the error? #####################################


# # Prediction function
def get_prediction(property_details) -> dict:

    validate_int(property_details["nbr_bedrooms"], "Number of Bedrooms")
    validate_int(property_details["nbr_frontages"], "Number of Frontages")



    # # Validate area relationships
    validate_area_relationships(
        property_details["surface_land_sqm"],
        property_details["total_area_sqm"],
        property_details["garden_sqm"],
    )


    # # Fetch latitude and longitude
    latitude, longitude = get_lat_lon(property_details["zip_code"], property_details["locality"])

    # # Encode categorical values
    # try:
    locality_encoded = locality_encoder.transform([[property_details["locality"]]])
    kitchen_encoded = kitchen_encoder.transform([[property_details["kitchen_type"]]])[0][0]
    building_encoded = building_state_encoder.transform([[property_details["building_state"]]])[0][0]
    epc_encoded = epc_encoder.transform([[property_details["epc"]]])[0][0]

    # Prepare features for prediction
    features = {
        "construction_year": property_details["construction_year"],
        "total_area_sqm": property_details["total_area_sqm"],
        "nbr_frontages": property_details["nbr_frontages"],
        "nbr_bedrooms": property_details["nbr_bedrooms"],
        "kitchen_type_encoded":kitchen_encoded ,
        "building_state_encoded": building_encoded,
        "epc_encoded": epc_encoded,
        "garden_sqm": property_details["garden_sqm"],
        "surface_land_sqm": property_details["surface_land_sqm"],
        "fl_double_glazing": property_details["fl_double_glazing"],
        "fl_terrace": property_details["fl_terrace"],
        "fl_swimming_pool": property_details["fl_swimming_pool"],
        "fl_floodzone": property_details['fl_floodzone'],
        "latitude": latitude,
        "longitude": longitude,
        "zip_code": property_details["zip_code"],
    }

    # Convert to DataFrame and concatenate locality encoding
    
    features_df = pd.DataFrame([features])
    input_data = np.concatenate([features_df.values, locality_encoded], axis=1)

    # Select model based on property type
    model = house_model if property_details["property_type"].lower() == "house" else apartment_model

    # Make the prediction
    prediction = model.predict(input_data)[0]
    prediction = int(prediction)

    # Calculate the price range
    mse = MSE_VALUES[property_details["property_type"].lower()]
    price_range = {"min": prediction - mse, "max": prediction + mse}

    # Return the prediction in the expected format
    return {
        "property_type": property_details["property_type"],
        "predicted_price": prediction,
        "predicted_price_range": price_range
    }
