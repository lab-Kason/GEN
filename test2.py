import pandas as pd
import streamlit as st

# Function to calculate BMR
def calculate_bmr(gender, age, weight, height):
    if gender.lower() == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    elif gender.lower() == "female":
        return 10 * weight + 6.25 * height - 5 * age - 161
    else:
        raise ValueError("Invalid gender. Please enter 'male' or 'female'.")

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

# Streamlit App
def main():
    st.title("Daily Suggested Intake Calculator")

    # User inputs
    st.subheader("Manual Input")
    name = st.text_input("Enter your name:", value="", disabled=False)
    gender = st.text_input("Enter your gender (male/female):", value="", disabled=False)
    age = st.number_input("Enter your age (in years):", min_value=1, value=None, step=1, disabled=False)
    weight = st.number_input("Enter your weight (in kg):", min_value=1.0, value=None, step=0.1, disabled=False)
    height = st.number_input("Enter your height (in cm):", min_value=1.0, value=None, step=0.1, disabled=False)

    # File uploader for user data CSV
    st.subheader("Upload User Data CSV")
    uploaded_user_file = st.file_uploader("Upload User Data CSV (name, gender, age, weight, height):", type=["csv"], disabled=False)

    # Logic to disable one input method based on the other
    if name or gender or age or weight or height:
        st.warning("Manual input detected. User data CSV upload is disabled.")
        uploaded_user_file = None  # Disable CSV upload
    elif uploaded_user_file is not None:
        st.warning("User data CSV uploaded. Manual input is disabled.")
        name = gender = age = weight = height = None  # Disable manual input

    if st.button("Calculate"):
        try:
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
            elif name and gender and age and weight and height:
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
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()