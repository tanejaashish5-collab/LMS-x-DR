"""
ATLAS Email Service -- Real email sending via Resend API

Falls back gracefully to logging when RESEND_API_KEY is not set.
All emails are logged to atlas_outreach table when a Supabase client is provided.
"""

import os
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import httpx

logger = logging.getLogger("atlas.email")


@dataclass
class EmailResult:
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


class EmailService:
    """Send real emails via Resend API"""

    def __init__(self, supabase_client=None):
        self.api_key = os.getenv("RESEND_API_KEY", "")
        self.default_from = "Ashish Taneja <ashish@forgevoice.studio>"
        self.api_url = "https://api.resend.com/emails"
        self.supabase = supabase_client
        self._enabled = bool(self.api_key)

        if not self._enabled:
            logger.warning(
                "RESEND_API_KEY not set -- emails will be logged but NOT sent"
            )

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None,
        pipeline_id: Optional[str] = None,
        email_type: Optional[str] = None,
    ) -> EmailResult:
        """Send an email via Resend. Falls back to logging if API key missing."""

        sender = from_email or self.default_from

        # Always log the attempt
        logger.info(f"EMAIL: To={to}, Subject={subject}, Type={email_type}")

        # Log to database if available
        if self.supabase and pipeline_id:
            try:
                self.supabase.table("atlas_outreach").insert(
                    {
                        "pipeline_id": pipeline_id,
                        "email_type": email_type or "unknown",
                        "subject": subject,
                        "body": body,
                        "to_email": to,
                        "from_email": sender,
                        "status": "sending",
                        "sent_at": datetime.now(timezone.utc).isoformat(),
                    }
                ).execute()
            except Exception as e:
                logger.error(f"Failed to log email to database: {e}")

        # If no API key, log only
        if not self._enabled:
            logger.warning(f"EMAIL SIMULATED (no API key): {subject} -> {to}")
            return EmailResult(
                success=True,
                message_id="simulated",
                error="No RESEND_API_KEY",
            )

        # Send via Resend
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": sender,
                        "to": [to],
                        "subject": subject,
                        "html": body.replace("\n", "<br>"),
                        "reply_to": reply_to or "ashish@forgevoice.studio",
                    },
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    message_id = data.get("id", "unknown")
                    logger.info(f"EMAIL SENT: {message_id} -> {to}")

                    # Update database status
                    if self.supabase and pipeline_id:
                        try:
                            self.supabase.table("atlas_outreach").update(
                                {"status": "sent"}
                            ).eq("pipeline_id", pipeline_id).eq(
                                "email_type", email_type
                            ).execute()
                        except Exception:
                            pass

                    return EmailResult(success=True, message_id=message_id)
                else:
                    error_msg = response.text
                    logger.error(
                        f"EMAIL FAILED: {response.status_code} -- {error_msg}"
                    )
                    return EmailResult(success=False, error=error_msg)

        except Exception as e:
            logger.error(f"EMAIL ERROR: {e}")
            return EmailResult(success=False, error=str(e))

    def send_email_sync(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        pipeline_id: Optional[str] = None,
        email_type: Optional[str] = None,
    ) -> EmailResult:
        """Synchronous email sending for non-async contexts."""
        import asyncio

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Already in async context, use thread pool
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as pool:
                    result = pool.submit(
                        asyncio.run,
                        self.send_email(
                            to,
                            subject,
                            body,
                            from_email,
                            pipeline_id=pipeline_id,
                            email_type=email_type,
                        ),
                    ).result()
                return result
            else:
                return loop.run_until_complete(
                    self.send_email(
                        to,
                        subject,
                        body,
                        from_email,
                        pipeline_id=pipeline_id,
                        email_type=email_type,
                    )
                )
        except RuntimeError:
            return asyncio.run(
                self.send_email(
                    to,
                    subject,
                    body,
                    from_email,
                    pipeline_id=pipeline_id,
                    email_type=email_type,
                )
            )


# Singleton
_service: Optional[EmailService] = None


def get_email_service(supabase_client=None) -> EmailService:
    global _service
    if _service is None:
        _service = EmailService(supabase_client)
    return _service
