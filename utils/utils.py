import streamlit as st

def api_key_input_sidebar():
    st.sidebar.header("🔑 OpenAI API Key")

    # Text input (password hidden)
    api_key = st.sidebar.text_input(
        "Enter your OpenAI API key:",
        type="password",
        placeholder="sk-...",
        key="input_api_key"  # Important: separate key so we control when to save
    )

    # Validate API Key
    if api_key:
        if api_key.startswith("sk-") and len(api_key) > 40:
            # Looks like a valid OpenAI key
            st.session_state['api_key'] = api_key
            st.sidebar.success("✅ API key saved successfully!")
        else:
            st.sidebar.error("⚠️ Invalid API key format. It should start with `sk-` and be longer than 40 characters.")
    else:
        if 'api_key' not in st.session_state:
            st.sidebar.info("Awaiting API key input...")
