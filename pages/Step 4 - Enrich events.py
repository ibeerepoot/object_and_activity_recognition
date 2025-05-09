import streamlit as st
import openai
import pandas as pd
import json
import random
import math
import collections

# --- Page Setup ---
st.set_page_config(page_title="Step 4: Enrich Events", layout="centered", initial_sidebar_state="collapsed")

# --- Custom CSS to shrink multiselect pills ---
st.markdown("""
    <style>
    .stMultiSelect [data-baseweb="select"] span {
        max-width: 500px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Step 4: Enrich Events")

st.markdown("""
In this final step, we'll associate your window titles with the most likely objects and activities using GPT-4.1.
You will be shown a set of random examples for review and correction. 
Please check if you agree with the associated activities and objects and edit them where necessary, before confirming. 
After confirming, you will be asked to rate the quality of the activity and object labels. 
""")

# --- Validate required data ---
required_keys = ["step3_summary_df", "step3_objects_df", "confirmed_activities", "profession", "api_key"]
if not all(k in st.session_state for k in required_keys):
    st.warning("⚠️ Please ensure all previous steps are completed and inputs provided.")
    st.stop()

# --- Extract Data ---
summary_df = st.session_state["step3_summary_df"]
titles = summary_df["Title"].tolist()
if len(titles) > 100:
    titles = random.sample(titles, 100)
profession = st.session_state["profession"]
api_key = st.session_state["api_key"]
objects_df = st.session_state["step3_objects_df"]
confirmed_activities = st.session_state["confirmed_activities"]
object_mappings = objects_df.to_dict(orient="records")

# --- GPT Call ---
@st.cache_data(show_spinner="🔄 Enriching a batch of titles with GPT-4.1")
def enrich_titles_batch(profession, objects, activities, batch_titles, api_key):
    client = openai.OpenAI(api_key=api_key)
    system_prompt = """
You are an assistant specialized in associating textual titles with objects and activities relevant to professional workflows.
Your task is to infer meaningful semantic associations between window titles and known entities.
"""
    user_prompt = f"""
### Task
For each of the following window titles, determine whether it clearly relates to one or more of the given activities and one or more of the given objects. 
If so, return the title and its associated activities and objects. Otherwise, return only the title with empty lists.

### Guidelines
- Use your understanding of the user's profession to ground your associations.
- Include objects and activities only if they are directly and unambiguously implied.
- Avoid guessing or over-interpreting vague titles.

### Output Format
Return a JSON array of dictionaries with the following structure:
[{{"title": "some title text", "activities": ["activity A"], "objects": ["object X"]}}]

### Input
Profession: {profession}
Objects and Types: {json.dumps(objects)}
Activities: {json.dumps(activities)}
Titles: {json.dumps(batch_titles)}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        output = response.choices[0].message.content.strip()
        if "```json" in output:
            output = output.split("```json")[1].split("```", 1)[0].strip()
        elif "```" in output:
            output = output.split("```", 1)[1].split("```", 1)[0].strip()
        return json.loads(output)
    except Exception as e:
        st.error(f"❌ GPT call failed: {e}")
        return []

# --- Trigger GPT only on button click ---
if "step4_gpt_enrichment" not in st.session_state:
    if st.button("🔍 Generate Title Enrichments with GPT"):
        all_valid = []
        batch_size = 10
        num_batches = math.ceil(len(titles) / batch_size)
        for i in range(num_batches):
            start = i * batch_size
            end = start + batch_size
            batch = titles[start:end]
            with st.spinner(f"Processing batch {i+1} of {num_batches}..."):
                enriched = enrich_titles_batch(profession, object_mappings, confirmed_activities, batch, api_key)
                valid = [item for item in enriched if item.get("activities") and item.get("objects")]
                all_valid.extend(valid)
        if not all_valid:
            st.warning("⚠️ GPT did not find any titles with both activities and objects. Please review your input.")
            st.stop()
        st.session_state["step4_gpt_enrichment"] = all_valid
        st.session_state["step4_sampled_titles"] = random.sample(all_valid, k=min(10, len(all_valid)))
        st.rerun()

# --- Proceed only if GPT results exist ---
if "step4_gpt_enrichment" in st.session_state:
    st.subheader("✍️ Review and Edit Enrichments")
    activity_options = confirmed_activities
    object_options = list(objects_df["object"].unique())
    edited_rows = []
    for i, row in enumerate(st.session_state["step4_sampled_titles"]):
        st.markdown(f"**{i+1}. {row['title']}")
        col1, col2 = st.columns(2)
        with col1:
            activities = st.multiselect("Activities", options=activity_options, default=row["activities"], key=f"activities_{i}")
        with col2:
            objects = st.multiselect("Objects", options=object_options, default=row["objects"], key=f"objects_{i}")
        edited_rows.append({"title": row["title"], "activities": activities, "objects": objects})

    if st.button("✅ Confirm Event Enrichment"):
        st.session_state["step4_data"] = {
            "gpt_suggestions": st.session_state["step4_gpt_enrichment"],
            "reviewed_sample": edited_rows
        }
        st.success("🎯 Annotations saved!")
        st.balloons()

        st.subheader("⭐ Finally, please rate the GPT Labeling Quality")
        activity_rating = st.slider("How would you rate the quality of the activity labels?", 1, 5, 3)
        object_rating = st.slider("How would you rate the quality of the object labels?", 1, 5, 3)
        st.session_state["step4_data"]["activity_rating"] = activity_rating
        st.session_state["step4_data"]["object_rating"] = object_rating
        st.success("✅ Thank you for your feedback!")

cols = st.columns([1, 6, 1])
with cols[0]:
    st.page_link("pages/Step 3 - Identify objects.py", label="⬅️ Previous")
with cols[2]:
    st.page_link("pages/Step 5 - Download results.py", label="Next ➡️")
