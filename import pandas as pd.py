import pandas as pd
import streamlit as st

# Function to calculate BMR
def calculate_bmr(gender, age, weight, height):
    gender = gender.lower()
    if gender in ["male", "m"]:
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    elif gender in ["female", "f"]:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    else:
        raise ValueError("Invalid gender. Please enter 'male' or 'female'.")
    return bmr

# Function to calculate BMI
def calculate_bmi(weight, height):
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    return bmi

# Function to calculate percentage
def calculate_percentage(amount, daily_intake):
    return (amount / daily_intake) * 100

# Function to process the food content CSV
def process_food_file(file):
    try:
        # Read the CSV file
        food_data = pd.read_csv(file)

        # Clean numeric columns by removing non-numeric characters
        food_data["sodium"] = pd.to_numeric(food_data["sodium"].str.replace("[^0-9.]", "", regex=True), errors="coerce")
        food_data["calories"] = pd.to_numeric(food_data["calories"].str.replace("[^0-9.]", "", regex=True), errors="coerce")
        food_data["carbohydrates"] = pd.to_numeric(food_data["carbohydrates"].str.replace("[^0-9.]", "", regex=True), errors="coerce")
        food_data["fat"] = pd.to_numeric(food_data["fat"].str.replace("[^0-9.]", "", regex=True), errors="coerce")
        food_data["protein"] = pd.to_numeric(food_data["protein"].str.replace("[^0-9.]", "", regex=True), errors="coerce")

        return food_data
    except Exception as e:
        st.error(f"Error reading or cleaning the uploaded file: {e}")
        return None

# Streamlit App
def main():
    st.title("Daily Suggested Intake Calculator")

    # User inputs
    gender = st.text_input("Enter your gender (male/female):", value="male")
    age = st.number_input("Enter your age (in years):", min_value=1, value=25)
    weight = st.number_input("Enter your weight (in kg):", min_value=1.0, value=70.0)
    height = st.number_input("Enter your height (in cm):", min_value=1.0, value=170.0)
    uploaded_file = st.file_uploader("Upload Food Content CSV:", type=["csv"])

    if st.button("Calculate"):
        try:
            # Validate inputs
            if age <= 0:
                st.error("Age must be greater than 0.")
                return
            if weight <= 0:
                st.error("Weight must be greater than 0.")
                return
            if height <= 0:
                st.error("Height must be greater than 0.")
                return

            # Calculate BMR and BMI
            bmr = calculate_bmr(gender, age, weight, height)
            bmi = calculate_bmi(weight, height)

            # Suggested intakes
            sodium_intake = 1500 if 19 <= age <= 50 else 2300
            fat_intake = (0.30 * bmr) / 9
            protein_min = weight * 0.8
            protein_max = weight * 1.2
            carb_intake = (bmr - (fat_intake * 9) - (protein_min * 4)) / 4

            # Display results
            st.subheader("Your Results")
            st.write(f"**BMR (Calories):** {bmr:.2f}")
            st.write(f"**BMI:** {bmi:.2f}")
            st.write(f"**Sodium Intake (mg):** {sodium_intake}")
            st.write(f"**Fat Intake (g):** {fat_intake:.2f}")
            st.write(f"**Protein Intake (g):** {protein_min:.2f} - {protein_max:.2f}")
            st.write(f"**Carbohydrate Intake (g):** {carb_intake:.2f}")

            # Process the uploaded file
            if uploaded_file is not None:
                food_data = process_food_file(uploaded_file)

                if food_data is not None:
                    # Calculate total intake
                    total_sodium = food_data["sodium"].sum(skipna=True)
                    total_calories = food_data["calories"].sum(skipna=True)
                    total_carbohydrates = food_data["carbohydrates"].sum(skipna=True)
                    total_fat = food_data["fat"].sum(skipna=True)
                    total_protein = food_data["protein"].sum(skipna=True)

                    # Calculate percentages
                    percentages = {
                        "Sodium": calculate_percentage(total_sodium / 4, sodium_intake),
                        "Calories": calculate_percentage(total_calories / 4, bmr),
                        "Carbohydrates": calculate_percentage(total_carbohydrates / 4, carb_intake),
                        "Fat": calculate_percentage(total_fat / 4, fat_intake),
                        "Protein": calculate_percentage(total_protein / 4, protein_min),
                    }

                    # Display food percentages
                    st.subheader("Food Percentages")
                    for nutrient, percentage in percentages.items():
                        st.write(f"**{nutrient}:** {percentage:.2f}%")

                    # Display the processed food data
                    st.subheader("Processed Food Data")
                    st.dataframe(food_data)
                else:
                    st.error("Failed to process the uploaded file.")
            else:
                st.warning("Please upload a food content CSV file.")

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()