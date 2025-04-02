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

# Function to suggest daily sugar intake
def suggest_daily_sugar():
    return 25

# Function to calculate BMI
def calculate_bmi(weight, height):
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    return bmi

# Function to process user data from a CSV file
def process_user_data_file(uploaded_user_file):
    try:
        user_data = pd.read_csv(uploaded_user_file)
        required_columns = ["name", "gender", "age", "weight", "height"]
        for column in required_columns:
            if column not in user_data.columns:
                raise ValueError(f"Missing required column: {column}")
        user_data.columns = user_data.columns.str.strip().str.lower()
        user_data["name"] = user_data["name"].str.strip()
        user_data["gender"] = user_data["gender"].str.lower().str.strip()
        user_data["age"] = pd.to_numeric(user_data["age"], errors="coerce")
        user_data["weight"] = pd.to_numeric(user_data["weight"], errors="coerce")
        user_data["height"] = pd.to_numeric(user_data["height"], errors="coerce")
        user_data.dropna(subset=["name", "gender", "age", "weight", "height"], inplace=True)
        return user_data
    except Exception as e:
        st.error(f"Error processing user data file: {e}")
        return None

# Function to calculate percentage
def calculate_percentage(amount, daily_intake):
    if daily_intake > 0:
        return (amount / daily_intake) * 100
    return 0

# Function to process food content data from a CSV file
def process_food_file(uploaded_food_file):
    try:
        food_data = pd.read_csv(uploaded_food_file)
        required_columns = ["sodium", "calories", "carbohydrates", "fat", "protein", "sugar"]
        for column in required_columns:
            if column not in food_data.columns:
                raise ValueError(f"Missing required column: {column}")
        food_data.columns = food_data.columns.str.strip().str.lower()
        for column in required_columns:
            food_data[column] = pd.to_numeric(
                food_data[column].astype(str).str.replace(r"[^\d.]", "", regex=True), errors="coerce"
            )
        food_data.fillna(0, inplace=True)
        return food_data
    except Exception as e:
        st.error(f"Error processing food content file: {e}")
        return None

