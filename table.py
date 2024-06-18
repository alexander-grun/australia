import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit_authenticator as stauth


st.set_page_config(page_title="ASX", page_icon="💹", layout="wide")
st.html("styles.html")


conn = st.connection("gsheets", type=GSheetsConnection)


df = conn.query('select * from "Sheet1" where "Ticker" NOT NULL', usecols=list(range(20)))

def display_table(df):
    def apply_odd_row_class(row):
        return ["background-color: #f8f8f8" if row.name % 2 != 0 else "" for _ in row]

    styled_df = df.style.apply(apply_odd_row_class, axis=1)

    st.dataframe(styled_df, use_container_width=True)

st.title("📊 ASX")
st.subheader("Browse all")
display_table(df)

st.subheader("Select one")
col1, col2, col3  = st.columns(3)
with col1:
    st.write("Ticker")
    ticker = st.selectbox(
        'Choose a Ticker',
        df['Ticker'].sort_values().unique().tolist(),
        placeholder='start typing...'
    )

with col2:
    pass
    # st.write("Company Name")
    # company_name = st.selectbox(
    #     'Choose a Company',
    #     df['Company Name'].sort_values().unique().tolist(),
    #     index=None,
    #     placeholder='start typing...'
    # )
with col3:
    pass

# if company_name :
#     st.data_editor(df[df['Company Name'] == company_name].transpose(), key="name")
if ticker:

    col1, col2,col3 = st.columns(3)
    with col1:
        st.data_editor(df[df['Ticker'] == ticker].transpose(), key="ticker", use_container_width=True)
    with col2:
        pass
    with col3:
        st.metric(label="CFO", value='{:,.1f}'.format(
            float(df[df['Ticker'] == ticker][df.columns[6]].values[0].replace(' ', '').replace(',', '.'))),
                  help="Net cash from / (used in) operating activities")
        st.metric(label="CFI", value='{:,.1f}'.format(df[df['Ticker'] == ticker][df.columns[7]].values[0]),
                  help="Net cash from / (used in) investing activities")
        st.metric(label="CFF", value='{:,.1f}'.format(df[df['Ticker'] == ticker][df.columns[13]].values[0]),
                  help="Net cash from / (used in) financing activities")


    # st.write(f'Info: {df[df['Company Name'] == company_name]["Business Description"].values[0]}')