import streamlit as st
import pandas as pd
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

# Set page config for a wider layout
st.set_page_config(layout="wide", page_title="ETF Screener", initial_sidebar_state="collapsed")

# Custom CSS for styling
st.markdown("""
    <style>
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
        st.session_state.type_select = 'Equity'
        st.session_state.category_select = None
        st.session_state.super_region_select = None
        st.session_state.region_group_select = None
        st.session_state.specific_region_select = None
        st.session_state.currency_select = None
        st.session_state.dividend_policy_select = None
        st.session_state.issuer_select = None
        st.session_state.subcategory_select = None

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
            if st.button('Clear Filters'):
                st.session_state.type_select = 'Equity'
                st.session_state.category_select = None
                st.session_state.super_region_select = None
                st.session_state.region_group_select = None
                st.session_state.specific_region_select = None
                st.session_state.currency_select = None
                st.session_state.dividend_policy_select = None
                st.session_state.issuer_select = None
                st.session_state.subcategory_select = None
                st.rerun()

            # Asset Type
            type_col = create_filter_row(1, "TYPE")
            with type_col:
                available_types = clean_options(df['type'].unique())
                selected_type = st.selectbox(
                    "",
                    options=available_types,
                    index=available_types.index(st.session_state.type_select) if st.session_state.type_select in available_types else 0,
                    label_visibility="collapsed",
                )
                if selected_type != st.session_state.type_select:
                    st.session_state.type_select = selected_type
                    st.session_state.category_select = None
                    st.session_state.super_region_select = None
                    st.session_state.region_group_select = None
                    st.session_state.specific_region_select = None
                    st.session_state.subcategory_select = None
                    
            filtered_df = filtered_df[filtered_df['type'] == selected_type]


            # Category Filter
            category_col = create_filter_row(2, "CATEGORY")
            with category_col:
                available_categories = ['Select Category...'] + clean_options(filtered_df['category_type'].unique())
                selected_category = st.selectbox(
                   label="",
                   options=available_categories,
                   index=available_categories.index(st.session_state.category_select) if st.session_state.category_select in available_categories else 0,
                   label_visibility="collapsed",
                )
                if selected_category != st.session_state.category_select:
                     st.session_state.category_select = selected_category
                     st.session_state.super_region_select = None
                     st.session_state.region_group_select = None
                     st.session_state.specific_region_select = None
                     st.session_state.subcategory_select = None
                     
            if selected_category != 'Select Category...':
                 filtered_df = filtered_df[filtered_df['category_type'] == selected_category]

                 if selected_category == 'Sector':
                    filtered_df = apply_sub_category_filter(filtered_df, 'SECTOR', 3)
                 elif selected_category == 'Theme':
                    filtered_df = apply_sub_category_filter(filtered_df, 'THEME', 3)
                 elif selected_category == 'Region':
                     filtered_df = apply_region_filters(filtered_df)
            


            # Currency Filter
            currency_col = create_filter_row(6, "CURRENCY")
            with currency_col:
                available_currencies = clean_options(filtered_df['currency'].unique())
                selected_currency = st.selectbox(
                    "",
                    options=available_currencies,
                    index=available_currencies.index(st.session_state.currency_select) if st.session_state.currency_select in available_currencies else None,
                    label_visibility="collapsed",
                )
                if selected_currency != st.session_state.currency_select:
                     st.session_state.currency_select = selected_currency
            if selected_currency:
                filtered_df = filtered_df[filtered_df['currency'] == selected_currency]

            # Dividend Policy Filter
            dividend_col = create_filter_row(7, "DIVIDEND POLICY")
            with dividend_col:
                available_dividend_policies = clean_options(filtered_df['dividend_policy'].unique())
                selected_dividend_policy = st.selectbox(
                    "",
                    options=available_dividend_policies,
                    index=available_dividend_policies.index(st.session_state.dividend_policy_select) if st.session_state.dividend_policy_select in available_dividend_policies else None,
                    label_visibility="collapsed",
                )
                if selected_dividend_policy != st.session_state.dividend_policy_select:
                     st.session_state.dividend_policy_select = selected_dividend_policy
            if selected_dividend_policy:
                filtered_df = filtered_df[filtered_df['dividend_policy'] == selected_dividend_policy]

            # Fund Issuer Filter
            issuer_col = create_filter_row(8, "FUND ISSUER")
            with issuer_col:
                available_issuers = clean_options(filtered_df['issuer'].unique())
                selected_issuer = st.selectbox(
                    "",
                    options=available_issuers,
                    index=available_issuers.index(st.session_state.issuer_select) if st.session_state.issuer_select in available_issuers else None,
                    label_visibility="collapsed",
                )
                if selected_issuer != st.session_state.issuer_select:
                     st.session_state.issuer_select = selected_issuer
            if selected_issuer:
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

def apply_sub_category_filter(filtered_df, label, number):
    sub_category_col = create_filter_row(number, label)
    with sub_category_col:
        available_sub_categories = clean_options(
            filtered_df['category_subdetail'].unique()
        )
        selected_sub_category = st.selectbox(
            "",
            options= available_sub_categories,
            index=available_sub_categories.index(st.session_state.subcategory_select) if st.session_state.subcategory_select in available_sub_categories else None,
            label_visibility="collapsed",
        )
        if selected_sub_category != st.session_state.subcategory_select:
             st.session_state.subcategory_select = selected_sub_category

    if selected_sub_category:
         filtered_df = filtered_df[filtered_df['category_subdetail'] == selected_sub_category]
    return filtered_df

def apply_region_filters(filtered_df):
    """Apply progressive region filtering."""
    region_col = create_filter_row(3, "REGION")
    with region_col:
        available_super_regions = clean_options(filtered_df['super_region'].unique())
        selected_super_region = st.selectbox(
            "",
            options=available_super_regions,
            index=available_super_regions.index(st.session_state.super_region_select) if st.session_state.super_region_select in available_super_regions else None,
            label_visibility="collapsed",
        )
        if selected_super_region != st.session_state.super_region_select:
             st.session_state.super_region_select = selected_super_region
             st.session_state.region_group_select = None
             st.session_state.specific_region_select = None

    if selected_super_region:
        filtered_df = filtered_df[filtered_df['super_region'] == selected_super_region]

        region_group_col = create_filter_row(4, "REGION GROUP")
        with region_group_col:
            available_region_groups = clean_options(filtered_df['region_group'].unique())
            selected_region_group = st.selectbox(
                "",
                options=available_region_groups,
                index=available_region_groups.index(st.session_state.region_group_select) if st.session_state.region_group_select in available_region_groups else None,
                label_visibility="collapsed",
            )
            if selected_region_group != st.session_state.region_group_select:
                 st.session_state.region_group_select = selected_region_group
                 st.session_state.specific_region_select = None

        if selected_region_group:
            filtered_df = filtered_df[filtered_df['region_group'] == selected_region_group]

            specific_region_col = create_filter_row(5, "SPECIFIC REGION")
            with specific_region_col:
                available_specific_regions = clean_options(filtered_df['category_subdetail'].unique())
                selected_specific_region = st.selectbox(
                    "",
                    options=available_specific_regions,
                    index=available_specific_regions.index(st.session_state.specific_region_select) if st.session_state.specific_region_select in available_specific_regions else None,
                    label_visibility="collapsed",
                )
                if selected_specific_region != st.session_state.specific_region_select:
                     st.session_state.specific_region_select = selected_specific_region

            if selected_specific_region:
                filtered_df = filtered_df[filtered_df['category_subdetail'] == selected_specific_region]

    return filtered_df



if __name__ == "__main__":
    main()
