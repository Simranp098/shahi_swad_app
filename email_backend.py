import json
import os
import urllib.request
from django.core.mail.backends.base import BaseEmailBackend

class ResendHTTPBackend(BaseEmailBackend):
    """
    Sends emails over HTTPS Port 443 via Resend API to bypass 
    Render's outbound SMTP port blocks.
    """
    def send_messages(self, email_messages):
        api_key = os.environ.get('RESEND_API_KEY', '')
        if not api_key:
            print("⚠️ RESEND_API_KEY is missing from environment variables!")
            return 0

        num_sent = 0
        for msg in email_messages:
            url = "https://api.resend.com/emails"
            
            body_content = msg.body
            if not body_content.strip().startswith("<"):
                body_content = f"<p style='font-size:16px;'>{msg.body}</p>"

            payload = json.dumps({
                "from": "Hotel Shahi Swad <onboarding@resend.dev>",
                "to": list(msg.to),
                "subject": msg.subject,
                "html": body_content,
            }).encode("utf-8")

            req = urllib.request.Request(
                url,
                data=payload,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0",
                },
                method="POST"
            )
            try:
                with urllib.request.urlopen(req) as resp:
                    if resp.status in (200, 201):
                        num_sent += 1
            except Exception as e:
                print(f"❌ Resend API dispatch error: {e}")

        return num_sent