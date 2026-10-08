from dataclasses import dataclass
from email.message import EmailMessage
import aiosmtplib
import httpx
from app.modules.auth.application.dto.outbox_dto import Payload
from app.shared.application.email.email_sender import EmailSender
from app.core.config import settings

@dataclass
class SMTPEmailSender(EmailSender):
    host: str
    port: int
    username: str
    password: str
    sender_email: str

    def _build_email_content(self, payload: Payload) -> tuple[str, str, str]:
        sender_addr = self.sender_email or self.username
        if payload.reset_url:
            subject = "Reset your Gradify password"
            plain_text = f"Reset your password: {payload.reset_url}"
            html_content = f"<p>Reset your password: <a href='{payload.reset_url}'>{payload.reset_url}</a></p>"
        elif payload.invitation_url:
            role_display = (payload.role or "Faculty Teacher").replace("_", " ").title()
            subject = f"Academic Invitation: Join {payload.workspace_name} as {role_display} | Gradify"
            plain_text = f"""Welcome to Gradify.

You have been invited to join the academic workspace: {payload.workspace_name}
Designated Role: {role_display}

To accept your invitation, set your account password, and enter your workspace cockpit, click the link below:
{payload.invitation_url}

This invitation link is valid for 7 days. If you did not expect this invitation, you can ignore this email.

Gradify Collective — The Academic Operating System.
"""
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Faculty Invitation - Gradify</title>
</head>
<body style="margin: 0; padding: 0; background-color: #000000; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; color: #E1E0CC; -webkit-font-smoothing: antialiased;">
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #000000; padding: 40px 15px;">
    <tr>
      <td align="center">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 580px; background-color: #101010; border: 1px solid rgba(222, 219, 200, 0.18); border-radius: 24px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.85);">
          <tr>
            <td style="padding: 35px 35px 15px 35px; text-align: center;">
              <div style="display: inline-block; padding: 6px 14px; background-color: rgba(222, 219, 200, 0.08); border: 1px solid rgba(222, 219, 200, 0.2); border-radius: 9999px; font-size: 11px; letter-spacing: 2px; color: #DEDBC8; text-transform: uppercase; font-weight: 600;">
                ● {"Student Workspace Protocol" if (payload.role or "").upper() == "STUDENT" else "Workspace Faculty Protocol"}
              </div>
              <h1 style="color: #E1E0CC; font-size: 30px; font-weight: 500; margin: 20px 0 8px; letter-spacing: -0.03em; line-height: 1.2;">
                {"Student Workspace Admission" if (payload.role or "").upper() == "STUDENT" else "Faculty Invitation"}
              </h1>
              <p style="color: rgba(222, 219, 200, 0.7); font-size: 14px; margin: 0; font-style: italic;">
                {"&ldquo;Access your curriculum classrooms, lecture notes, and faculty directory&rdquo;" if (payload.role or "").upper() == "STUDENT" else "&ldquo;Where academic discipline meets effortless collaboration&rdquo;"}
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding: 0 35px;">
              <div style="height: 1px; background-color: rgba(255, 255, 255, 0.08); margin: 20px 0;"></div>
            </td>
          </tr>
          <tr>
            <td style="padding: 0 35px 30px 35px; text-align: left;">
              <p style="color: #c7c6b7; font-size: 15px; line-height: 1.6; margin: 0 0 20px 0;">
                You have been formally invited to join the academic workspace:
              </p>
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #161616; border: 1px solid rgba(222, 219, 200, 0.12); border-radius: 16px; margin: 0 0 25px 0;">
                <tr>
                  <td style="padding: 18px 22px;">
                    <div style="font-size: 11px; color: #888880; font-family: monospace; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">
                      Academic Workspace
                    </div>
                    <div style="font-size: 18px; font-weight: 600; color: #DEDBC8;">
                      {payload.workspace_name}
                    </div>
                    <div style="margin-top: 10px; display: inline-block; padding: 4px 10px; background-color: rgba(222, 219, 200, 0.1); border-radius: 6px; font-size: 11px; font-weight: 600; color: #DEDBC8; font-family: monospace;">
                      ROLE: {role_display.upper()}
                    </div>
                  </td>
                </tr>
              </table>
              <p style="color: #c7c6b7; font-size: 14px; line-height: 1.6; margin: 0 0 25px 0;">
                To accept this seat, please click the button below to set your account password and immediately access your workspace cockpit:
              </p>
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 25px 0 25px 0;">
                <tr>
                  <td align="center">
                    <a href="{payload.invitation_url}" target="_blank" style="background-color: #DEDBC8; color: #000000; display: inline-block; padding: 16px 36px; border-radius: 9999px; font-size: 14px; font-weight: 600; text-decoration: none; letter-spacing: 0.5px; box-shadow: 0 8px 24px rgba(222, 219, 200, 0.25);">
                      ACCEPT INVITATION &amp; SET PASSWORD &rarr;
                    </a>
                  </td>
                </tr>
              </table>
              <p style="color: #777770; font-size: 12px; line-height: 1.6; margin: 20px 0 0 0; text-align: center;">
                Once your password is set, you can seamlessly sign in to Gradify at any time. This link is encrypted and secure.
              </p>
            </td>
          </tr>
          <tr>
            <td style="background-color: #0b0b0b; padding: 20px 35px; border-top: 1px solid rgba(255, 255, 255, 0.06); text-align: center;">
              <p style="color: #555550; font-size: 11px; margin: 0; font-family: monospace;">
                &copy; 2026 Gradify Collective &bull; 256-bit Encrypted Academic Protocol
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
        elif payload.classroom_invitation_url:
            subject = f"You're Invited to Join {payload.classroom_name} — Gradify Classroom"
            plain_text = f"""Welcome to Gradify.

You have been invited to join the academic classroom: {payload.classroom_name}

To accept your invitation and access the classroom, click the link below:
{payload.classroom_invitation_url}

This invitation link is valid for 7 days. If you did not expect this invitation, you can ignore this email.

Gradify Collective — The Academic Operating System.
"""
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Classroom Invitation - Gradify</title>
</head>
<body style="margin: 0; padding: 0; background-color: #000000; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; color: #E1E0CC; -webkit-font-smoothing: antialiased;">
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #000000; padding: 40px 15px;">
    <tr>
      <td align="center">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 580px; background-color: #101010; border: 1px solid rgba(222, 219, 200, 0.18); border-radius: 24px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.85);">
          <tr>
            <td style="padding: 35px 35px 15px 35px; text-align: center;">
              <div style="display: inline-block; padding: 6px 14px; background-color: rgba(222, 219, 200, 0.08); border: 1px solid rgba(222, 219, 200, 0.2); border-radius: 9999px; font-size: 11px; letter-spacing: 2px; color: #DEDBC8; text-transform: uppercase; font-weight: 600;">
                ● Student Classroom Protocol
              </div>
              <h1 style="color: #E1E0CC; font-size: 30px; font-weight: 500; margin: 20px 0 8px; letter-spacing: -0.03em; line-height: 1.2;">
                Classroom Invitation
              </h1>
              <p style="color: rgba(222, 219, 200, 0.7); font-size: 14px; margin: 0; font-style: italic;">
                &ldquo;Your academic journey begins here&rdquo;
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding: 0 35px;">
              <div style="height: 1px; background-color: rgba(255, 255, 255, 0.08); margin: 20px 0;"></div>
            </td>
          </tr>
          <tr>
            <td style="padding: 0 35px 30px 35px; text-align: left;">
              <p style="color: #c7c6b7; font-size: 15px; line-height: 1.6; margin: 0 0 20px 0;">
                You have been formally invited to join the academic classroom:
              </p>
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #161616; border: 1px solid rgba(222, 219, 200, 0.12); border-radius: 16px; margin: 0 0 25px 0;">
                <tr>
                  <td style="padding: 18px 22px;">
                    <div style="font-size: 11px; color: #888880; font-family: monospace; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">
                      Academic Classroom
                    </div>
                    <div style="font-size: 18px; font-weight: 600; color: #DEDBC8;">
                      {payload.classroom_name}
                    </div>
                    <div style="margin-top: 10px; display: inline-block; padding: 4px 10px; background-color: rgba(222, 219, 200, 0.1); border-radius: 6px; font-size: 11px; font-weight: 600; color: #DEDBC8; font-family: monospace;">
                      ROLE: STUDENT
                    </div>
                  </td>
                </tr>
              </table>
              <p style="color: #c7c6b7; font-size: 14px; line-height: 1.6; margin: 0 0 25px 0;">
                Click the button below to set your password, provide your roll number, and immediately access the classroom:
              </p>
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 25px 0 25px 0;">
                <tr>
                  <td align="center">
                    <a href="{payload.classroom_invitation_url}" target="_blank" style="background-color: #DEDBC8; color: #000000; display: inline-block; padding: 16px 36px; border-radius: 9999px; font-size: 14px; font-weight: 600; text-decoration: none; letter-spacing: 0.5px; box-shadow: 0 8px 24px rgba(222, 219, 200, 0.25);">
                      JOIN CLASSROOM &amp; SET PASSWORD &rarr;
                    </a>
                  </td>
                </tr>
              </table>
              <p style="color: #777770; font-size: 12px; line-height: 1.6; margin: 20px 0 0 0; text-align: center;">
                Once set, you can sign in to Gradify at any time to access your classroom. This link is valid for 7 days.
              </p>
            </td>
          </tr>
          <tr>
            <td style="background-color: #0b0b0b; padding: 20px 35px; border-top: 1px solid rgba(255, 255, 255, 0.06); text-align: center;">
              <p style="color: #555550; font-size: 11px; margin: 0; font-family: monospace;">
                &copy; 2026 Gradify Collective &bull; 256-bit Encrypted Academic Protocol
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
        elif payload.note_title:
            subject = f"New notes uploaded in {payload.classroom_name}: {payload.note_title}"
            body = f"Hello,\n\nYour teacher has uploaded new notes '{payload.note_title}' in classroom '{payload.classroom_name}'."
            if payload.note_url:
                body += f"\n\nYou can access the notes here: {payload.note_url}"
            plain_text = body
            html_content = f"<p>Hello,</p><p>Your teacher has uploaded new notes <strong>'{payload.note_title}'</strong> in classroom <strong>'{payload.classroom_name}'</strong>.</p>"
            if payload.note_url:
                html_content += f"<p><a href='{payload.note_url}'>View Notes</a></p>"
        else:
            verify_url = f"{settings.FRONTEND_URL}/?token={payload.raw_token}&email={payload.email}"
            subject = "Activate Your Gradify Identity — Verification Required"
            plain_text = f"""Welcome to Gradify.

Turn Your College Chaos Into Smarter Academic Workflow.

Please activate your Gradify account and enter your cockpit by clicking the link below:
{verify_url}

This link is valid for 30 minutes. If you didn't create this account, please ignore this email.

Gradify Collective — The Academic Operating System.
"""
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Activate Your Gradify Identity</title>
</head>
<body style="margin: 0; padding: 0; background-color: #000000; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; color: #E1E0CC; -webkit-font-smoothing: antialiased;">
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #000000; padding: 40px 15px;">
    <tr>
      <td align="center">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 580px; background-color: #101010; border: 1px solid rgba(222, 219, 200, 0.15); border-radius: 24px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.8);">
          <tr>
            <td style="padding: 35px 35px 15px 35px; text-align: center;">
              <div style="display: inline-block; padding: 6px 14px; background-color: rgba(222, 219, 200, 0.08); border: 1px solid rgba(222, 219, 200, 0.2); border-radius: 9999px; font-size: 11px; letter-spacing: 2px; color: #DEDBC8; text-transform: uppercase; font-weight: 600;">
                ● The Academic Operating System
              </div>
              <h1 style="color: #E1E0CC; font-size: 32px; font-weight: 500; margin: 20px 0 8px; letter-spacing: -0.03em; line-height: 1.15;">
                Activate Your Identity
              </h1>
              <p style="color: rgba(222, 219, 200, 0.7); font-size: 14px; margin: 0; font-style: italic;">
                &ldquo;Turn Your College Chaos Into Smarter Academic Workflow&rdquo;
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding: 0 35px;">
              <div style="height: 1px; background-color: rgba(255, 255, 255, 0.08); margin: 20px 0;"></div>
            </td>
          </tr>
          <tr>
            <td style="padding: 0 35px 30px 35px; text-align: left;">
              <p style="color: #c7c6b7; font-size: 15px; line-height: 1.6; margin: 0 0 25px 0;">
                Welcome to <strong style="color: #DEDBC8;">Gradify</strong>. Before you can access your personalized cockpit, automated streak intelligence, and curriculum workspace, please confirm your academic email address.
              </p>
              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 25px 0 25px 0;">
                <tr>
                  <td align="center">
                    <a href="{verify_url}" target="_blank" style="background-color: #DEDBC8; color: #000000; display: inline-block; padding: 16px 40px; border-radius: 9999px; font-size: 14px; font-weight: 600; text-decoration: none; letter-spacing: 0.5px; box-shadow: 0 8px 24px rgba(222, 219, 200, 0.25);">
                      VERIFY EMAIL &amp; ENTER COCKPIT &rarr;
                    </a>
                  </td>
                </tr>
              </table>
              <p style="color: #777770; font-size: 12px; line-height: 1.6; margin: 20px 0 0 0; text-align: center;">
                Clicking the button immediately verifies your academic account, logs you in, and grants access to your workspace cockpit. Valid for 30 minutes.
              </p>
            </td>
          </tr>
          <tr>
            <td style="background-color: #0b0b0b; padding: 20px 35px; border-top: 1px solid rgba(255, 255, 255, 0.06); text-align: center;">
              <p style="color: #555550; font-size: 11px; margin: 0; font-family: monospace;">
                &copy; 2026 Gradify Collective &bull; 256-bit Encrypted Academic Protocol
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
        return subject, plain_text, html_content

    async def _send_via_resend(self, subject: str, plain_text: str, html_content: str, recipient: str) -> bool:
        if not settings.RESEND_API_KEY:
            return False
        raw_addr = (self.sender_email or "").strip()
        if "<" in raw_addr and ">" in raw_addr:
            raw_addr = raw_addr.split("<")[-1].split(">")[0].strip()
        if not raw_addr or "@" not in raw_addr:
            raw_addr = "onboarding@resend.dev"
        from_header = f"Gradify <{raw_addr}>"
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY.strip()}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": from_header,
                    "to": [recipient],
                    "subject": subject,
                    "text": plain_text,
                    "html": html_content,
                },
            )
            if res.status_code in {200, 201, 202}:
                print(f"[RESEND SUCCESS] Email delivered via HTTP to {recipient}: {res.json()}")
                return True
            print(f"[RESEND ERROR] Status {res.status_code}: {res.text}")
            return False

    async def _send_via_brevo(self, subject: str, plain_text: str, html_content: str, recipient: str) -> bool:
        if not settings.BREVO_API_KEY:
            return False
        raw_addr = (self.sender_email or self.username or "").strip()
        if "<" in raw_addr and ">" in raw_addr:
            raw_addr = raw_addr.split("<")[-1].split(">")[0].strip()
        if not raw_addr or "@" not in raw_addr:
            return False
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={
                    "api-key": settings.BREVO_API_KEY.strip(),
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
                json={
                    "sender": {"name": "Gradify", "email": raw_addr},
                    "to": [{"email": recipient}],
                    "subject": subject,
                    "textContent": plain_text,
                    "htmlContent": html_content,
                },
            )
            if res.status_code in {200, 201, 202}:
                print(f"[BREVO SUCCESS] Email delivered via HTTP to {recipient}: {res.json()}")
                return True
            print(f"[BREVO ERROR] Status {res.status_code}: {res.text}")
            return False

    async def send_email(self, payload: Payload):
        subject, plain_text, html_content = self._build_email_content(payload)

        if settings.BREVO_API_KEY:
            sent = await self._send_via_brevo(subject, plain_text, html_content, payload.email)
            if sent:
                return

        if settings.RESEND_API_KEY:
            sent = await self._send_via_resend(subject, plain_text, html_content, payload.email)
            if sent:
                return

        message = EmailMessage()
        sender_addr = self.sender_email or self.username
        message["From"] = f"Gradify <{sender_addr}>"
        message["To"] = payload.email
        message["Reply-To"] = sender_addr
        message["Subject"] = subject
        message.set_content(plain_text)
        if html_content and not payload.note_title:
            message.add_alternative(html_content, subtype="html")

        username = self.username.strip() if self.username else ""
        password = self.password.replace(" ", "").strip() if self.password else ""
        port = int(self.port) if self.port else 587
        use_tls = (port == 465)
        start_tls = (port == 587)

        print(f"[SMTP] Dispatching email to {payload.email} via {self.host}:{port} (use_tls={use_tls}, start_tls={start_tls})...")
        res = await aiosmtplib.send(
            message,
            hostname=self.host,
            port=port,
            username=username,
            password=password,
            use_tls=use_tls,
            start_tls=start_tls,
            timeout=15,
        )
        print(f"[SMTP SUCCESS] Email delivered to {payload.email}: {res}")

