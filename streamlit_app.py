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
        # Initialize session state for filters
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
        # Load and preprocess the DataFrame
        df = pd.read_csv('sample_df.csv')
        df = df.rename(columns={
            'asset_type': 'type',
            'fund_dividend_policy': 'dividend_policy'
        })
        df = df.sort_values(by=['market_cap', 'ongoing_charge_tercile'], ascending=[False, True])
        
        total_etfs = len(df)
        filtered_df = df.copy()

        filter_col, data_col = st.columns([1, 3])  # Layout for filters and table

        with filter_col:
            # Clear Filters Button
            if st.button('Clear Filters', key='clear_filters'):
                st.session_state.super_region_select = None
                st.session_state.region_group_select = None
                st.session_state.specific_region_select = None
                st.session_state.currency_select = None
                st.session_state.dividend_policy_select = None
                st.session_state.issuer_select = None
                st.session_state.equity_category = None
                st.experimental_rerun()

            # Asset Type (Preselect Equity)
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

            # Progressive Filters for Equity Type
            if selected_type == 'Equity':
                category_col = create_filter_row(2, "CATEGORY")
                with category_col:
                    selected_category = st.selectbox(
                        "",
                        options=['Select Category...', 'Theme', 'Region', 'Sector'],
                        index=0,
                        label_visibility="collapsed",
                        key="equity_category"
                    )

                if selected_category == 'Sector':
                    # Filter for Sector
                    sector_col = create_filter_row(3, "SECTOR")
                    with sector_col:
                        available_sectors = clean_options(
                            filtered_df[filtered_df['category_type'] == 'Sector']['category_subdetail'].unique()
                        )
                        selected_sector = st.selectbox(
                            "",
                            options=['Select Sector...'] + available_sectors,
                            index=0,
                            label_visibility="collapsed",
                            key="sector_select"
                        )
                    if selected_sector and selected_sector != 'Select Sector...':
                        filtered_df = filtered_df[filtered_df['category_subdetail'] == selected_sector]

                elif selected_category == 'Theme':
                    # Filter for Theme
                    theme_col = create_filter_row(3, "THEME")
                    with theme_col:
                        available_themes = clean_options(
                            filtered_df[filtered_df['category_type'] == 'Theme']['category_subdetail'].unique()
                        )
                        selected_theme = st.selectbox(
                            "",
                            options=['Select Theme...'] + available_themes,
                            index=0,
                            label_visibility="collapsed",
                            key="theme_select"
                        )
                    if selected_theme and selected_theme != 'Select Theme...':
                        filtered_df = filtered_df[filtered_df['category_subdetail'] == selected_theme]

                elif selected_category == 'Region':
                    # Progressive Filters for Regions
                    filtered_df = apply_region_filters(filtered_df)

            # Currency Filter
            currency_col = create_filter_row(6, "CURRENCY")
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

            # Dividend Policy Filter
            dividend_col = create_filter_row(7, "DIVIDEND POLICY")
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

            # Fund Issuer Filter
            issuer_col = create_filter_row(8, "FUND ISSUER")
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
            # Display the filtered DataFrame
            st.dataframe(
                filtered_df,
                hide_index=True,
                use_container_width=True,
                height=600
            )

    except Exception as e:
        st.error(f"Error loading data: {e}")


def apply_region_filters(filtered_df):
    """Apply progressive region filtering."""
    # Ensure only regions are considered
    filtered_df = filtered_df[filtered_df['category_type'] == 'Region']

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

        region_group_col = create_filter_row(4, "REGION GROUP")
        with region_group_col:
            available_region_groups = clean_options(filtered_df['region_group'].unique())
            selected_region_group = st.selectbox(
                "",
                options=['Select Region Group...'] + available_region_groups,
                index=0,
                label_visibility="collapsed",
                key="region_group_select"
            )
        if selected_region_group and selected_region_group != 'Select Region Group...':
            filtered_df = filtered_df[filtered_df['region_group'] == selected_region_group]

            specific_region_col = create_filter_row(5, "SPECIFIC REGION")
            with specific_region_col:
                available_specific_regions = clean_options(filtered_df['category_subdetail'].unique())
                selected_specific_region = st.selectbox(
                    "",
                    options=['Select Specific Region...'] + available_specific_regions,
                    index=0,
                    label_visibility="collapsed",
                    key="specific_region_select"
                )
            if selected_specific_region and selected_specific_region != 'Select Specific Region...':
                filtered_df = filtered_df[filtered_df['category_subdetail'] == selected_specific_region]

    return filtered_df



if __name__ == "__main__":
    main()