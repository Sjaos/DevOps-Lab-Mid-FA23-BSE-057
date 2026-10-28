from flask import Flask, render_template, request
from urllib.parse import urlparse

app = Flask(__name__)


submissions = []


def valid_url(url):
    """Check that URL starts with http/https and has a domain."""
    try:
        result = urlparse(url)
        hostname = result.hostname
        port = result.port
        return (
            result.scheme in ("http", "https")
            and bool(hostname)
            and not any(character.isspace() for character in url)
            and (port is None or 1 <= port <= 65535)
        )
    except ValueError:
        return False


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    success = None

    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip()
        registration_number = request.form.get(
            "registration_number", ""
        ).strip()
        assignment_title = request.form.get(
            "assignment_title", ""
        ).strip()
        submission_url = request.form.get("submission_url", "").strip()

        # Required fields validation
        if not student_name:
            error = "Student Name is required."

        elif not registration_number:
            error = "Registration Number is required."

        elif not assignment_title:
            error = "Assignment Title is required."

        elif not submission_url:
            error = "Submission URL is required."

        # URL validation
        elif not valid_url(submission_url):
            error = "Please enter a valid http/https URL."

        else:
            submission = {
                "student_name": student_name,
                "registration_number": registration_number,
                "assignment_title": assignment_title,
                "submission_url": submission_url,
            }

            submissions.append(submission)
            success = "Submission saved successfully."

    return render_template(
        "index.html",
        submissions=submissions,
        error=error,
        success=success,
    )


if __name__ == "__main__":
    app.run(debug=True)
