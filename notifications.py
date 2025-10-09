import streamlit as st
import datetime

notifications = []

def generate_notification(message, category="info"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    notifications.append({"time": timestamp, "msg": message, "category": category})

def show_notifications():
    if notifications:
        for note in notifications[-5:]:  # show last 5
            st.info(f"🛎 {note['time']} — {note['msg']} ({note['category']})")
    else:
        st.write("No notifications yet.")
