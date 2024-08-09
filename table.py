import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import pandas as pd

st.set_page_config(page_title="ASX IQ", page_icon="💹", layout="wide")
st.html("styles.html")
st.elements.utils._shown_default_value_warning=True

# Read configuration for authenticator
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
    st.title('ASX IQ - Premium analysis')


    if st.session_state["authentication_status"]:
        conn = st.connection("gsheets", type=GSheetsConnection)

        df = conn.query('''select sh1."Ticker",                          
                                    com."Company Name",                                                     
                                    sh1."Units/Currency",
                                    sh1."Quarter Ended (current quarter)",
                                    sh1."Net cash from / (used in) operating activities",
                                    sh1."Net cash from / (used in) investing activities",
                                    sh1."Net cash from / (used in) financing activities",
                                    sh1."Cash and cash equivalents at quarter end",
                                    sh1."IQ Cash",
                                    sh1."IQ Cash Burn",
                                    sh1."IQ Cash Cover",
                                    com."GICS industry group" as Industry, 
                                    sh1."Year-Quarter",   
                                    sh1."Receipts from Customers",
                                    sh1."Government grants and tax incentives",                            
                                    sh1."Proceeds from issues of equity securities",
                                    sh1."Proceeds from issue of convertible debt securities",
                                    sh1."Proceeds from borrowings",
                                    sh1."Repayment of borrowings",
                                    sh1."Dividends paid",                            
                                    sh1."Total Financing Facilities (Amount drawn at quarter end)",
                                    sh1."Unused financing facilities available at quarter end",
                                    sh1."Total relevant outgoings",
                                    sh1."Total available funding",
                                    sh1."Estimated quarters of funding available",
                                    sh1."Section 8.8",
                                    com."Business Description" from "Sheet1" sh1  
                                LEFT JOIN "Company" com on sh1.Ticker = com.Ticker 
                                where sh1."Ticker" NOT NULL''')

        df["Receipts from Customers"] = df["Receipts from Customers"].fillna(0).apply(
            lambda x: int(round(float(str(x).replace(',', '.')))))
        df["Government grants and tax incentives"] = df["Government grants and tax incentives"].fillna(0).apply(
            lambda x: int(round(float(str(x).replace(',', '.')))))
        df["Net cash from / (used in) operating activities"] = df[
            "Net cash from / (used in) operating activities"].fillna(0).apply(
            lambda x: int(round(float(str(x).replace(',', '.')))))
        df["Net cash from / (used in) investing activities"] = df[
            "Net cash from / (used in) investing activities"].fillna(0).apply(
            lambda x: int(round(float(str(x).replace(',', '.')))))
        df["Proceeds from issues of equity securities"] = df["Proceeds from issues of equity securities"].fillna(
            0).apply(lambda x: int(round(float(str(x).replace(',', '.')))))
        df["Proceeds from issue of convertible debt securities"] = df[
            "Proceeds from issue of convertible debt securities"].fillna(0).apply(
            lambda x: int(round(float(str(x).replace(',', '.')))))
        df["Proceeds from borrowings"] = df["Proceeds from borrowings"].fillna(0).apply(
            lambda x: int(round(float(str(x).replace(',', '.')))))
        df["Repayment of borrowings"] = df["Repayment of borrowings"].fillna(0).apply(
            lambda x: int(round(float(str(x).replace(',', '.')))))
        df["Dividends paid"] = df["Dividends paid"].fillna(0).apply(
            lambda x: int(round(float(str(x).replace(',', '.')))))
        df["Net cash from / (used in) financing activities"] = df[
            "Net cash from / (used in) financing activities"].fillna(0).apply(
            lambda x: int(round(float(str(x).replace(',', '.')))))
        df["Total Financing Facilities (Amount drawn at quarter end)"] = df[
            "Total Financing Facilities (Amount drawn at quarter end)"].fillna(0).apply(
            lambda x: int(round(float(str(x).replace(',', '.')))))
        df["Unused financing facilities available at quarter end"] = df[
            "Unused financing facilities available at quarter end"].fillna(0).apply(
            lambda x: int(round(float(str(x).replace(',', '.')))))
        df["Total relevant outgoings"] = df["Total relevant outgoings"].fillna(0).apply(
            lambda x: int(round(float(str(x).replace(',', '.')))))
        df["Cash and cash equivalents at quarter end"] = df["Cash and cash equivalents at quarter end"].fillna(0).apply(
            lambda x: int(round(float(str(x).replace(',', '.')))))
        df["Total available funding"] = df["Total available funding"].fillna(0).apply(
            lambda x: int(round(float(str(x).replace(',', '.')))))
        df["Total relevant outgoings"] = df["Total relevant outgoings"].fillna(0).apply(
            lambda x: int(round(float(str(x).replace(',', '.')))))
        df["IQ Cash"] = df["IQ Cash"].fillna(0).apply(lambda x: int(round(float(str(x).replace(',', '.')))))
        df["IQ Cash Burn"] = df["IQ Cash Burn"].fillna(0).apply(lambda x: int(round(float(str(x).replace(',', '.')))))
        df["Estimated quarters of funding available"] = df["Estimated quarters of funding available"].fillna(0).apply(
            lambda x: round(float(str(x).replace(',', '.')), 1))
        df['IQ Cash Cover'] = pd.to_numeric(df['IQ Cash Cover'], errors='coerce').round(1)

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

    if st.session_state["authentication_status"]:
        # Define ranges for each of the inputs
        ranges = {
            "cfo": (int(df['Net cash from / (used in) operating activities'].min()),
                    int(df['Net cash from / (used in) operating activities'].max())),
            "cfi": (int(df['Net cash from / (used in) investing activities'].min()),
                    int(df['Net cash from / (used in) investing activities'].max())),
            "cff": (int(df['Net cash from / (used in) financing activities'].min()),
                    int(df['Net cash from / (used in) financing activities'].max())),
            "iq_cash": (int(df['IQ Cash'].min()), int(df['IQ Cash'].max())),
            "iq_cash_burn": (int(df['IQ Cash Burn'].min()), int(df['IQ Cash Burn'].max())),
            "iq_cash_cover": (float(df['IQ Cash Cover'].min()), float(df['IQ Cash Cover'].max()))
        }

        # Initialize session state variables if they don't exist
        for key in ranges.keys():
            if f'{key}_slider' not in st.session_state:
                st.session_state[f'{key}_slider'] = ranges[key]
            if f'{key}_numeric_min' not in st.session_state:
                st.session_state[f'{key}_numeric_min'] = ranges[key][0]
            if f'{key}_numeric_max' not in st.session_state:
                st.session_state[f'{key}_numeric_max'] = ranges[key][1]


    # Function to update the sliders when number inputs change
    def update_slider(key_prefix):
        st.session_state[f"{key_prefix}_slider"] = (
            st.session_state[f"{key_prefix}_numeric_min"],
            st.session_state[f"{key_prefix}_numeric_max"]
        )


    if st.session_state["authentication_status"]:

        col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 1, 2])

        # CFO Inputs
        with col1:
            st.write("**CFO**")
            col1_1, col1_3 = st.columns([1, 1])
            with col1_1:
                st.number_input('Min', min_value=ranges["cfo"][0], max_value=ranges["cfo"][1], value=ranges["cfo"][0],
                                key='cfo_numeric_min', on_change=lambda: update_slider('cfo'))
            with col1_3:
                st.number_input('Max', min_value=ranges["cfo"][0], max_value=ranges["cfo"][1], value=ranges["cfo"][1],
                                key='cfo_numeric_max', on_change=lambda: update_slider('cfo'))

        # CFI Inputs
        with col3:
            st.write("**CFI**")
            col3_1, col3_3 = st.columns([1, 1])
            with col3_1:
                st.number_input('Min', min_value=ranges["cfi"][0], max_value=ranges["cfi"][1], value=ranges["cfi"][0],
                                key='cfi_numeric_min', on_change=lambda: update_slider('cfi'))
            with col3_3:
                st.number_input('Max', min_value=ranges["cfi"][0], max_value=ranges["cfi"][1], value=ranges["cfi"][1],
                                key='cfi_numeric_max', on_change=lambda: update_slider('cfi'))

        # CFF Inputs
        with col5:
            st.write("**CFF**")
            col5_1, col5_3 = st.columns([1, 1])
            with col5_1:
                st.number_input('Min', min_value=ranges["cff"][0], max_value=ranges["cff"][1], value=ranges["cff"][0],
                                key='cff_numeric_min', on_change=lambda: update_slider('cff'))
            with col5_3:
                st.number_input('Max', min_value=ranges["cff"][0], max_value=ranges["cff"][1], value=ranges["cff"][1],
                                key='cff_numeric_max', on_change=lambda: update_slider('cff'))

        col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 1, 2])

        # IQ Cash Inputs
        with col1:
            st.write("**IQ Cash**")
            col1_1, col1_3 = st.columns([1, 1])
            with col1_1:
                st.number_input('Min', min_value=ranges["iq_cash"][0], max_value=ranges["iq_cash"][1],
                                value=ranges["iq_cash"][0], key='iq_cash_numeric_min',
                                on_change=lambda: update_slider('iq_cash'))
            with col1_3:
                st.number_input('Max', min_value=ranges["iq_cash"][0], max_value=ranges["iq_cash"][1],
                                value=ranges["iq_cash"][1], key='iq_cash_numeric_max',
                                on_change=lambda: update_slider('iq_cash'))

        # IQ Cash Burn Inputs
        with col3:
            st.write("**IQ Cash Burn**")
            col3_1, col3_3 = st.columns([1, 1])
            with col3_1:
                st.number_input('Min', min_value=ranges["iq_cash_burn"][0], max_value=ranges["iq_cash_burn"][1],
                                value=ranges["iq_cash_burn"][0], key='iq_cash_burn_numeric_min',
                                on_change=lambda: update_slider('iq_cash_burn'))
            with col3_3:
                st.number_input('Max', min_value=ranges["iq_cash_burn"][0], max_value=ranges["iq_cash_burn"][1],
                                value=ranges["iq_cash_burn"][1], key='iq_cash_burn_numeric_max',
                                on_change=lambda: update_slider('iq_cash_burn'))

        # IQ Cash Cover Inputs
        with col5:
            st.write("**IQ Cash Cover**")
            col5_1, col5_3 = st.columns([1, 1])
            with col5_1:
                st.number_input('Min', min_value=ranges["iq_cash_cover"][0], max_value=ranges["iq_cash_cover"][1],
                                value=ranges["iq_cash_cover"][0], key='iq_cash_cover_numeric_min',
                                on_change=lambda: update_slider('iq_cash_cover'))
            with col5_3:
                st.number_input('Max', min_value=ranges["iq_cash_cover"][0], max_value=ranges["iq_cash_cover"][1],
                                value=ranges["iq_cash_cover"][1], key='iq_cash_cover_numeric_max',
                                on_change=lambda: update_slider('iq_cash_cover'))

    sliced_df = (
        df[
            (df['Net cash from / (used in) operating activities'] >= st.session_state.cfo_numeric_min) &
            (df['Net cash from / (used in) operating activities'] <= st.session_state.cfo_numeric_max) &
            (df['Net cash from / (used in) investing activities'] >= st.session_state.cfi_numeric_min) &
            (df['Net cash from / (used in) investing activities'] <= st.session_state.cfi_numeric_max) &
            (df['Net cash from / (used in) financing activities'] >= st.session_state.cff_numeric_min) &
            (df['Net cash from / (used in) financing activities'] <= st.session_state.cff_numeric_max) &
            (df['IQ Cash'] >= st.session_state.iq_cash_numeric_min) &
            (df['IQ Cash'] <= st.session_state.iq_cash_numeric_max) &
            (df['IQ Cash Burn'] >= st.session_state.iq_cash_burn_numeric_min) &
            (df['IQ Cash Burn'] <= st.session_state.iq_cash_burn_numeric_max) &
            (df['IQ Cash Cover'] >= st.session_state.iq_cash_cover_numeric_min) &
            (df['IQ Cash Cover'] <= st.session_state.iq_cash_cover_numeric_max)
            ]
    )



    sliced_df = sliced_df.style.applymap(lambda x: 'background-color: lightgray', subset=["IQ Cash", "IQ Cash Burn","IQ Cash Cover"])
    sliced_df = sliced_df.format({
    "Receipts from Customers": "{:,.0f}",
    "Government grants and tax incentives": "{:,.0f}",
    "Net cash from / (used in) operating activities": "{:,.0f}",
    "Net cash from / (used in) investing activities": "{:,.0f}",
    "Proceeds from issues of equity securities": "{:,.0f}",
    "Proceeds from issue of convertible debt securities": "{:,.0f}",
    "Proceeds from borrowings": "{:,.0f}",
    "Repayment of borrowings": "{:,.0f}",
    "Dividends paid": "{:,.0f}",
    "Net cash from / (used in) financing activities": "{:,.0f}",
    "Total Financing Facilities (Amount drawn at quarter end)": "{:,.0f}",
    "Unused financing facilities available at quarter end": "{:,.0f}",
    "Total relevant outgoings": "{:,.0f}",
    "Cash and cash equivalents at quarter end": "{:,.0f}",
    "Total available funding": "{:,.0f}",
    "IQ Cash": "{:,.0f}",
    "IQ Cash Burn": "{:,.0f}",
    "IQ Cash Cover": "{:,.1f}",
    })
    unique_count_total = df['Ticker'].nunique()
    unique_count_filtered = sliced_df.data['Ticker'].nunique()
    st.subheader(f"📊 Showing {unique_count_filtered}/ {unique_count_total} listings")
    st.dataframe(sliced_df, column_config={
        "Net cash from / (used in) operating activities": st.column_config.NumberColumn(label="CFO", help="Net cash from / (used in) operating activities"),
        "Net cash from / (used in) investing activities": st.column_config.NumberColumn(label="CFI",help="Net cash from / (used in) investing activities"),
        "Net cash from / (used in) financing activities": st.column_config.NumberColumn(label="CFF",help="Net cash from / (used in) financing activities"),
        "Cash and cash equivalents at quarter end": st.column_config.NumberColumn(label="Cash",help="Cash and cash equivalents at quarter end"),
                                                },
                 hide_index=True,
                 use_container_width=True)

    st.subheader("✏️ Analyze one company")


    col1, col2 = st.columns([1,3])

    with col1:
        ticker = st.selectbox(
            'Choose a ticker',
            df['Ticker'].sort_values().unique().tolist(),
            placeholder='start typing...'
        )
        if ticker:
            df1 = df[df['Ticker'] == ticker]
            st.caption(f"Info: {df1['Business Description'].iloc[0]}", )
        with col2:
            df1.set_index("Year-Quarter", inplace=True)
            df1.sort_index(ascending=False, inplace = True)
            df1 = df1.drop(['Ticker', 'Company Name','Units/Currency','Business Description', 'Industry'], axis=1)
            df1.rename(columns={"Net cash from / (used in) operating activities": "CFO",
                                "Net cash from / (used in) investing activities": "CFI",
                                "Net cash from / (used in) financing activities": "CFF",
                                "Net cash from / (used in) financing activities": "CFF",
                                "Cash and cash equivalents at quarter end": "Cash",
                                }, inplace=True)

            df1 = df1.transpose()

            st.write(" ")
            st.write(" ")
            st.dataframe(df1, key="ticker",use_container_width=True,)


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
        "document_release_date": st.column_config.DateColumn("Publication Date", format="DD-MM-YYYY"), # Date column for publication date
        "number_of_pages": "Pages",  # Column for number of pages
        "issuer_code": "Ticker"  # Column for ticker
    }, hide_index=True)

    st.subheader("🕗Recent Placements")
    st.write("Coming soon …")



