
import streamlit as st
def get_state():
    if 'state' not in st.session_state:
        st.session_state['state'] = {}
    return st.session_state['state']
