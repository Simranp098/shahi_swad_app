import json
import os
from django.core.mail.backends.base import BaseEmailBackend

class ResendHTTPBackend(BaseEmailBackend):
    """
    HTTP Email Backend for Render Free Tier.
    Sends emails over HTTPS Port 443 via Resend API.
    Includes custom User-Agent header to bypass Cloudflare Error 1010.
    """
    def send_messages(self, email_messages):
        api_key = os.environ.get('RESEND_API_KEY', '').strip()
        if not api_key:
            print("❌ RESEND_API_KEY missing from environment variables!")
            return 0

        num_sent = 0
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ShahiSwadApp/1.0",  # Custom User-Agent prevents Cloudflare 1010 blocks
        }

        for msg in email_messages:
            recipients = list(msg.to)
            body_content = msg.body
            if not body_content.strip().startswith("<"):
                body_content = f"<p style='font-size:16px;'>{msg.body}</p>"

            payload = {
                "from": "onboarding@resend.dev",
                "to": recipients,
                "subject": msg.subject,
                "html": body_content,
            }

            try:
                import requests
                resp = requests.post(
                    "https://api.resend.com/emails",
                    headers=headers,
                    json=payload,
                    timeout=10
                )
                if resp.status_code in (200, 201):
                    num_sent += 1
                    print(f"✅ OTP Email dispatched successfully via Resend to {recipients}")
                else:
                    error_msg = f"Resend error {resp.status_code}: {resp.text}"
                    print(f"❌ {error_msg}")
                    if not self.fail_silently:
                        raise Exception(error_msg)
            except ImportError:
                import urllib.request
                import urllib.error

                req = urllib.request.Request(
                    "https://api.resend.com/emails",
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST"
                )
                try:
                    with urllib.request.urlopen(req) as resp:
                        if resp.status in (200, 201):
                            num_sent += 1
                            print(f"✅ OTP Email dispatched successfully via Resend to {recipients}")
                except urllib.error.HTTPError as e:
                    error_body = e.read().decode('utf-8')
                    error_msg = f"Resend error {e.code}: {error_body}"
                    print(f"❌ {error_msg}")
                    if not self.fail_silently:
                        raise Exception(error_msg)
                except Exception as e:
                    if not self.fail_silently:
                        raise e

        return num_sent