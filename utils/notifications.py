import streamlit as st
from datetime import datetime

class PopupNotificationSystem:
    def __init__(self):
        if "popup_notifications" not in st.session_state:
            st.session_state.popup_notifications = []
        if "show_popup" not in st.session_state:
            st.session_state.show_popup = False
        if "current_popup" not in st.session_state:
            st.session_state.current_popup = None
    
    def add_popup(self, title, message, type="info", duration=5):
        popup = {
            "id": len(st.session_state.popup_notifications) + 1,
            "title": title,
            "message": message,
            "type": type,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "duration": duration
        }
        st.session_state.popup_notifications.insert(0, popup)
        st.session_state.show_popup = True
        st.session_state.current_popup = popup
    
    def clear_current_popup(self):
        st.session_state.show_popup = False
        st.session_state.current_popup = None
    
    def get_current_popup(self):
        return st.session_state.current_popup

class NotificationSystem:
    def __init__(self):
        if "notifications" not in st.session_state:
            st.session_state.notifications = []
        if "unread_count" not in st.session_state:
            st.session_state.unread_count = 0
    
    def add_notification(self, message, type="info"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notification = {
            "id": len(st.session_state.notifications) + 1,
            "message": message,
            "type": type,
            "timestamp": timestamp,
            "read": False
        }
        st.session_state.notifications.insert(0, notification)
        st.session_state.unread_count += 1
    
    def mark_as_read(self, notification_id):
        for notification in st.session_state.notifications:
            if notification["id"] == notification_id and not notification["read"]:
                notification["read"] = True
                st.session_state.unread_count -= 1
                break
    
    def mark_all_as_read(self):
        for notification in st.session_state.notifications:
            if not notification["read"]:
                notification["read"] = True
        st.session_state.unread_count = 0
    
    def get_unread_count(self):
        return st.session_state.unread_count
    
    def get_notifications(self):
        return st.session_state.notifications