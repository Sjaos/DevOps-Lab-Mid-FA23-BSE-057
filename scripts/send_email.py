import argparse
from email.message import EmailMessage
import json
import os
import smtplib
import ssl


def build_message(report, sender, recipients):
    counts = report["test_counts"]
    lines = [
        f"Repository: {report['repository']}",
        f"Branch: {report['branch']}",
        f"Commit: {report['commit_sha']}",
        f"Pipeline run: {report['pipeline_run_id']}",
        f"Overall result: {report['status']}",
        (
            f"Tests: {counts['total']} total, {counts['passed']} passed, "
            f"{counts['failed']} failed, {counts['skipped']} skipped"
        ),
        "",
        "Individual results:",
    ]

    for test in report["tests"]:
        lines.append(f"- {test['result']}: {test['name']}")
        if test["failure_message"]:
            lines.append(f"  {test['failure_message']}")

    message = EmailMessage()
    message["Subject"] = (
        f"Test report: {report['status']} - "
        f"{report['repository']} ({report['commit_sha'][:8]})"
    )
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message.set_content("\n".join(lines))
    message.add_attachment(
        json.dumps(report, indent=2).encode("utf-8"),
        maintype="application",
        subtype="json",
        filename="test-report.json",
    )
    return message


def main():
    parser = argparse.ArgumentParser(
        description="Email a JSON test report using SMTP."
    )
    parser.add_argument("--report", default="test-report.json")
    args = parser.parse_args()

    smtp_host = os.environ.get("SMTP_HOST")
    smtp_username = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    email_to = os.environ.get("REPORT_EMAIL_TO")

    settings = (smtp_host, smtp_username, smtp_password, email_to)
    if not any(settings):
        print("Email report skipped: SMTP and recipient settings are not configured.")
        return
    if not all(settings):
        raise ValueError(
            "Set SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, and REPORT_EMAIL_TO "
            "together to enable email reports."
        )

    with open(args.report, encoding="utf-8") as report_file:
        report = json.load(report_file)

    recipients = [address.strip() for address in email_to.split(",") if address.strip()]
    if not recipients:
        raise ValueError("REPORT_EMAIL_TO must contain at least one email address.")

    sender = os.environ.get("REPORT_EMAIL_FROM") or smtp_username
    port = int(os.environ.get("SMTP_PORT") or "587")
    use_ssl = os.environ.get("SMTP_USE_SSL", "").lower() == "true"
    message = build_message(report, sender, recipients)
    context = ssl.create_default_context()

    if use_ssl:
        with smtplib.SMTP_SSL(
            smtp_host, port, timeout=20, context=context
        ) as server:
            server.login(smtp_username, smtp_password)
            server.send_message(message)
    else:
        with smtplib.SMTP(smtp_host, port, timeout=20) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(smtp_username, smtp_password)
            server.send_message(message)

    print(f"Test report emailed to {', '.join(recipients)}.")


if __name__ == "__main__":
    main()
