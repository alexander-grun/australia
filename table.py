import streamlit as st
from streamlit_gsheets import GSheetsConnection


conn = st.experimental_connection("gsheets", type=GSheetsConnection)

data = conn.read(spreadsheet=url, usecols=[0, 1, 2])
st.dataframe(data)