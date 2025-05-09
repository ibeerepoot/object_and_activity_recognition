import streamlit as st
import pandas as pd

st.set_page_config(page_title="Home", page_icon="🏠", layout="centered", initial_sidebar_state="collapsed")

st.title("👋 Welcome!")

st.markdown("""
### To the Interactive Object and Activity Recognition App

This application is designed to help users identify **object types**, **activities**, and **objects** from Active Window Tracking data.  
You will be guided through a series of steps that support the interactive discovery of these elements using **GPT-4.1** and **your expert knowledge**.

#### 🔒 Data Privacy
- This is a **local Streamlit app**: none of your data is sent to any external server other than for GPT-4.1 completions.
- Your data is used only within this session and is **not stored or collected** beyond your current use.
- From the Tockler data you will upload, we will filter out all titles that occur on only one day, and then focus on the 500 most frequently occurring titles for a call to GPT-4.1. 
- Calls to GPT-4.1 are made securely and **not used for training** by OpenAI.
- Please complete all steps **in one sitting** and download your data before closing the app or refreshing the page.

#### 🧪 Evaluation Participants
If you are taking part in the research evaluation led by *Iris Beerepoot, Vinicius Stein Dani,* and *Xixi Lu*,  
please ensure you follow the app to the final step (**Step 5**) where you can view and download your results. 
These results will contain the generated object types, activities and objects, as well as the edits you made. 
In addition, we will ask you to verify a small set of titles that GPT-4.1 associated with one or more activities and objects.
Once downloaded, you are kindly requested to send the resulting JSON file to the researchers manually.  
**No data is submitted automatically.** 

Before we begin, please let us know if you'd like to make use of a set of predefined object types and activities:
""")

# --- User Type Selection ---
user_type = st.radio(
    "Make use of predefined set of object types and activities: ",
    ("Yes", "No"),
    key="user_type_selection"
)

st.session_state["user_type"] = user_type

# --- Proceed Button ---
if st.button("Continue"):
    st.session_state["user_type_confirmed"] = True

# --- Input fields shown only after user type confirmed ---
if st.session_state.get("user_type_confirmed"):

    if user_type == "Yes":
        st.session_state["profession"] = "Academic staff"
        st.info("👨‍🏫 Your profession has been set to 'Academic staff'.")
    else:
        # --- Profession ---
        profession = st.text_input("💼 Your Profession")
        if profession:
            st.session_state["profession"] = profession.strip()

    # --- API Key ---
    api_key = st.text_input("🔑 OpenAI API Key", type="password")
    if api_key:
        st.session_state["api_key"] = api_key.strip()

    # --- File Upload ---
    uploaded_file = st.file_uploader("📁 Upload your Tockler data", type="csv")
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file, sep=";")
            if df.empty:
                st.error("❌ Uploaded file is empty.")
            else:
                # Drop 'Type' column if it exists
                if 'Type' in df.columns:
                    df = df.drop(columns=['Type'])

                df['Begin'] = pd.to_datetime(df['Begin'])
                df['End'] = pd.to_datetime(df['End'])
                df['Date'] = df['Begin'].dt.date
                df['Duration'] = (df['End'] - df['Begin']).dt.total_seconds()

                # Filter titles that appear on 3 or more unique days
                days_per_title = df.groupby('Title')['Date'].nunique().reset_index(name='UniqueDays')
                df = df.merge(days_per_title, on='Title')
                df = df[df['UniqueDays'] >= 2]

                summary_df = (
                    df.groupby('Title', as_index=False)
                    .agg(Duration=('Duration', 'sum'), Frequency=('Title', 'count'))
                    .sort_values(by='Duration', ascending=False)
                    .head(500)
                )

                # Save summary and metadata
                st.session_state["step3_summary_df"] = summary_df
                st.session_state["step3_total_rows"] = len(df)

                st.success("✅ File processed successfully!")
        except Exception as e:
            st.error(f"❌ Failed to process file: {e}")

    # --- Validation ---
    all_ready = (
        st.session_state.get("api_key") and
        st.session_state.get("profession") and
        st.session_state.get("step3_summary_df") is not None
    )

    if all_ready:
        st.success("✅ All required inputs provided and processed!")
        cols = st.columns([1, 6, 1])

        with cols[2]:
            st.page_link("pages/Step 1 - Identify object types.py", label="Next ➡️")

        #st.markdown("👉 Go to **Step 1** using the sidebar to begin.")
    else:
        st.info("⬆️ Please provide all the required inputs to continue.")


