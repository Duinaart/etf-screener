import streamlit as st
import pandas as pd
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

# Set page config for a wider layout
st.set_page_config(layout="wide", page_title="ETF Screener", initial_sidebar_state="collapsed")

# Custom CSS for styling
st.markdown("""
    <style>
    /* Dark theme */
    .stApp {
        background-color: #1E1E1E;
        color: white;
    }
    
    /* Filter container */
    .filter-container {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
    }
    
    .filter-label-section {
        display: flex;
        align-items: center;
        background-color: rgba(255, 255, 255, 0.1);
        padding: 8px 12px;
        border-radius: 6px;
        width: 140px;
    }
    
    .filter-number {
        color: #888;
        font-size: 13px;
        margin-right: 12px;
    }
    
    .filter-label {
        color: #888;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Dropdown styling */
    .stSelectbox [data-baseweb="select"], 
    .stMultiSelect [data-baseweb="select"] {
        background-color: transparent !important;
        border: none !important;
        max-width: 200px !important;
    }

    /* Remove padding from containers */
    .element-container {
        margin: 0 !important;
    }
    .stSelectbox {
        margin: 0 !important;
    }
    .stMultiSelect {
        margin: 0 !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Title styling */
    h1 {
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 24px;
        color: white;
    }

    /* Clear Filters button */
    .stButton button {
        background-color: rgba(255, 255, 255, 0.1);
        color: #888;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 13px;
        margin-bottom: 16px;
    }
    
    .stButton button:hover {
        background-color: rgba(255, 255, 255, 0.15);
        color: white;
    }

    /* ETF count text */
    .etf-count {
        color: #888;
        font-size: 13px;
        margin-top: 16px;
    }
    </style>
""", unsafe_allow_html=True)

def clean_options(options):
    """Remove NaN values from options only"""
    return sorted([opt for opt in options if pd.notna(opt)])

