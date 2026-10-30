"""
ZERO-INBOX: Newsletter Ingestion Adapter (MIME / RFC822 / IMAP / Webhook Support)
"""

import email
from email import policy
from email.message import EmailMessage
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime, timezone
import re
from bs4 import BeautifulSoup

from app.core.models import SourceConfig, RawArticle
from app.ingestion.base import SourceConnector


class NewsletterConnector(SourceConnector):
    """
    Ingests and parses email newsletters from standard MIME streams,
    forwarding hooks, or IMAP payloads while strictly filtering out personal emails.
    """

    def validate_configuration(self, source: SourceConfig) -> Tuple[bool, str]:
        # Newsletters can be configured with an email address, inbox prefix, or webhook ID
        if not source.name:
            return False, "Newsletter source must have a display name."
        return True, ""

    def is_likely_newsletter(self, msg: EmailMessage) -> Tuple[bool, str]:
        """
        Determines whether an email is a legitimate bulk newsletter rather than private personal mail.
        Checks headers like List-Unsubscribe, Precedence: bulk, and sender signatures.
        """
        # 1. Check for standard bulk/list headers
        if msg.get("List-Unsubscribe") or msg.get("List-Id") or msg.get("List-Post"):
            return True, "Verified List-Unsubscribe header"

        precedence = msg.get("Precedence", "").lower()
        if precedence in ("bulk", "list", "newsletter"):
            return True, f"Precedence is {precedence}"

        # 2. Check for known newsletter platform headers
        for hdr in ("X-Substack-Post-Id", "X-Beehiiv-Post-Id", "X-Mailchimp-Campaign-Id", "X-Buttondown"):
            if msg.get(hdr):
                return True, f"Identified newsletter provider header: {hdr}"

        # 3. Check subject/body hints
        subject = msg.get("Subject", "").lower()
        if any(term in subject for term in ("issue #", "weekly", "digest", "briefing", "roundup", "newsletter")):
            return True, "Subject keywords match newsletter profile"

        return False, "Not recognized as a bulk newsletter; excluded for privacy protection."

    def parse_raw_email(self, raw_bytes_or_str: Any, source: SourceConfig) -> Optional[RawArticle]:
        """Parses a raw email (RFC822 bytes or text) into a RawArticle."""
        if isinstance(raw_bytes_or_str, str):
            msg = email.message_from_string(raw_bytes_or_str, policy=policy.default)
        else:
            msg = email.message_from_bytes(raw_bytes_or_str, policy=policy.default)

        is_newsletter, reason = self.is_likely_newsletter(msg)
        if not is_newsletter:
            return None

        subject = msg.get("Subject", "Untitled Newsletter")
        sender = msg.get("From", source.name)
        date_str = msg.get("Date")

        # Parse date
        pub_date = None
        if date_str:
            try:
                pub_date = email.utils.parsedate_to_datetime(date_str)
            except Exception:
                pub_date = datetime.now(timezone.utc)

        # Extract HTML and plain text bodies
        html_body = ""
        text_body = ""

        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get("Content-Disposition", ""))
                if "attachment" in cdispo:
                    continue
                if ctype == "text/html":
                    html_body = part.get_content()
                elif ctype == "text/plain":
                    text_body = part.get_content()
        else:
            if msg.get_content_type() == "text/html":
                html_body = msg.get_content()
            else:
                text_body = msg.get_content()

        content = html_body if html_body else text_body

        # Construct unique message URI
        msg_id = msg.get("Message-ID", f"msg_{hash(subject + str(date_str))}")
        clean_msg_id = re.sub(r"[<> ]", "", msg_id)

        return RawArticle(
            source_id=source.id or "newsletter_source",
            source_name=source.name,
            url=f"mailto:{sender}?msgid={clean_msg_id}",
            title=subject,
            raw_content=content,
            author=sender,
            published_at=pub_date or datetime.now(timezone.utc),
            retrieved_at=datetime.utcnow(),
            metadata={
                "message_id": clean_msg_id,
                "detection_reason": reason,
                "has_html": bool(html_body)
            }
        )

    async def fetch_updates(
        self, source: SourceConfig
    ) -> Tuple[List[RawArticle], Optional[str], Optional[str]]:
        # In a production setup, this queries IMAP / Gmail API or mailbox storage.
        # If simulated or webhook-fed, it processes cached unread messages.
        return [], source.etag, source.last_modified

    def get_source_metadata(self, source: SourceConfig) -> Dict[str, Any]:
        return {
            "connector": "NewsletterConnector",
            "privacy_mode": "Strict Bulk Filter Active",
            "personal_email_suppression": True
        }

