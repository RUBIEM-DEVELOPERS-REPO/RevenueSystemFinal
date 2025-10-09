import streamlit as st
from utils.notifications import NotificationSystem

def show_sidebar_controls():
    """Display sidebar controls and return settings"""
    notification_system = NotificationSystem()
    
    st.sidebar.header("🎛️ Analysis Controls")
    refresh_rate = st.sidebar.slider("Refresh rate (seconds)", 1, 30, 5)
    batch_size = st.sidebar.slider("Transactions per tick", 1, 20, 3)
    
    analysis_mode = st.sidebar.selectbox(
        "Analysis Mode",
        ["Real-time Monitoring", "Historical Pattern Analysis", "Anomaly Investigation"]
    )

    display_currency = st.sidebar.selectbox("Display Currency", ["USD", "ZiG"])
    exchange_rate = 13.5 if display_currency == "ZiG" else 1.0

    # Enhanced Intelligent Filters
    st.sidebar.header("🔍 Intelligent Filters")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        min_amount = st.number_input("Min Amount", value=0, step=10)
        max_amount = st.number_input("Max Amount", value=10000, step=100)
        
    with col2:
        anomaly_threshold = st.slider("Anomaly Threshold", 0.0, 1.0, 0.7)
        show_high_severity_only = st.checkbox("High Severity Only")

    # Report Download Section
    st.sidebar.header("📊 Reports")
    
    with st.sidebar.expander("Download Analysis Reports", expanded=False):
        st.write("Generate comprehensive reports in multiple formats:")
        
        if st.button("🎁 Show Download Options", use_container_width=True, type="primary", key="show_reports_btn"):
            st.session_state.show_reports = True
        
        st.info("""
        Available formats:
        • PDF - Professional summary
        • Excel - Detailed data sheets  
        • Word - Formatted document
        • CSV - Raw data files
        • JSON - Structured data
        """)
    
    # Safe category filter
    if not st.session_state.transaction_types.empty and "category_name" in st.session_state.transaction_types.columns:
        available_categories = ["All"] + sorted(st.session_state.transaction_types["category_name"].dropna().unique().tolist())
    else:
        available_categories = ["All"]
        st.sidebar.info("No transaction categories loaded. Using default categories.")
    
    focus_category = st.sidebar.selectbox("Focus Category", available_categories)
    
    # Safe currency filter
    if not st.session_state.all_transactions.empty and "currency" in st.session_state.all_transactions.columns:
        available_currencies = ["All"] + sorted(st.session_state.all_transactions["currency"].dropna().unique().tolist())
    else:
        available_currencies = ["All"]
    
    focus_currency = st.sidebar.selectbox("Focus Currency", available_currencies)
    
    risk_level = st.sidebar.multiselect(
        "Risk Level",
        ["Low", "Medium", "High", "Critical"],
        default=["Medium", "High", "Critical"]
    )

    # Notification Bell in Sidebar
    st.sidebar.header("🔔 Notifications")
    unread_count = notification_system.get_unread_count()
    
    if st.sidebar.button(f"🔔 Notifications ({unread_count})", use_container_width=True):
        with st.sidebar.expander("Recent Notifications", expanded=True):
            notifications = notification_system.get_notifications()
            if notifications:
                for notification in notifications[:10]:
                    status_color = "🔴" if notification["type"] == "error" else "🟡" if notification["type"] == "warning" else "🔵"
                    st.write(f"{status_color} **{notification['type'].upper()}**: {notification['message']}")
                    st.caption(f"_{notification['timestamp']}_")
                    if not notification["read"]:
                        if st.button("Mark as read", key=f"read_{notification['id']}"):
                            notification_system.mark_as_read(notification["id"])
                            st.rerun()
                if unread_count > 0:
                    if st.button("Mark all as read"):
                        notification_system.mark_all_as_read()
                        st.rerun()
            else:
                st.info("No notifications yet")
    
    return {
        'refresh_rate': refresh_rate,
        'batch_size': batch_size,
        'analysis_mode': analysis_mode,
        'display_currency': display_currency,
        'exchange_rate': exchange_rate,
        'min_amount': min_amount,
        'max_amount': max_amount,
        'anomaly_threshold': anomaly_threshold,
        'show_high_severity_only': show_high_severity_only,
        'focus_category': focus_category,
        'focus_currency': focus_currency,
        'risk_level': risk_level
    }

