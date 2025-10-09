import smtplib
from email.mime.text import MIMEText
import requests

class AlertSystem:
    """System for sending alerts via various channels"""
    
    def __init__(self):
        self.slack_webhook = "https://hooks.slack.com/services/XXXX/XXXX/XXXX"  # Replace with actual webhook
        self.email_config = {
            "sender": "patiencemupikeni@outlook.com",
            "receiver": "patiencemupikeni@gmail.com",
            "password": "Dube1999"  # ⚠️ Use environment variables in production
        }
    
    def send_slack_alert(self, message):
        """Send alert to Slack"""
        try:
            payload = {"text": message}
            response = requests.post(self.slack_webhook, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Slack alert failed: {e}")
            return False
    
    def send_email_alert(self, subject, body):
        """Send alert via email"""
        try:
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = self.email_config["sender"]
            msg["To"] = self.email_config["receiver"]

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.email_config["sender"], self.email_config["password"])
                server.sendmail(self.email_config["sender"], self.email_config["receiver"], msg.as_string())
            return True
        except Exception as e:
            print(f"Email alert failed: {e}")
            return False
    
    def send_multiple_alerts(self, message, subject=None):
        """Send alerts through all available channels"""
        results = {
            'slack': self.send_slack_alert(message),
            'email': False
        }
        
        if subject:
            results['email'] = self.send_email_alert(subject, message)
        
        return results

    import smtplib
import requests
from email.mime.text import MIMEText

class AlertSystem:
    """System for sending alerts via various channels"""
    
    def __init__(self):
        self.slack_webhook = "https://hooks.slack.com/services/XXXX/XXXX/XXXX"  # Replace with actual webhook
        self.email_config = {
            "sender": "patiencemupikeni@outlook.com",
            "receiver": "patiencemupikeni@gmail.com",
            "password": "Dube1999"  # ⚠️ Use environment variables in production
        }
    
    def send_slack_alert(self, message):
        """Send alert to Slack"""
        try:
            payload = {"text": message}
            response = requests.post(self.slack_webhook, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Slack alert failed: {e}")
            return False
    
    def send_email_alert(self, subject, body):
        """Send alert via email"""
        try:
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = self.email_config["sender"]
            msg["To"] = self.email_config["receiver"]

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.email_config["sender"], self.email_config["password"])
                server.sendmail(self.email_config["sender"], self.email_config["receiver"], msg.as_string())
            return True
        except Exception as e:
            print(f"Email alert failed: {e}")
            return False
    
    def send_multiple_alerts(self, message, subject=None):
        """Send alerts through all available channels"""
        results = {
            'slack': self.send_slack_alert(message),
            'email': False
        }
        
        if subject:
            results['email'] = self.send_email_alert(subject, message)
        
        return results