def create_filter_row(number, label):
    col1, col2 = st.columns([0.4, 0.6])  # Adjusted ratio to prevent overlap
    with col1:
        st.markdown(
            f"""
            <div class="filter-container">
                <div class="filter-label-section">
                    <span class="filter-number">{number}</span>
                    <span class="filter-label">{label}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    return col2

def main():
    if 'filters_initialized' not in st.session_state:
        st.session_state.filters_initialized = True
        st.session_state.super_region_select = None
        st.session_state.region_group_select = None
        st.session_state.specific_region_select = None
        st.session_state.currency_select = None
        st.session_state.dividend_policy_select = None
        st.session_state.issuer_select = None
        st.session_state.equity_category = None

    st.title("ETF Screener")
    
    try:
        df = pd.read_csv('sample_df.csv')
        df = df.rename(columns={
            'asset_type': 'type',
            'fund_dividend_policy': 'dividend_policy'
        })
        
        df = df.sort_values(
            by=['market_cap', 'ongoing_charge_tercile'],
            ascending=[False, True]
        )
        
        total_etfs = len(df)
        filtered_df = df.copy()
        
        filter_col, data_col = st.columns([1, 3])

        with filter_col:
            if st.button('Clear Filters', key='clear_filters'):
                st.session_state.super_region_select = None
                st.session_state.region_group_select = None
                st.session_state.specific_region_select = None
                st.session_state.currency_select = None
                st.session_state.dividend_policy_select = None
                st.session_state.issuer_select = None
                st.session_state.equity_category = None
                st.rerun()

            # Type filter
            type_col = create_filter_row(1, "TYPE")
            with type_col:
                available_types = clean_options(df['type'].unique())
                selected_type = st.selectbox(
                    "",
                    options=available_types,
                    index=available_types.index('Equity') if 'Equity' in available_types else 0,
                    label_visibility="collapsed",
                    key="asset_type_select"
                )
            filtered_df = filtered_df[filtered_df['type'] == selected_type]

            # If Equity is selected, show Theme/Region selector
            if selected_type == 'Equity':
                category_col = create_filter_row(2, "CATEGORY")
                with category_col:
                    selected_category = st.selectbox(
                        "",
                        options=['Select Category...', 'Theme', 'Region'],
                        index=0,
                        label_visibility="collapsed",
                        key="equity_category"
                    )

                if selected_category == 'Theme':
                    # Theme selector
                    theme_col = create_filter_row(3, "THEME")
                    with theme_col:
                        available_themes = clean_options(filtered_df[filtered_df['region_group'].isna()]['fund_category'].unique())
                        selected_theme = st.selectbox(
                            "",
                            options=['Select Theme...'] + list(available_themes),
                            index=0,
                            label_visibility="collapsed",
                            key="theme_select"
                        )
                    if selected_theme and selected_theme != 'Select Theme...':
                        filtered_df = filtered_df[filtered_df['fund_category'] == selected_theme]

                elif selected_category == 'Region':
                    # Super Region filter
                    region_col = create_filter_row(3, "REGION")
                    with region_col:
                        available_super_regions = clean_options(filtered_df['super_region'].unique())
                        selected_super_region = st.selectbox(
                            "",
                            options=['Select Region...'] + available_super_regions,
                            index=0,
                            label_visibility="collapsed",
                            key="super_region_select"
                        )
                    
                    if selected_super_region and selected_super_region != 'Select Region...':
                        filtered_df = filtered_df[filtered_df['super_region'] == selected_super_region]
                        
                        # Region Group filter
                        region_group_col = create_filter_row(4, "REGION GROUP")
                        with region_group_col:
                            available_region_groups = clean_options(filtered_df['region_group'].unique())
                            selected_region_group = st.selectbox(
                                "",
                                options=['All Groups'] + available_region_groups,
                                index=0,
                                label_visibility="collapsed",
                                key="region_group_select"
                            )
                        
                        if selected_region_group and selected_region_group != 'All Groups':
                            filtered_df = filtered_df[filtered_df['region_group'] == selected_region_group]
                            
                            # Specific Region filter
                            specific_region_col = create_filter_row(5, "SPECIFIC REGION")
                            with specific_region_col:
                                available_specific_regions = clean_options(filtered_df['fund_category'].unique())
                                selected_specific_region = st.selectbox(
                                    "",
                                    options=['All Regions'] + available_specific_regions,
                                    index=0,
                                    label_visibility="collapsed",
                                    key="specific_region_select"
                                )
                            
                            if selected_specific_region and selected_specific_region != 'All Regions':
                                filtered_df = filtered_df[filtered_df['fund_category'] == selected_specific_region]

            # Continue with other filters (adjust numbers based on previous selections)
            next_filter_num = 6 if selected_type == 'Equity' and selected_category == 'Region' else 4

            # Currency filter
            currency_col = create_filter_row(next_filter_num, "CURRENCY")
            with currency_col:
                available_currencies = clean_options(filtered_df['currency'].unique())
                selected_currency = st.selectbox(
                    "",
                    options=['Select Currency...'] + available_currencies,
                    index=0,
                    label_visibility="collapsed",
                    key="currency_select"
                )
            if selected_currency and selected_currency != 'Select Currency...':
                filtered_df = filtered_df[filtered_df['currency'] == selected_currency]

            # Dividend Policy filter
            dividend_col = create_filter_row(next_filter_num + 1, "DIVIDEND POLICY")
            with dividend_col:
                available_dividend_policies = clean_options(filtered_df['dividend_policy'].unique())
                selected_dividend_policy = st.selectbox(
                    "",
                    options=['Select Policy...'] + available_dividend_policies,
                    index=0,
                    label_visibility="collapsed",
                    key="dividend_policy_select"
                )
            if selected_dividend_policy and selected_dividend_policy != 'Select Policy...':
                filtered_df = filtered_df[filtered_df['dividend_policy'] == selected_dividend_policy]

            # Fund Issuer filter
            issuer_col = create_filter_row(next_filter_num + 2, "FUND ISSUER")
            with issuer_col:
                available_issuers = clean_options(filtered_df['issuer'].unique())
                selected_issuer = st.selectbox(
                    "",
                    options=['Select Issuer...'] + available_issuers,
                    index=0,
                    label_visibility="collapsed",
                    key="issuer_select"
                )
            if selected_issuer and selected_issuer != 'Select Issuer...':
                filtered_df = filtered_df[filtered_df['issuer'] == selected_issuer]

            st.markdown(
                f"""
                <div class="etf-count">
                    Showing {len(filtered_df)} of {total_etfs} ETFs
                </div>
                """,
                unsafe_allow_html=True
            )

        with data_col:
            st.dataframe(
                filtered_df,
                hide_index=True,
                use_container_width=True,
                height=600,
                column_config={
                    "ticker": st.column_config.TextColumn("Ticker", width=100),
                    "currency": st.column_config.TextColumn("Currency", width=100),
                    "type": st.column_config.TextColumn("Type", width=120),
                    "super_region": st.column_config.TextColumn("Region", width=120),
                    "region_group": st.column_config.TextColumn("Region Group", width=150),
                    "fund_category": st.column_config.TextColumn("Category", width=150),
                    "dividend_policy": st.column_config.TextColumn("Dividend Policy", width=150),
                    "fund_benchmark": st.column_config.TextColumn("Benchmark", width=300),
                    "fund_domicile": st.column_config.TextColumn("Domicile", width=100),
                    "market_cap": st.column_config.NumberColumn("Market Cap", width=120),
                    "ongoing_charge_tercile": st.column_config.NumberColumn("Ongoing Charge Tercile", width=100),
                    "issuer": st.column_config.TextColumn("Fund Issuer", width=100)
                }
            )

    except Exception as e:
        st.error(f"Error loading CSV file: {e}")



if __name__ == "__main__":
    main()