####################################____________END OF PREMIUM APP______________########################################

elif st.session_state["authentication_status"] is False:
    with st.sidebar:
        st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    with st.sidebar:
        st.warning('Please enter your username and password')


# Visible to all
    st.title("ASX IQ - public")

    conn = st.connection("gsheets", type=GSheetsConnection)

    df_pub = conn.query('''select
                             pub."Ticker",
                             pub."Company Name",
                             com."GICS industry group" as Industry, 
                             pub."Quarter Ended (current quarter)",
                             pub."Net cash from / (used in) operating activities",
                             pub."Net cash from / (used in) investing activities",
                             pub."Net cash from / (used in) financing activities",    
                        com."Business Description" from "Public" pub  
                        LEFT JOIN "Company" com on pub.Ticker = com.Ticker 
                        where pub."Ticker" NOT NULL''')
    st.subheader("📊 Browse all")
    st.dataframe(df_pub, use_container_width=True, hide_index=True)

    st.subheader("✏️ Select one")
    col1, col2, col3 = st.columns(3)
    with col1:
        ticker = st.selectbox(
            'Choose a ticker',
            df_pub['Ticker'].sort_values().unique().tolist(),
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
            st.write(f"Info: {df_pub[df_pub['Ticker'] == ticker][df_pub.columns[7]].values[0]}")
        with col2:
            st.data_editor(df_pub[df_pub['Ticker'] == ticker].transpose(), key="ticker", use_container_width=True)
        with col3:
            st.metric(label="CFO", value='{:.0f}'.format(
                float(df_pub[df_pub['Ticker'] == ticker][df_pub.columns[4]].values[0].replace(' ', '').replace(',', '.'))),
                      help="Net cash from / (used in) operating activities")
            st.metric(label="CFI", value='{:.0f}'.format(df_pub[df_pub['Ticker'] == ticker][df_pub.columns[5]].values[0]),
                      help="Net cash from / (used in) investing activities")
            st.metric(label="CFF", value='{:.0f}'.format(df_pub[df_pub['Ticker'] == ticker][df_pub.columns[6]].values[0]),
                      help="Net cash from / (used in) financing activities")



