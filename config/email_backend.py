import json
import os
import urllib.request
import urllib.error
from django.core.mail.backends.base import BaseEmailBackend

class ResendHTTPBackend(BaseEmailBackend):
    """
    HTTP Email Backend for Render Free Tier.
    Sends emails over HTTPS Port 443 via Resend API to bypass Render outbound SMTP blocks.
    """
    def send_messages(self, email_messages):
        api_key = os.environ.get('RESEND_API_KEY', '').strip()
        if not api_key:
            print("❌ RESEND_API_KEY missing from environment variables!")
            return 0

        num_sent = 0
        for msg in email_messages:
            url = "https://api.resend.com/emails"
            recipients = list(msg.to)
            
            body_content = msg.body
            if not body_content.strip().startswith("<"):
                body_content = f"<p style='font-size:16px;'>{msg.body}</p>"

            payload = json.dumps({
                "from": "onboarding@resend.dev",
                "to": recipients,
                "subject": msg.subject,
                "html": body_content,
            }).encode("utf-8")

            req = urllib.request.Request(
                url,
                data=payload,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                method="POST"
            )
            try:
                with urllib.request.urlopen(req) as resp:
                    if resp.status in (200, 201):
                        num_sent += 1
                        print(f"✅ OTP Email dispatched successfully via Resend to {recipients}")
            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8')
                print(f"❌ Resend HTTPError {e.code}: {error_body}")
                raise Exception(f"Resend error {e.code}: {error_body}")
            except Exception as e:
                print(f"❌ Resend dispatch error: {e}")
                raise e

        return num_sent