#!/usr/bin/env python3
"""Send the generated digest through SMTP."""

from __future__ import annotations

import json
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"


def required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Required environment variable is missing: {name}")
    return value


def recipients(raw: str) -> list[str]:
    result = [item.strip() for item in raw.split(",") if item.strip()]
    if not result:
        raise RuntimeError("MAIL_TO does not contain a valid address.")
    return result


def main() -> int:
    try:
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
        smtp_port = int(os.getenv("SMTP_PORT", "465"))
        smtp_username = required("SMTP_USERNAME")
        smtp_password = required("SMTP_PASSWORD")
        mail_to = recipients(required("MAIL_TO"))
        mail_from = os.getenv("MAIL_FROM", "").strip() or smtp_username

        # Google displays app passwords in grouped blocks. SMTP needs no spaces.
        if smtp_host.lower() == "smtp.gmail.com":
            smtp_password = smtp_password.replace(" ", "")

        data = json.loads(
            (OUTPUT_DIR / "latest.json").read_text(encoding="utf-8")
        )
        target_date = data["date"]
        html_body = (OUTPUT_DIR / "digest.html").read_text(encoding="utf-8")
        text_body = (OUTPUT_DIR / "digest.txt").read_text(encoding="utf-8")

        message = EmailMessage()
        message["Subject"] = f"Hacker News 昨日 Top 30｜{target_date}"
        message["From"] = mail_from
        message["To"] = ", ".join(mail_to)
        message.set_content(text_body)
        message.add_alternative(html_body, subtype="html")

        context = ssl.create_default_context()
        if smtp_port == 465:
            with smtplib.SMTP_SSL(
                smtp_host,
                smtp_port,
                context=context,
                timeout=30,
            ) as smtp:
                smtp.login(smtp_username, smtp_password)
                smtp.send_message(message)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as smtp:
                smtp.ehlo()
                smtp.starttls(context=context)
                smtp.ehlo()
                smtp.login(smtp_username, smtp_password)
                smtp.send_message(message)

        print(
            f"Email sent to {', '.join(mail_to)} for {target_date}.",
            file=sys.stderr,
        )
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
