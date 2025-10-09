import streamlit as st
import pandas as pd

def show_categorization_tab(unmapped_df, categories_df, subcategories_df, client):
    st.subheader("🚨 Unmapped Transactions")
    
    if unmapped_df.empty:
        st.success("All transactions are mapped! ✅")
        return
    
    st.warning(f"{len(unmapped_df)} transactions need mapping")
    
    # Apply AI categorization
    with st.spinner("Generating AI category suggestions..."):
        unmapped_df[["suggested_category", "suggested_subcategory"]] = unmapped_df[
            "transaction_type_name"
        ].apply(lambda x: pd.Series(suggest_category_ai(x, client)))
    
    # Display unmapped transactions
    st.dataframe(unmapped_df[["id", "transaction_type_name", "suggested_category", "suggested_subcategory"]])
    
    # Manual mapping form
    show_mapping_form(unmapped_df, categories_df, subcategories_df)

def show_mapping_form(unmapped_df, categories_df, subcategories_df):
    with st.form("mapping_form"):
        st.subheader("📝 Manual Mapping Override")
        
        selected_id = st.selectbox("Pick a transaction to map", unmapped_df["id"])
        selected_cat = st.selectbox("Category", categories_df["category_name"].unique())

        # Get category_id and corresponding subcategories
        cat_id = categories_df[categories_df["category_name"] == selected_cat]["category_id"].iloc[0]
        sub_options = subcategories_df[subcategories_df["category_id"] == cat_id]
        selected_sub = st.selectbox("Subcategory", sub_options["subcategory_name"].unique())

        if st.form_submit_button("✅ Approve Mapping"):
            sub_id = sub_options[sub_options["subcategory_name"] == selected_sub]["subcategory_id"].iloc[0]
            
            # Update mapping in database
            success = update_transaction_mapping(selected_id, cat_id, sub_id)
            
            if success:
                st.success(f"Transaction {selected_id} mapped to {selected_cat} → {selected_sub}")
                st.rerun()
            else:
                st.error("Failed to update mapping. Please check database connection.")

     
import pandas as pd
from utils.ai_categorization import suggest_category_ai
from utils.database import update_transaction_mapping

def show_categorization_tab(unmapped_df, categories_df, subcategories_df, client):
    """Display the categorization tab with AI suggestions"""
    
    st.subheader("🚨 Unmapped Transactions")
    
    if unmapped_df.empty:
        st.success("All transactions are mapped! ✅")
        return
    
    st.warning(f"{len(unmapped_df)} transactions need mapping")
    
    # Apply AI categorization
    with st.spinner("Generating AI category suggestions..."):
        unmapped_df[["suggested_category", "suggested_subcategory"]] = unmapped_df[
            "transaction_type_name"
        ].apply(lambda x: pd.Series(suggest_category_ai(x, client)))
    
    # Display unmapped transactions with AI suggestions
    st.dataframe(unmapped_df[["id", "transaction_type_name", "suggested_category", "suggested_subcategory"]])
    
    # Manual mapping form
    show_mapping_form(unmapped_df, categories_df, subcategories_df)

def show_mapping_form(unmapped_df, categories_df, subcategories_df):
    """Display manual mapping override form"""
    
    with st.form("mapping_form"):
        st.subheader("📝 Manual Mapping Override")
        
        selected_id = st.selectbox("Pick a transaction to map", unmapped_df["id"])
        selected_cat = st.selectbox("Category", categories_df["category_name"].unique())

        # Get category_id and corresponding subcategories
        cat_id = categories_df[categories_df["category_name"] == selected_cat]["category_id"].iloc[0]
        sub_options = subcategories_df[subcategories_df["category_id"] == cat_id]
        selected_sub = st.selectbox("Subcategory", sub_options["subcategory_name"].unique())

        if st.form_submit_button("✅ Approve Mapping"):
            sub_id = sub_options[sub_options["subcategory_name"] == selected_sub]["subcategory_id"].iloc[0]
            
            # Update mapping in database
            success = update_transaction_mapping(selected_id, cat_id, sub_id)
            
            if success:
                st.success(f"Transaction {selected_id} mapped to {selected_cat} → {selected_sub}")
                st.rerun()
            else:
                st.error("Failed to update mapping. Please check database connection.")