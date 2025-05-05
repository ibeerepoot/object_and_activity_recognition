import streamlit as st
import json
from datetime import datetime
import re

# --- Page Setup ---
st.set_page_config(page_title="Step 5: Download Results", layout="centered", initial_sidebar_state="collapsed")

# --- Build structured export data ---
export_data = {
    "step1": {
        "profession": st.session_state.get("profession", ""),
        "source": st.session_state.get("source", ""),
        "original_object_types": st.session_state.get("original_object_types", []),
        "confirmed_object_types": st.session_state.get("confirmed_object_types", []),
        "added_object_types": st.session_state.get("added_object_types", []),
        "removed_object_types": st.session_state.get("removed_object_types", [])
    },
    "step2": st.session_state.get("step2_data", {}),
    "step3": st.session_state.get("step3_data", {}),
    "step4": st.session_state.get("step4_data", {})
}

# --- Convert to formatted JSON string ---
export_json = json.dumps(export_data, indent=4)

# --- Generate dynamic filename ---
profession = st.session_state.get("profession", "unknown").lower()
profession_clean = re.sub(r'\W+', '_', profession)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"{profession_clean}_results_{timestamp}.json"

# --- UI ---
st.title("Step 5: Export Your Data")

st.markdown("You can now download the full record of your results from steps 1 through 4.")

st.subheader("📄 Preview of Your Data")
st.json(export_data)

st.download_button(
    label="📥 Download Your Data as JSON",
    data=export_json,
    file_name=filename,
    mime="application/json"
)

cols = st.columns([1, 6, 1])
with cols[0]:
    st.page_link("pages/Step 4 - Enrich events.py", label="⬅️ Previous")
