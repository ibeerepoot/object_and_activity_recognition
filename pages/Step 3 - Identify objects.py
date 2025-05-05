import streamlit as st
import pandas as pd
import openai
import json

# --- Page Setup ---
st.set_page_config(page_title="Step 3: Identify Objects", layout="centered", initial_sidebar_state="collapsed")

st.title("Step 3: Identify Objects")

st.markdown("""
The third step identifies concrete object instances, that is, specific entities that appear in your data and instantiate one of the previously verified object types.
We will use gpt-4.1 to generate a list of possibly relevant objects, with corresponding object types. 
Please review them and edit them where necessary, as well as unchecking the ones that are irrelevant for you to analyze your work processes.
""")

# --- Pull processed data ---
if "step3_summary_df" not in st.session_state or "step3_total_rows" not in st.session_state:
    st.warning("⚠️ Please upload and process your dataset on the Home page before continuing.")
    st.stop()

summary_df = st.session_state["step3_summary_df"]
total_rows = st.session_state["step3_total_rows"]

# --- UI ---
st.markdown("---")
st.header("🔍 Generate Objects with GPT")

api_key = st.session_state.get("api_key")
profession = st.session_state.get("profession")
object_types = st.session_state.get("confirmed_object_types")
activities = st.session_state.get("confirmed_activities")

if not (profession and object_types and activities):
    st.warning("⚠️ Please make sure you have completed Step 1 and Step 2 (profession, object types, and activities).")

elif api_key:
    if 'step3_gpt_objects' not in st.session_state:
        if st.button("🧠 Generate Objects with GPT"):
            client = openai.OpenAI(api_key=api_key)
            titles = summary_df['Title'].tolist()

            system_prompt = """
You are an assistant specialized in extracting object instances from textual digital traces.
Your task is to identify distinct object instances and assign them to appropriate object types.
This is part of preparing structured data for object-centric process mining.

### Task
1. Analyze a list of window titles in context of a given profession, confirmed object types, and activities.
2. Identify specific objects (e.g., "project alpha", "thesis john doe") mentioned or implied in those titles.
3. Assign each object to the most appropriate type from the provided list.

### Guidelines
- Do not repeat objects (no duplicates).
- Do not assign the object name to be exactly the same as its object type.
- If the object type is a person (e.g., student, colleague), use a plausible name as object.
- Consider abbreviations, concatenations, or project/document references in titles.
- The result should help map interactions to real-world entities.

### Output Format
A JSON array of dictionaries:
[
  {"object": "project alpha", "object_type": "research project"},
  {"object": "john doe", "object_type": "colleague"}
]
"""

            user_prompt = f"""
Profession: {profession}
Object Types: {json.dumps(object_types)}
Activities: {json.dumps(activities)}
Window Titles: {json.dumps(titles)}
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

                # Extract the first JSON block if multiple outputs are present
                if "```json" in output:
                    output = output.split("```json")[1].split("```", 1)[0].strip()
                elif "```" in output:
                    output = output.split("```", 1)[1].split("```", 1)[0].strip()

                #st.markdown("**🔎 Raw GPT Output:**")
                #st.code(output, language="json")
                object_data = json.loads(output)
                st.session_state['step3_gpt_objects'] = object_data
                st.session_state['step3_edited_objects'] = pd.DataFrame(object_data)

            except Exception as e:
                st.error(f"❌ GPT call failed: {e}")

    if 'step3_edited_objects' in st.session_state:
        df_objects = st.session_state['step3_edited_objects'].copy()

        if 'Confirm' not in df_objects.columns:
            df_objects['Confirm'] = True

        df_objects['object_type'] = pd.Categorical(df_objects['object_type'], categories=object_types)

        edited_df = st.data_editor(
            df_objects,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Confirm": st.column_config.CheckboxColumn("Confirm", help="Check to keep this object"),
                "object_type": st.column_config.SelectboxColumn("Object Type", options=object_types)
            },
            key="object_editor"
        )

        # Only update session state after explicit confirmation
        if st.button("✅ Confirm Objects"):
            st.session_state['step3_edited_objects'] = edited_df  # Safe to store final state now

            confirmed_df = edited_df[edited_df['Confirm']].drop(columns=['Confirm'])
            st.session_state['step3_objects_df'] = confirmed_df
            st.session_state['step3_data'] = {
                "total_rows": total_rows,
                "gpt_suggestions": st.session_state['step3_gpt_objects'],
                "confirmed_objects": confirmed_df.to_dict(orient="records")
            }
            st.success("🎯 Object suggestions processed and saved!")

cols = st.columns([1, 6, 1])

with cols[0]:
    st.page_link("pages/Step 2 - Identify activities.py", label="⬅️ Previous")

with cols[2]:
    st.page_link("pages/Step 4 - Enrich events.py", label="Next ➡️")
