import json
import os
import urllib.request
import urllib.error
from django.core.mail.backends.base import BaseEmailBackend

class ResendHTTPBackend(BaseEmailBackend):
    """
    Brevo HTTP Email Backend for Render Free Tier.
    Sends OTP emails over HTTPS Port 443 to ANY registered user email address.
    """
    def send_messages(self, email_messages):
        api_key = os.environ.get('BREVO_API_KEY', '').strip()
        if not api_key:
            print("❌ BREVO_API_KEY missing from environment variables!")
            return 0

        num_sent = 0
        for msg in email_messages:
            url = "https://api.brevo.com/v3/smtp/email"
            recipients = [{"email": recipient} for recipient in msg.to]
            
            body_content = msg.body
            if not body_content.strip().startswith("<"):
                body_content = f"<p style='font-size:16px;'>{msg.body}</p>"

            payload = json.dumps({
                "sender": {"name": "Hotel Shahi Swad", "email": "hotel.shahi.swad@gmail.com"},
                "to": recipients,
                "subject": msg.subject,
                "htmlContent": body_content,
            }).encode("utf-8")

            req = urllib.request.Request(
                url,
                data=payload,
                headers={
                    "api-key": api_key,
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                method="POST"
            )
            try:
                with urllib.request.urlopen(req) as resp:
                    if resp.status in (200, 201):
                        num_sent += 1
                        print(f"✅ OTP Email sent via Brevo to {recipients}")
            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8')
                print(f"❌ Brevo Error {e.code}: {error_body}")
                if not self.fail_silently:
                    raise Exception(f"Brevo error {e.code}: {error_body}")
            except Exception as e:
                print(f"❌ Brevo dispatch error: {e}")
                if not self.fail_silently:
                    raise e

        return num_sent