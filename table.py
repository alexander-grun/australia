import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

if "dta" not in st.session_state:
    st.session_state.dta = None

df=pd.DataFrame({ "Name": ['Paul', 'Gina'], "Age": [43, 35], "Inducted": [True, False],
                  "Firm": ['Google', 'Microsoft'], "JDesc": ['Analyst', 'Programmer']})
gridOptions = GridOptionsBuilder.from_dataframe(df)
gridOptions.configure_selection('single', use_checkbox=True)
gb = gridOptions.build()

def sub_page():
    st.subheader("Sub Page")
    st.write(f'Name: {st.session_state.dta["selected_rows"][0]["Name"]}')
    st.write(f'Firm: {st.session_state.dta["selected_rows"][0]["Firm"]}')

    if st.button("Return to Main Page"):
        st.session_state.runpage = main_page
        st.rerun()

def main_page():
    st.subheader("Main Page")
    st.session_state.dta = AgGrid(df, gridOptions=gb, height=150, update_mode=GridUpdateMode.SELECTION_CHANGED)

    if len(st.session_state.dta["selected_rows"]) == 1:
        st.session_state.runpage = sub_page
        st.rerun()

if 'runpage' not in st.session_state:
    st.session_state.runpage = main_page
st.session_state.runpage()