# Streamlit App
def main():
    st.title("Daily Suggested Intake Calculator")

    # Let the user choose between manual input and CSV upload
    input_method = st.radio("Choose Input Method:", ("Manual Input", "Upload User Data CSV"))

    # Manual Input
    if input_method == "Manual Input":
        st.subheader("Manual Input")
        name = st.text_input("Enter your name:", value="")
        gender = st.text_input("Enter your gender (male/female):", value="")
        age = st.number_input("Enter your age (in years):", min_value=1, value=25, step=1)
        weight = st.number_input("Enter your weight (in kg):", min_value=1.0, value=70.0, step=0.1)
        height = st.number_input("Enter your height (in cm):", min_value=1.0, value=170.0, step=0.1)
        uploaded_user_file = None  # Disable CSV upload

    # CSV Upload
    elif input_method == "Upload User Data CSV":
        st.subheader("Upload User Data CSV")
        uploaded_user_file = st.file_uploader("Upload User Data CSV (name, gender, age, weight, height):", type=["csv"])
        name = gender = age = weight = height = None  # Disable manual input

    # File uploader for food content CSV
    st.subheader("Upload Food Content CSV")
    uploaded_food_file = st.file_uploader("Upload Food Content CSV (sodium, calories, carbohydrates, fat, protein, sugar):", type=["csv"])

    if st.button("Calculate"):
        try:
            # Process user data
            if uploaded_user_file is not None:
                user_data = process_user_data_file(uploaded_user_file)
                if user_data is not None:
                    st.subheader("Results for Uploaded Users")
                    results = []
                    for _, row in user_data.iterrows():
                        try:
                            bmr = calculate_bmr(row["gender"], row["age"], row["weight"], row["height"])
                            bmi = calculate_bmi(row["weight"], row["height"])
                            sodium_intake = 1500 if 19 <= row["age"] <= 50 else 2300
                            fat_intake = (0.30 * bmr) / 9
                            protein_min = row["weight"] * 0.8
                            protein_max = row["weight"] * 1.2
                            remaining_energy = bmr - (fat_intake * 9) - (protein_min * 4)
                            carb_intake = max(remaining_energy / 4, 0)
                            sugar_intake = suggest_daily_sugar()
                            results.append({
                                "Name": row["name"],
                                "Gender": row["gender"],
                                "Age": row["age"],
                                "Weight (kg)": row["weight"],
                                "Height (cm)": row["height"],
                                "BMR (Calories)": round(bmr, 2),
                                "BMI": round(bmi, 2),
                                "Sodium Intake (mg)": sodium_intake,
                                "Fat Intake (g)": round(fat_intake, 2),
                                "Protein Intake (g)": f"{round(protein_min, 2)} - {round(protein_max, 2)}",
                                "Carbohydrate Intake (g)": round(carb_intake, 2),
                                "Sugar Intake (g)": sugar_intake,
                            })
                        except Exception as e:
                            st.error(f"Error processing user: {e}")
                    results_df = pd.DataFrame(results)
                    st.dataframe(results_df)
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="Download Results as CSV",
                        data=csv,
                        file_name="user_results.csv",
                        mime="text/csv",
                    )
                else:
                    st.error("Failed to process the uploaded user data file.")
            elif name and gender and age is not None and weight is not None and height is not None:
                bmr = calculate_bmr(gender, age, weight, height)
                bmi = calculate_bmi(weight, height)
                sodium_intake = 1500 if 19 <= age <= 50 else 2300
                fat_intake = (0.30 * bmr) / 9
                protein_min = weight * 0.8
                protein_max = weight * 1.2
                remaining_energy = bmr - (fat_intake * 9) - (protein_min * 4)
                carb_intake = max(remaining_energy / 4, 0)
                sugar_intake = suggest_daily_sugar()
                st.subheader(f"{name}'s Results")
                st.write(f"**BMR (Calories):** {bmr:.2f}")
                st.write(f"**BMI:** {bmi:.2f}")
                st.write(f"**Sodium Intake (mg):** {sodium_intake}")
                st.write(f"**Fat Intake (g):** {fat_intake:.2f}")
                st.write(f"**Protein Intake (g):** {protein_min:.2f} - {protein_max:.2f}")
                st.write(f"**Carbohydrate Intake (g):** {carb_intake:.2f}")
                st.write(f"**Sugar Intake (g):** {sugar_intake}")
            else:
                st.error("Please provide either manual input or upload a user data CSV file.")
                # Ensure default values are None for manual input fields
                name = name if name else None
                gender = gender if gender else None
                age = age if age else None
                weight = weight if weight else None
                height = height if height else None
            # Process food content data
            if uploaded_food_file is not None:
                if not (name and gender and age is not None and weight is not None and height is not None) and uploaded_user_file is None:
                    st.error("Please provide user data (manual input or CSV) before uploading food content data.")
                    return
                if 'bmr' not in locals() or 'carb_intake' not in locals() or 'fat_intake' not in locals() or 'protein_min' not in locals():
                    st.error("Please provide user data (manual input or CSV) before uploading food content data.")
                    return
                food_data = process_food_file(uploaded_food_file)
                if food_data is not None:
                    st.subheader("Food Content Data")
                    st.dataframe(food_data)

                    # Calculate totals
                    total_sodium = food_data["sodium"].sum()
                    total_calories = food_data["calories"].sum()
                    total_carbohydrates = food_data["carbohydrates"].sum()
                    total_fat = food_data["fat"].sum()
                    total_protein = food_data["protein"].sum()
                    total_sugar = food_data["sugar"].sum()

                    # Display totals
                    st.write(f"**Total Sodium (mg):** {total_sodium}")
                    st.write(f"**Total Calories (kcal):** {total_calories}")
                    st.write(f"**Total Carbohydrates (g):** {total_carbohydrates}")
                    st.write(f"**Total Fat (g):** {total_fat}")
                    st.write(f"**Total Protein (g):** {total_protein}")
                    st.write(f"**Total Sugar (g):** {total_sugar}")

                    # Calculate percentages
                    percentages = {
                        "Sodium": calculate_percentage(total_sodium, sodium_intake) if sodium_intake > 0 else 0,
                        "Calories": calculate_percentage(total_calories, bmr) if bmr > 0 else 0,
                        "Carbohydrates": calculate_percentage(total_carbohydrates, carb_intake) if carb_intake > 0 else 0,
                        "Fat": calculate_percentage(total_fat, fat_intake) if fat_intake > 0 else 0,
                        "Protein": calculate_percentage(total_protein, protein_min) if protein_min > 0 else 0,
                        "Sugar": calculate_percentage(total_sugar, sugar_intake) if sugar_intake > 0 else 0,
                    }

                    # Display food percentages
                    st.subheader("Food Percentages")
                    for nutrient, percentage in percentages.items():
                        st.write(f"**{nutrient}:** {percentage:.2f}%" if percentage is not None else f"**{nutrient}:** N/A")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            # Removed unnecessary else block causing a compile error
if __name__ == "__main__":
    main()