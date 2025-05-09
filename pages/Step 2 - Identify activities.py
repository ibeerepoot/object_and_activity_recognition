import streamlit as st
import openai
import json

# --- Page Setup ---
st.set_page_config(page_title="Step 2: Identify Activities", layout="centered", initial_sidebar_state="collapsed")

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

# --- Validate required inputs from Home page ---
if "api_key" not in st.session_state or "profession" not in st.session_state or "confirmed_object_types" not in st.session_state:
    st.warning("⚠️ Please complete the Home page and Step 1 before continuing.")
    st.stop()

# --- Predefined Activities for Academic Staff ---
predefined_activities = [
    "read and respond to email", "schedule meetings", "attend meetings",
    "analyze research data", "develop data analysis scripts", "visualize research results",
    "write research papers", "edit manuscripts", "collaborate on papers in Overleaf",
    "review and revise manuscripts", "manage references and citations",
    "submit manuscripts to journals or conferences", "review peer submissions",
    "prepare conference presentations", "attend and present at conferences",
    "develop research grant applications", "collaborate with colleagues",
    "supervise students", "grade assignments", "organize and manage research files",
    "search scientific literature", "read research publications"
]

# --- GPT Call to Generate Activities ---
@st.cache_data(show_spinner="🔄 Generating activities from GPT...")
def generate_activities_from_gpt(profession, object_types, api_key):
    if not object_types:
        st.error("❌ No object types provided. Please complete Step 1 first.")
        return None

    client = openai.OpenAI(api_key=api_key)

    system_prompt = """
You are an assistant specialized in semantic activity recognition. Your task is to identify high-level work activities based on a user's profession and relevant object types. 
Activities describe meaningful steps a user performs and often reflect actions in business processes.

### Task
1. Analyze the provided profession and reflect on the types of activities commonly involved in that work.
2. Analyze the provided object types. For each, identify a set of activities that typically involve, affect, or support those object types. 
3. Generate a list of relevant activities for the provided profession and object types. Include both core and supportive tasks that are recognizable within the user’s domain.

### Guidelines
- Return a list of lowercase strings.
- Do not include explanations or additional formatting.
- Focus on meaningful, commonly performed activities suitable for process mining.

### Output Format
Return a JSON array of lowercase strings:
["activity_1", "activity_2", ...]

### Example
Profession: "recruiter"
Object Types: ["applicants", "applications", "job offers", "managers"]

Output:
["review applications", "screen applicants", "schedule interviews", "coordinate with managers", "send job offers"]
"""

    user_prompt = f"Profession: {profession}\nObject Types: {json.dumps(object_types)}"

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
        if output.startswith("```"):
            output = output.split("```", 1)[1].strip()
        if output.startswith("json"):
            output = output[4:].strip()
        return json.loads(output)
    except json.JSONDecodeError as e:
        st.error(f"❌ Failed to parse GPT output: {e}")
        st.code(output)
        return None

# --- UI Start ---
st.title("Step 2: Identify Activities")

st.markdown("""
In this second step, we shift our focus to recognizing relevant activities, i.e., the actions that you perform in relation to the identified object types.
""")

user_type = st.session_state.get("user_type", "")

if user_type == "Yes":
    if 'predefined_activities_selected' not in st.session_state:
        st.session_state['predefined_activities_selected'] = predefined_activities.copy()

    new_act = st.text_input("➕ Add a new activity:", key="new_predefined_activity")
    if st.button("Add Activity", key="add_predefined_activity"):
        if new_act and new_act.lower() not in [a.lower() for a in st.session_state['predefined_activities_selected']]:
            st.session_state['predefined_activities_selected'].append(new_act.strip())
            st.success(f"✅ Added: {new_act.strip()}")

    selected = st.multiselect(
        "Edit your activities:",
        options=st.session_state['predefined_activities_selected'],
        default=st.session_state['predefined_activities_selected'],
        key="predefined_activities_multiselect"
    )

    if st.button("✅ Confirm Predefined Activities"):
        st.session_state['confirmed_activities'] = selected
        st.session_state['original_activities'] = predefined_activities.copy()
        st.session_state['added_activities'] = list(set(selected) - set(predefined_activities))
        st.session_state['removed_activities'] = list(set(predefined_activities) - set(selected))
        st.session_state['activity_source'] = "predefined"
        st.session_state['step2_data'] = {
            "profession": st.session_state.get("profession"),
            "source": "predefined",
            "original_activities": st.session_state['original_activities'],
            "confirmed_activities": st.session_state['confirmed_activities'],
            "added_activities": st.session_state['added_activities'],
            "removed_activities": st.session_state['removed_activities']
        }
        st.success("🎯 Activities confirmed from predefined list!")
        st.balloons()
else:
    object_types = st.session_state.get("confirmed_object_types")
    api_key = st.session_state.get("api_key")
    profession = st.session_state.get("profession")

    st.info(f"🔍 Using profession: **{profession}**")
    st.info(f"🧱 Using object types: {', '.join(object_types)}")

    if st.button("🔍 Generate Activities with GPT"):
        activities = generate_activities_from_gpt(profession, object_types, api_key)
        if activities:
            st.session_state['gpt_activities'] = activities.copy()
            st.session_state['gpt_activities_selected'] = activities.copy()
            st.success("✅ GPT-generated activities loaded.")
        else:
            st.error("❌ Failed to generate activities. Check your API key or input.")

    if st.session_state.get('gpt_activities'):
        new_act = st.text_input("➕ Add a new activity:", key="new_gpt_activity")
        if st.button("Add Activity", key="add_gpt_activity"):
            if new_act and new_act.lower() not in [a.lower() for a in st.session_state['gpt_activities_selected']]:
                st.session_state['gpt_activities_selected'].append(new_act.strip())
                st.success(f"✅ Added: {new_act.strip()}")
        selected = st.multiselect(
            "Edit your activities:",
            options=st.session_state['gpt_activities_selected'],
            default=st.session_state['gpt_activities_selected'],
            key="gpt_activities_multiselect"
        )
        if st.button("✅ Confirm GPT Activities"):
            original = st.session_state['gpt_activities']
            st.session_state['confirmed_activities'] = selected
            st.session_state['original_activities'] = original
            st.session_state['added_activities'] = list(set(selected) - set(original))
            st.session_state['removed_activities'] = list(set(original) - set(selected))
            st.session_state['activity_source'] = "gpt"
            st.session_state['step2_data'] = {
                "profession": st.session_state.get("profession"),
                "source": "gpt",
                "original_activities": st.session_state['original_activities'],
                "confirmed_activities": st.session_state['confirmed_activities'],
                "added_activities": st.session_state['added_activities'],
                "removed_activities": st.session_state['removed_activities']
            }
            st.success("🎯 Activities confirmed from GPT-generated list!")
            st.balloons()

cols = st.columns([1, 6, 1])

with cols[0]:
    st.page_link("pages/Step 1 - Identify object types.py", label="⬅️ Previous")

with cols[2]:
    st.page_link("pages/Step 3 - Identify objects.py", label="Next ➡️")