import streamlit as st
from utils.notifications import NotificationSystem

def show_sidebar_controls():
    """Display sidebar controls and return settings"""
    notification_system = NotificationSystem()
    
    st.sidebar.header("🎛️ Analysis Controls")
    refresh_rate = st.sidebar.slider("Refresh rate (seconds)", 1, 30, 5)
    batch_size = st.sidebar.slider("Transactions per tick", 1, 20, 3)
    
    analysis_mode = st.sidebar.selectbox(
        "Analysis Mode",
        ["Real-time Monitoring", "Historical Pattern Analysis", "Anomaly Investigation"]
    )

    display_currency = st.sidebar.selectbox("Display Currency", ["USD", "ZiG"])
    exchange_rate = 13.5 if display_currency == "ZiG" else 1.0

    # Enhanced Intelligent Filters
    st.sidebar.header("🔍 Intelligent Filters")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        min_amount = st.number_input("Min Amount", value=0, step=10)
        max_amount = st.number_input("Max Amount", value=10000, step=100)
        
    with col2:
        anomaly_threshold = st.slider("Anomaly Threshold", 0.0, 1.0, 0.7)
        show_high_severity_only = st.checkbox("High Severity Only")

    # Report Download Section
    st.sidebar.header("📊 Reports")
    
    with st.sidebar.expander("Download Analysis Reports", expanded=False):
        st.write("Generate comprehensive reports in multiple formats:")
        
        if st.button("🎁 Show Download Options", use_container_width=True, type="primary", key="show_reports_btn"):
            st.session_state.show_reports = True
        
        st.info("""
        Available formats:
        • PDF - Professional summary
        • Excel - Detailed data sheets  
        • Word - Formatted document
        • CSV - Raw data files
        • JSON - Structured data
        """)
    
    # Safe category filter
    if not st.session_state.transaction_types.empty and "category_name" in st.session_state.transaction_types.columns:
        available_categories = ["All"] + sorted(st.session_state.transaction_types["category_name"].dropna().unique().tolist())
    else:
        available_categories = ["All"]
        st.sidebar.info("No transaction categories loaded. Using default categories.")
    
    focus_category = st.sidebar.selectbox("Focus Category", available_categories)
    
    # Safe currency filter
    if not st.session_state.all_transactions.empty and "currency" in st.session_state.all_transactions.columns:
        available_currencies = ["All"] + sorted(st.session_state.all_transactions["currency"].dropna().unique().tolist())
    else:
        available_currencies = ["All"]
    
    focus_currency = st.sidebar.selectbox("Focus Currency", available_currencies)
    
    risk_level = st.sidebar.multiselect(
        "Risk Level",
        ["Low", "Medium", "High", "Critical"],
        default=["Medium", "High", "Critical"]
    )

    # Notification Bell in Sidebar
    st.sidebar.header("🔔 Notifications")
    unread_count = notification_system.get_unread_count()
    
    if st.sidebar.button(f"🔔 Notifications ({unread_count})", use_container_width=True):
        with st.sidebar.expander("Recent Notifications", expanded=True):
            notifications = notification_system.get_notifications()
            if notifications:
                for notification in notifications[:10]:
                    status_color = "🔴" if notification["type"] == "error" else "🟡" if notification["type"] == "warning" else "🔵"
                    st.write(f"{status_color} **{notification['type'].upper()}**: {notification['message']}")
                    st.caption(f"_{notification['timestamp']}_")
                    if not notification["read"]:
                        if st.button("Mark as read", key=f"read_{notification['id']}"):
                            notification_system.mark_as_read(notification["id"])
                            st.rerun()
                if unread_count > 0:
                    if st.button("Mark all as read"):
                        notification_system.mark_all_as_read()
                        st.rerun()
            else:
                st.info("No notifications yet")
    
    return {
        'refresh_rate': refresh_rate,
        'batch_size': batch_size,
        'analysis_mode': analysis_mode,
        'display_currency': display_currency,
        'exchange_rate': exchange_rate,
        'min_amount': min_amount,
        'max_amount': max_amount,
        'anomaly_threshold': anomaly_threshold,
        'show_high_severity_only': show_high_severity_only,
        'focus_category': focus_category,
        'focus_currency': focus_currency,
        'risk_level': risk_level
    }