import streamlit as st
import pandas as pd
import io

# Set page config
st.set_page_config(
    page_title="Text Classification Tool",
    page_icon="📊",
    layout="wide"
)

# Initialize session state for dictionaries if not exists
if 'dictionaries' not in st.session_state:
    st.session_state.dictionaries = {
        'urgency_marketing': {
            'limited', 'limited time', 'limited run', 'limited edition', 'order now',
            'last chance', 'hurry', 'while supplies last', 'before they\'re gone',
            'selling out', 'selling fast', 'act now', 'don\'t wait', 'today only',
            'expires soon', 'final hours', 'almost gone'
        },
        'exclusive_marketing': {
            'exclusive', 'exclusively', 'exclusive offer', 'exclusive deal',
            'members only', 'vip', 'special access', 'invitation only',
            'premium', 'privileged', 'limited access', 'select customers',
            'insider', 'private sale', 'early access'
        }
    }

# Title and description
st.title("📊 Text Classification Tool")
st.markdown("""
This app classifies text based on customizable dictionaries. 
Upload your CSV file and modify the dictionaries to suit your needs.
""")

# Sidebar for dictionary management
st.sidebar.header("📚 Dictionary Management")

# Add new dictionary
with st.sidebar.expander("➕ Add New Dictionary", expanded=False):
    new_dict_name = st.text_input("Dictionary Name", key="new_dict_name")
    new_dict_terms = st.text_area(
        "Terms (one per line)", 
        key="new_dict_terms",
        height=100
    )
    if st.button("Add Dictionary"):
        if new_dict_name and new_dict_terms:
            terms = set(term.strip() for term in new_dict_terms.split('\n') if term.strip())
            st.session_state.dictionaries[new_dict_name] = terms
            st.success(f"Dictionary '{new_dict_name}' added!")
            st.rerun()
        else:
            st.error("Please provide both name and terms.")

# Edit existing dictionaries
st.sidebar.subheader("✏️ Edit Dictionaries")
dict_to_edit = st.sidebar.selectbox(
    "Select dictionary to edit",
    options=list(st.session_state.dictionaries.keys())
)

if dict_to_edit:
    current_terms = '\n'.join(sorted(st.session_state.dictionaries[dict_to_edit]))
    edited_terms = st.sidebar.text_area(
        f"Edit '{dict_to_edit}' terms",
        value=current_terms,
        height=200,
        key=f"edit_{dict_to_edit}"
    )
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("💾 Save Changes"):
            terms = set(term.strip() for term in edited_terms.split('\n') if term.strip())
            st.session_state.dictionaries[dict_to_edit] = terms
            st.success("Changes saved!")
            st.rerun()
    
    with col2:
        if st.button("🗑️ Delete Dictionary"):
            if len(st.session_state.dictionaries) > 1:
                del st.session_state.dictionaries[dict_to_edit]
                st.success(f"Dictionary '{dict_to_edit}' deleted!")
                st.rerun()
            else:
                st.error("Cannot delete the last dictionary!")

# Reset to defaults
if st.sidebar.button("🔄 Reset to Defaults"):
    st.session_state.dictionaries = {
        'urgency_marketing': {
            'limited', 'limited time', 'limited run', 'limited edition', 'order now',
            'last chance', 'hurry', 'while supplies last', 'before they\'re gone',
            'selling out', 'selling fast', 'act now', 'don\'t wait', 'today only',
            'expires soon', 'final hours', 'almost gone'
        },
        'exclusive_marketing': {
            'exclusive', 'exclusively', 'exclusive offer', 'exclusive deal',
            'members only', 'vip', 'special access', 'invitation only',
            'premium', 'privileged', 'limited access', 'select customers',
            'insider', 'private sale', 'early access'
        }
    }
    st.success("Dictionaries reset to defaults!")
    st.rerun()

# Main content area
st.header("📁 Upload Your Data")

# File uploader
uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=['csv'],
    help="Upload a CSV file containing a 'Statement' column to classify"
)

