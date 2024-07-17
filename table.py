import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import pandas as pd

st.set_page_config(page_title="ASX", page_icon="💹", layout="wide")
st.html("styles.html")
st.elements.utils._shown_default_value_warning=True


###########___Functions___##################

# Function to update the slider when number input changes
def update_cfo_slider():
    st.session_state.cfo_slider = (st.session_state.cfo_numeric_min, st.session_state.cfo_numeric_max)


# Function to update number input when slider changes
def update_cfo_numeric():
    st.session_state.cfo_numeric_min, st.session_state.cfo_numeric_max = st.session_state.cfo_slider


def apply_odd_row_class(row):
    return ["background-color: #f8f8f8" if row.name % 2 != 0 else "" for _ in row]


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
    st.title('ASX - Premium analysis')

    #######################################################################___APP___#######################################
    conn = st.connection("gsheets", type=GSheetsConnection)

    df = conn.query('''select sh1."Ticker",
                            com."Company Name",
                            sh1."Year-Quarter",                            
                            sh1."Units/Currency",
                            sh1."Quarter Ended (current quarter)",
                            sh1."Receipts from Customers",
                            sh1."Government grants and tax incentives",
                            sh1."Net cash from / (used in) operating activities",
                            sh1."Net cash from / (used in) investing activities",
                            sh1."Proceeds from issues of equity securities",
                            sh1."Proceeds from issue of convertible debt securities",
                            sh1."Proceeds from borrowings",
                            sh1."Repayment of borrowings",
                            sh1."Dividends paid",
                            sh1."Net cash from / (used in) financing activities",
                            sh1."Total Financing Facilities (Amount drawn at quarter end)",
                            sh1."Unused financing facilities available at quarter end",
                            sh1."Total relevant outgoings",
                            sh1."Cash and cash equivalents at quarter end",
                            sh1."Total available funding",
                            sh1."Estimated quarters of funding available",
                            sh1."Section 8.8",
                            sh1."IQ Cash",
                            sh1."IQ Cash Burn",
                            com."Business Description" from "Sheet100" sh1  
                        LEFT JOIN "Company" com on sh1.Ticker = com.Ticker 
                        where sh1."Ticker" NOT NULL''')


    df["Receipts from Customers"] = df["Receipts from Customers"].fillna(0).astype(int)
    df["Government grants and tax incentives"] = df["Government grants and tax incentives"].fillna(0).apply(lambda x: f'{int(round(x))}').astype(int)
    df["Net cash from / (used in) operating activities"] = df["Net cash from / (used in) operating activities"].fillna(0).apply(lambda x: f'{int(round(x))}').astype(int)
    df["Net cash from / (used in) investing activities"] = df["Net cash from / (used in) investing activities"].fillna(0).apply(lambda x: f'{int(round(x))}').astype(int)
    df["Proceeds from issues of equity securities"] = df["Proceeds from issues of equity securities"].fillna(0).apply(lambda x: f'{int(round(x))}').astype(int)
    df["Proceeds from issue of convertible debt securities"] = df["Proceeds from issue of convertible debt securities"].fillna(0).apply(lambda x: f'{int(round(x))}').astype(int)
    df["Proceeds from borrowings"] = df["Proceeds from borrowings"].fillna(0).apply(lambda x: f'{int(round(x))}').astype(int)
    df["Repayment of borrowings"] = df["Repayment of borrowings"].fillna(0).apply(lambda x: f'{int(round(x))}').astype(int)
    df["Dividends paid"] = df["Dividends paid"].fillna(0).apply(lambda x: f'{int(round(x))}').astype(int)
    df["Net cash from / (used in) financing activities"] = df["Net cash from / (used in) financing activities"].fillna(0).apply(lambda x: f'{int(round(x))}').astype(int)
    df["Total Financing Facilities (Amount drawn at quarter end)"] = df["Total Financing Facilities (Amount drawn at quarter end)"].fillna(0).apply(lambda x: f'{int(round(x))}').astype(int)
    df["Unused financing facilities available at quarter end"] = df["Unused financing facilities available at quarter end"].fillna(0).apply(lambda x: f'{int(round(x))}').astype(int)
    df["Total relevant outgoings"] = df["Total relevant outgoings"].fillna(0).apply(lambda x: f'{int(round(x))}').astype(int)
    df["Cash and cash equivalents at quarter end"] = df["Cash and cash equivalents at quarter end"].fillna(0).apply(lambda x: f'{int(round(x))}').astype(int)
    df["Total available funding"] = df["Total available funding"].fillna(0).apply(lambda x: f'{int(round(x))}').astype(int)
    df["Total relevant outgoings"] = df["Total relevant outgoings"].fillna(0).apply(lambda x: f'{int(round(x))}').astype(int)
    df["IQ Cash"] = df["IQ Cash"].fillna(0).apply(lambda x: f'{int(round(x))}').astype(int)
    df["IQ Cash Burn"] = df["IQ Cash Burn"].fillna(0).apply(lambda x: f'{int(round(x))}').astype(int)


    df_url = conn.query('''select 
                            url.header,
                            url.document_release_date,
                            url.number_of_pages,
                            url.size,
                            url.url,
                            url.Predicted_Quartery_report,
                            url.issuer_code
                            from "URLS" url
                            where url.issuer_code  NOT NULL
                            AND url.header != 'error'
                            ''')

    st.subheader("📊 Browse all")

    min_cfo, max_cfo = int(df['Net cash from / (used in) operating activities'].min()), int(df['Net cash from / (used in) operating activities'].max())
    min_cfi, max_cfi = int(df['Net cash from / (used in) investing activities'].min()), int(df['Net cash from / (used in) investing activities'].max())
    min_cff, max_cff = int(df['Net cash from / (used in) financing activities'].min()), int(df['Net cash from / (used in) financing activities'].max())

    # Initialize session state variables if they don't exist
    if 'cfo_slider' not in st.session_state:
        st.session_state.cfo_slider = (min_cfo, max_cfo)
    if 'cfo_numeric_min' not in st.session_state:
        st.session_state.cfo_numeric_min = min_cfo
    if 'cfo_numeric_max' not in st.session_state:
        st.session_state.cfo_numeric_max = max_cfo

    col1, col2, col3,col4, col5 = st.columns([2,1,2,1,2])

    with col1:
        st.html('<span class="slider"></span>')
        st.subheader("CFO")
        col1_1, col1_2, col1_3 = st.columns([2, 1, 2])
        with col1_1:
            # Numeric input for CFO min and max
            st.number_input('Min', min_value=min_cfo, max_value=max_cfo, value=min_cfo, key='cfo_numeric_min',
                            on_change=update_cfo_slider)
        with col1_3:
            st.number_input('Max', min_value=min_cfo, max_value=max_cfo, value=max_cfo, key='cfo_numeric_max',
                            on_change=update_cfo_slider)

        # Slider for CFO
        st.slider("CFO", min_value=min_cfo, max_value=max_cfo, value=(min_cfo, max_cfo), key='cfo_slider',
                  on_change=update_cfo_numeric, label_visibility="hidden")


    with col3:
        cfi_slicer = st.slider("CFI", min_value=min_cfi, max_value=max_cfi, value=(min_cfi, max_cfi))

    with col5:
        cff_slicer = st.slider("CFF", min_value=min_cff, max_value=max_cff, value=(min_cff, max_cff))

    sliced_df = (df[(df['Net cash from / (used in) operating activities'] >= st.session_state.cfo_slider[0]) &
                    (df['Net cash from / (used in) operating activities'] <= st.session_state.cfo_slider[1]) &
                    (df['Net cash from / (used in) investing activities'] >= cfi_slicer[0]) &
                    (df['Net cash from / (used in) investing activities'] <= cfi_slicer[1]) &
                    (df['Net cash from / (used in) financing activities'] >= cff_slicer[0]) &
                    (df['Net cash from / (used in) financing activities'] <= cff_slicer[1])])


    st.dataframe(sliced_df, column_config={
        "Net cash from / (used in) operating activities": st.column_config.NumberColumn(label="CFO", help="Net cash from / (used in) operating activities"),
        "Net cash from / (used in) investing activities": st.column_config.NumberColumn(label="CFI",help="Net cash from / (used in) investing activities"),
        "Net cash from / (used in) financing activities": st.column_config.NumberColumn(label="CFF",help="Net cash from / (used in) financing activities"),
                                                },
                 hide_index=True,
                 use_container_width=True)

    st.subheader("✏️ Analyze one company")
    col1, col2, col3 = st.columns([1,1,3])
    with col1:
        ticker = st.selectbox(
            'Choose a ticker',
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
        col1, col2, col3 = st.columns([1,3,1])
        df1 = df[df['Ticker'] == ticker]
        with col1:
            st.caption(f"Info: {df1['Business Description'].iloc[0]}", )
        with col2:
            df1.set_index("Year-Quarter", inplace=True)
            df1.sort_index(ascending=False, inplace = True)
            st.dataframe(df1.transpose(), key="ticker", use_container_width=True, )


        with col3:
            st.metric(label="CFO", value='{:.0f}'.format(float(df1["Net cash from / (used in) operating activities"].iloc[0])),
                      help="Net cash from / (used in) operating activities")
            st.metric(label="CFI", value='{:.0f}'.format(float(df1["Net cash from / (used in) investing activities"].iloc[0])),
                      help="Net cash from / (used in) investing activities")
            st.metric(label="CFF", value='{:.0f}'.format(float(df1["Net cash from / (used in) financing activities"].iloc[0])),
                      help="Net cash from / (used in) financing activities")

        st.subheader("📄Reports/Announcements")

        # Data preprocessing and type conversion
        df_url['Predicted_Quartery_report'] = df_url['Predicted_Quartery_report'].fillna(0).astype(int)
        df_url['number_of_pages'] = df_url['number_of_pages'].fillna(0).astype(int)
        df_url['document_release_date'] = pd.to_datetime(df_url['document_release_date'], errors='coerce')
        df_url['document_release_date'] = df_url['document_release_date'].apply(
            lambda x: x.strftime('%m-%d-%Y') if pd.notnull(x) else x)

        # Toggle to show all announcements or only quarterly reports
        on = st.toggle("Show all Announcements")
        if on:
            df_url = df_url[df_url['issuer_code'] == ticker].copy()  # Filter by ticker if show all is toggled on
        else:
            st.caption("Reports only")
            df_url = df_url[(df_url['issuer_code'] == ticker) & (
                        df_url['Predicted_Quartery_report'] == 1)].copy()  # Filter for quarterly reports if toggled off

        # Dropping unnecessary column and resetting index
        df_url = df_url.drop(columns=['Predicted_Quartery_report'])
        df_url = df_url.reset_index(drop=True)

        # Displaying the DataFrame with specific column configurations
        st.dataframe(df_url, column_config={
            "url": st.column_config.LinkColumn("URL"),  # Link column for URL
            "document_release_date": st.column_config.DateColumn("Publication Date", format="DD-MM-YYYY"),
            # Date column for publication date
            "number_of_pages": "Pages",  # Column for number of pages
            "issuer_code": "Ticker"  # Column for ticker
        }, hide_index=True)


####################################____________END OF PREMIUM APP______________########################################

elif st.session_state["authentication_status"] is False:
    with st.sidebar:
        st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    with st.sidebar:
        st.warning('Please enter your username and password')


# Visible to all
    st.title("ASX - public")

    conn = st.connection("gsheets", type=GSheetsConnection)

    df = conn.query('''select
                             pub."Ticker",
                             pub."Company Name",
                             pub."Quarter Ended (current quarter)",
                             pub."Net cash from / (used in) operating activities",
                             pub."Net cash from / (used in) investing activities",
                             pub."Net cash from / (used in) financing activities",    
                        com."Business Description" from "Public" pub  
                        LEFT JOIN "Company" com on pub.Ticker = com.Ticker 
                        where pub."Ticker" NOT NULL''')
    st.subheader("📊 Browse all")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("✏️ Select one")
    col1, col2, col3 = st.columns(3)
    with col1:
        ticker = st.selectbox(
            'Choose a ticker',
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
            st.metric(label="CFO", value='{:.0f}'.format(
                float(df[df['Ticker'] == ticker][df.columns[3]].values[0].replace(' ', '').replace(',', '.'))),
                      help="Net cash from / (used in) operating activities")
            st.metric(label="CFI", value='{:.0f}'.format(df[df['Ticker'] == ticker][df.columns[4]].values[0]),
                      help="Net cash from / (used in) investing activities")
            st.metric(label="CFF", value='{:.0f}'.format(df[df['Ticker'] == ticker][df.columns[5]].values[0]),
                      help="Net cash from / (used in) financing activities")



