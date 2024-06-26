import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

st.set_page_config(page_title="ASX", page_icon="💹", layout="wide")
st.html("styles.html")


###########___Functions___##################

def display_table(df):
    def apply_odd_row_class(row):
        return ["background-color: #f8f8f8" if row.name % 2 != 0 else "" for _ in row]

    styled_df = df.style.apply(apply_odd_row_class, axis=1)

    st.dataframe(styled_df, use_container_width=True)

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

authenticator.login(location='sidebar')

if st.session_state["authentication_status"]:
    authenticator.logout(location='sidebar')
    with st.sidebar:
        st.write(f'Welcome *{st.session_state["name"]}*',)
    st.title('Premium analysis')

    #######################################################################___APP___#######################################
    conn = st.connection("gsheets", type=GSheetsConnection)

    df = conn.query('''select sh1.*, com."Business Description" from "Sheet1" sh1  
                        LEFT JOIN "Company" com on sh1.Ticker = com.Ticker 
                        where sh1."Ticker" NOT NULL''',
                    usecols=list(range(20)))

    st.title("📊 ASX")
    st.subheader("Browse all")

    display_table(df)

    st.subheader("Select one")
    col1, col2, col3 = st.columns(3)
    with col1:
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
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"Info: {df[df['Ticker'] == ticker][df.columns[20]].values[0]}")
        with col2:
            st.data_editor(df[df['Ticker'] == ticker].transpose(), key="ticker", use_container_width=True)
        with col3:
            st.metric(label="CFO", value='{:,.1f}'.format(
                float(df[df['Ticker'] == ticker][df.columns[6]].values[0].replace(' ', '').replace(',', '.'))),
                      help="Net cash from / (used in) operating activities")
            st.metric(label="CFI", value='{:,.1f}'.format(df[df['Ticker'] == ticker][df.columns[7]].values[0]),
                      help="Net cash from / (used in) investing activities")
            st.metric(label="CFF", value='{:,.1f}'.format(df[df['Ticker'] == ticker][df.columns[13]].values[0]),
                      help="Net cash from / (used in) financing activities")



elif st.session_state["authentication_status"] is False:
    with st.sidebar:
        st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    with st.sidebar:
        st.warning('Please enter your username and password')


# Visible to all
    st.title("ASX - public")

    conn = st.connection("gsheets", type=GSheetsConnection)

    df = conn.query('''select pub.*, com."Business Description" from "Public" pub  
                        LEFT JOIN "Company" com on pub.Ticker = com.Ticker 
                        where pub."Ticker" NOT NULL''', usecols=list(range(6)))
    st.subheader("Browse all")
    display_table(df)

    st.subheader("Select one")
    col1, col2, col3 = st.columns(3)
    with col1:
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
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"Info: {df[df['Ticker'] == ticker][df.columns[6]].values[0]}")
        with col2:
            st.data_editor(df[df['Ticker'] == ticker].transpose(), key="ticker", use_container_width=True)
        with col3:
            st.metric(label="CFO", value='{:,.1f}'.format(
                float(df[df['Ticker'] == ticker][df.columns[3]].values[0].replace(' ', '').replace(',', '.'))),
                      help="Net cash from / (used in) operating activities")
            st.metric(label="CFI", value='{:,.1f}'.format(df[df['Ticker'] == ticker][df.columns[4]].values[0]),
                      help="Net cash from / (used in) investing activities")
            st.metric(label="CFF", value='{:,.1f}'.format(df[df['Ticker'] == ticker][df.columns[5]].values[0]),
                      help="Net cash from / (used in) financing activities")