# Text column selector
text_column = st.text_input(
    "Text Column Name",
    value="Statement",
    help="Name of the column containing text to classify"
)

if uploaded_file is not None:
    try:
        # Load data
        df = pd.read_csv(uploaded_file)
        
        st.success(f"✅ File uploaded successfully! ({len(df)} rows)")
        
        # Check if text column exists
        if text_column not in df.columns:
            st.error(f"❌ Column '{text_column}' not found in the CSV. Available columns: {', '.join(df.columns)}")
        else:
            # Show preview
            with st.expander("📋 Data Preview", expanded=True):
                st.dataframe(df.head(10), use_container_width=True)
            
            # Classification function
            def classify_text(text, dictionary):
                if pd.isna(text):
                    return 0
                text_lower = text.lower()
                return int(any(term in text_lower for term in dictionary))
            
            # Classify button
            if st.button("🚀 Classify Text", type="primary"):
                with st.spinner("Classifying..."):
                    # Apply classification for each dictionary
                    for dict_name, dict_terms in st.session_state.dictionaries.items():
                        df[dict_name] = df[text_column].apply(
                            lambda x: classify_text(x, dict_terms)
                        )
                    
                    # Store results in session state
                    st.session_state.classified_df = df
                
                st.success("✅ Classification complete!")
            
            # Display results if classification has been done
            if 'classified_df' in st.session_state:
                st.header("📊 Results")
                
                # Show statistics
                dict_cols = list(st.session_state.dictionaries.keys())
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Rows", len(st.session_state.classified_df))
                with col2:
                    total_classified = (st.session_state.classified_df[dict_cols].sum(axis=1) > 0).sum()
                    st.metric("Rows with Matches", total_classified)
                with col3:
                    match_rate = (total_classified / len(st.session_state.classified_df) * 100)
                    st.metric("Match Rate", f"{match_rate:.1f}%")
                
                # Show breakdown by dictionary
                st.subheader("📈 Classification Breakdown")
                breakdown_data = []
                for dict_name in dict_cols:
                    count = st.session_state.classified_df[dict_name].sum()
                    percentage = (count / len(st.session_state.classified_df) * 100)
                    breakdown_data.append({
                        'Dictionary': dict_name,
                        'Matches': int(count),
                        'Percentage': f"{percentage:.1f}%"
                    })
                
                breakdown_df = pd.DataFrame(breakdown_data)
                st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
                
                # Show classified data
                with st.expander("📋 View Classified Data", expanded=True):
                    # Filter options
                    filter_option = st.selectbox(
                        "Filter results",
                        ["Show All", "Show Only Matches", "Show No Matches"]
                    )
                    
                    display_df = st.session_state.classified_df.copy()
                    
                    if filter_option == "Show Only Matches":
                        display_df = display_df[display_df[dict_cols].sum(axis=1) > 0]
                    elif filter_option == "Show No Matches":
                        display_df = display_df[display_df[dict_cols].sum(axis=1) == 0]
                    
                    st.dataframe(display_df, use_container_width=True)
                    st.caption(f"Showing {len(display_df)} of {len(st.session_state.classified_df)} rows")
                
                # Download button
                st.header("💾 Download Results")
                
                # Convert to CSV
                csv_buffer = io.StringIO()
                st.session_state.classified_df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="📥 Download Classified Data (CSV)",
                    data=csv_data,
                    file_name="classified_data.csv",
                    mime="text/csv",
                    type="primary"
                )
    
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.info("Please make sure your CSV is properly formatted.")

else:
    # Show instructions when no file is uploaded
    st.info("""
    👆 **Get started:**
    1. Upload a CSV file containing text data
    2. Specify the column name with text to classify
    3. Customize dictionaries in the sidebar (optional)
    4. Click 'Classify Text' to process your data
    5. Download the results
    """)
    
    # Show current dictionaries
    st.subheader("📚 Current Dictionaries")
    for dict_name, terms in st.session_state.dictionaries.items():
        with st.expander(f"**{dict_name}** ({len(terms)} terms)"):
            st.write(", ".join(sorted(terms)))