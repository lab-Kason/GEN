# Function to process user data from a CSV file
def process_user_data_file(uploaded_user_file):
    try:
        # Read the CSV file into a DataFrame
        user_data = pd.read_csv(uploaded_user_file)

        # Ensure required columns exist
        required_columns = ["gender", "age", "weight", "height"]
        for column in required_columns:
            if column not in user_data.columns:
                raise ValueError(f"Missing required column: {column}")

        # Normalize column names
        user_data.columns = user_data.columns.str.strip().str.lower()

        # Validate and clean data
        user_data["gender"] = user_data["gender"].str.lower().str.strip()
        user_data["age"] = pd.to_numeric(user_data["age"], errors="coerce")
        user_data["weight"] = pd.to_numeric(user_data["weight"], errors="coerce")
        user_data["height"] = pd.to_numeric(user_data["height"], errors="coerce")

        # Drop rows with invalid or missing data
        user_data.dropna(subset=["gender", "age", "weight", "height"], inplace=True)

        return user_data
    except Exception as e:
        st.error(f"Error processing user data file: {e}")
        return None

# Streamlit App
def main():
    st.title("Daily Suggested Intake Calculator")

    # User inputs
    st.subheader("Manual Input")
    gender = st.text_input("Enter your gender (male/female):", value="male")
    age = st.number_input("Enter your age (in years):", min_value=1, value=25)
    weight = st.number_input("Enter your weight (in kg):", min_value=1.0, value=70.0)
    height = st.number_input("Enter your height (in cm):", min_value=1.0, value=170.0)

    # File uploader for user data CSV
    st.subheader("Upload User Data CSV")
    uploaded_user_file = st.file_uploader("Upload User Data CSV (gender, age, weight, height):", type=["csv"])

    # File uploader for food content CSV
    st.subheader("Upload Food Content CSV")
    uploaded_food_file = st.file_uploader("Upload Food Content CSV:", type=["csv"])

    if st.button("Calculate"):
        try:
            # Process user data from CSV if uploaded
            if uploaded_user_file is not None:
                user_data = process_user_data_file(uploaded_user_file)

                if user_data is not None:
                    st.subheader("Results for Uploaded Users")
                    results = []

                    for _, row in user_data.iterrows():
                        try:
                            # Calculate BMR and BMI for each user
                            bmr = calculate_bmr(row["gender"], row["age"], row["weight"], row["height"])
                            bmi = calculate_bmi(row["weight"], row["height"])

                            # Suggested intakes
                            sodium_intake = 1500 if 19 <= row["age"] <= 50 else 2300
                            fat_intake = (0.30 * bmr) / 9
                            protein_min = row["weight"] * 0.8
                            protein_max = row["weight"] * 1.2
                            remaining_energy = bmr - (fat_intake * 9) - (protein_min * 4)
                            carb_intake = max(remaining_energy / 4, 0)
                            sugar_intake = suggest_daily_sugar()

                            # Append results
                            results.append({
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

                    # Display results as a table
                    results_df = pd.DataFrame(results)
                    st.dataframe(results_df)

                    # Option to download results
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="Download Results as CSV",
                        data=csv,
                        file_name="user_results.csv",
                        mime="text/csv",
                    )
                else:
                    st.error("Failed to process the uploaded user data file.")
            else:
                # Manual input processing
                bmr = calculate_bmr(gender, age, weight, height)
                bmi = calculate_bmi(weight, height)

                # Suggested intakes
                sodium_intake = 1500 if 19 <= age <= 50 else 2300
                fat_intake = (0.30 * bmr) / 9
                protein_min = weight * 0.8
                protein_max = weight * 1.2
                remaining_energy = bmr - (fat_intake * 9) - (protein_min * 4)
                carb_intake = max(remaining_energy / 4, 0)
                sugar_intake = suggest_daily_sugar()

                # Display results
                st.subheader("Your Results")
                st.write(f"**BMR (Calories):** {bmr:.2f}")
                st.write(f"**BMI:** {bmi:.2f}")
                st.write(f"**Sodium Intake (mg):** {sodium_intake}")
                st.write(f"**Fat Intake (g):** {fat_intake:.2f}")
                st.write(f"**Protein Intake (g):** {protein_min:.2f} - {protein_max:.2f}")
                st.write(f"**Carbohydrate Intake (g):** {carb_intake:.2f}")
                st.write(f"**Sugar Intake (g):** {sugar_intake}")

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()