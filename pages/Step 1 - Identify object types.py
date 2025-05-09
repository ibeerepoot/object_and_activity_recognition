import streamlit as st
import openai
import json

# --- Page Setup ---
st.set_page_config(page_title="Step 1: Identify Object Types", layout="centered", initial_sidebar_state="collapsed")

# --- Validate required inputs from Home page ---
if "api_key" not in st.session_state or "profession" not in st.session_state:
    st.warning("⚠️ Please enter your API key and profession on the Home page before continuing.")
    st.stop()

# --- Predefined Object Types ---
predefined_object_types = [
    "courses", "students", "lectures", "assignments", "research projects",
    "publications", "colleagues", "meetings", "departments", "emails",
    "exams", "grades", "syllabi", "conferences", "grant applications"
]

# --- GPT Call ---
@st.cache_data(show_spinner="🔄 Generating object types from GPT...")
def generate_object_types_from_gpt(profession, api_key):
    client = openai.OpenAI(api_key=api_key)
    system_prompt = """
You are an assistant specialized in semantic object recognition. Your task is to identify high-level object types based on a user’s profession. Object types represent general categories, human and non-human, and are used in object-centric event logs to group related entities.

### Task
1. Analyze the provided profession and reflect on the types of entities commonly involved in that work.
2. Identify a list of relevant object types that could occur in the user's work processes.
3. Focus on categories of entities, not specific instances or activities.

### Guidelines
- Output only lowercase string literals.
- Do not include any explanation or commentary.
- Include a broad range of object types that are reasonably relevant to the profession
- Ensure object types are distinct and profession-relevant.

### Output Format
Return a JSON array of lowercase strings:
```json
["object_type_1", "object_type_2", ...]
```

### Example
Profession: "recruiter"

Output:
```json
["applicants", "applications", "managers", "offers", "vacancies"]
```
"""

    user_prompt = f"Profession: \"{profession}\""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        output = response.choices[0].message.content
        if output.startswith("```json"):
            output = output.strip("` ").replace("json", "").strip()
        return json.loads(output)
    except json.JSONDecodeError as e:
        st.error(f"❌ Failed to parse GPT response. Error: {e}")
        st.code(output)
        return None

# --- UI ---
st.title("Step 1: Identify Object Types")

st.markdown("""
This first step focuses on identifying relevant object types, i.e., general categories of entities that are relevant in your work, which can be people and things.
""")

user_type = st.session_state.get("user_type", "")

if user_type == "Yes":
    st.markdown("You are using a predefined list of object types tailored for academic staff. " \
        "Please review them and reflect on whether are likely to appear in your work."
        "You may add additional types or delete ones that are irrelevant in your work context.")

    if 'predefined_selected' not in st.session_state:
        st.session_state['predefined_selected'] = predefined_object_types.copy()

    new_object = st.text_input("➕ Add a new object type:", key="new_predefined_object")

    if st.button("Add Object Type", key="add_predefined"):
        if new_object and new_object.lower() not in [obj.lower() for obj in st.session_state['predefined_selected']]:
            st.session_state['predefined_selected'].append(new_object.strip())
            st.success(f"✅ Added new object type: {new_object.strip()}")
        else:
            st.warning("⚠️ Object type already exists or input is empty.")

    selected = st.multiselect(
        "Object types (editable):",
        options=st.session_state['predefined_selected'],
        default=st.session_state['predefined_selected'],
        key="predefined_multiselect"
    )

    if st.button("✅ Confirm Academic Staff Object Types"):
        original_set = set(predefined_object_types)
        final_set = set(selected)
        st.session_state['original_object_types'] = list(original_set)
        st.session_state['confirmed_object_types'] = list(final_set)
        st.session_state['added_object_types'] = list(final_set - original_set)
        st.session_state['removed_object_types'] = list(original_set - final_set)
        st.session_state['source'] = "predefined"
        st.success("🎯 Object types confirmed from predefined list!")
        st.balloons()

else:
    st.markdown("You will generate a customized list of object types based on your profession."\
        "Please review them and reflect on whether are likely to appear in your work. " \
        "You may add additional types or delete ones that are irrelevant in your work context."
    )

    profession_input = st.session_state.get("profession", "")
    api_key = st.session_state.get("api_key")

    if st.button("🔍 Generate Object Types"):
        if not api_key:
            st.error("⚠️ OpenAI API key not found.")
        elif not profession_input.strip():
            st.error("⚠️ Please enter a valid profession.")
        else:
            gpt_types = generate_object_types_from_gpt(profession_input.strip(), api_key)
            if gpt_types:
                st.session_state['gpt_object_types'] = gpt_types.copy()
                st.session_state['gpt_selected'] = gpt_types.copy()
                st.session_state['source'] = "gpt"
                st.success("✅ Object types generated!")
            else:
                st.error("❌ No object types could be generated. Please check your input or try again.")

    if st.session_state.get('gpt_selected'):
        new_gpt_object = st.text_input("➕ Add a new object type:", key="new_gpt_object")

        if st.button("Add Object Type", key="add_gpt"):
            if new_gpt_object and new_gpt_object.lower() not in [obj.lower() for obj in st.session_state['gpt_selected']]:
                st.session_state['gpt_selected'].append(new_gpt_object.strip())
                st.success(f"✅ Added new object type: {new_gpt_object.strip()}")
            else:
                st.warning("⚠️ Object type already exists or input is empty.")

        gpt_selected = st.multiselect(
            "Object types (editable):",
            options=st.session_state['gpt_selected'],
            default=st.session_state['gpt_selected'],
            key="gpt_multiselect"
        )

        if st.button("✅ Confirm GPT-Generated Object Types"):
            original_set = set(st.session_state['gpt_object_types'])
            final_set = set(gpt_selected)
            st.session_state['confirmed_object_types'] = list(final_set)
            st.session_state['added_object_types'] = list(final_set - original_set)
            st.session_state['removed_object_types'] = list(original_set - final_set)
            st.session_state['original_object_types'] = list(original_set)
            st.success("🎯 Object types confirmed from GPT!")
            st.balloons()

cols = st.columns([1, 6, 1])

with cols[0]:
    st.page_link("Home.py", label="⬅️ Previous")

with cols[2]:
    st.page_link("pages/Step 2 - Identify activities.py", label="Next ➡️")
