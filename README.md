
# CSC418 Assignment Submission Portal

A small Flask portal for assignment-link submissions, with automated tests, a
local JSON report receiver, and GitHub Actions CI.

## Run the portal

On Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>. Students submit their name, registration number,
assignment title, and an HTTP or HTTPS link. Required fields and the link are
validated; accepted submissions appear in the list while the app is running.
Submissions are intentionally stored in memory and reset when the app restarts.

## Run tests and save a local report

Install the requirements, then run these commands in two PowerShell terminals
from the project folder.

Terminal 1:

```powershell
python receiver\receiver.py
```

Terminal 2:

```powershell
pytest -v --json-report --json-report-file=pytest-report.json
python scripts\build_report.py --input pytest-report.json
```

The receiver accepts reports only from the local machine and saves the enriched
report as `test-report.json`. The report includes repository, branch, commit,
pipeline run, execution time, overall status, test counts, individual results,
and failure details. A failed test run still writes and sends its JSON report.
The pytest command retains its non-zero exit status when tests fail.

## Connect the project to GitHub

This project folder is not currently connected to a GitHub repository. Create
or choose an empty repository, then run these commands from the project folder
(replace the URL with your repository's URL):

```powershell
git init -b main
git add .
git commit -m "Complete CSC418 assignment portal"
git remote add origin https://github.com/<account>/<repository>.git
git push -u origin main
```

## GitHub Actions

The workflow runs on every push, pull request, and manual dispatch. It uses a
self-hosted Windows runner so the localhost report receiver and its
`test-report.json` run on your computer. To register the runner, open your
GitHub repository's **Settings → Actions → Runners → New self-hosted runner**,
select Windows, and follow GitHub's setup steps on this computer. Keep the
runner online while pushing or triggering a workflow. Reports are also uploaded
as workflow artifacts, including when tests fail.

To demonstrate failure handling, temporarily introduce a defect in URL
validation (for example, make `valid_url` accept every input), push the change,
and inspect the failed test run and its `test-report.json` artifact. Restore URL
validation and push again; the passing run produces a new report. Do not leave
the intentional defect in the final revision.

### Optional email reports

Add these repository Actions secrets to email reports after both successful and
failed test runs:

- `REPORT_EMAIL_TO`: one or more comma-separated recipient addresses
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`
- `REPORT_EMAIL_FROM`: optional sender address (defaults to `SMTP_USERNAME`)
- `SMTP_USE_SSL`: optional `true` for implicit TLS (otherwise STARTTLS is used)

Email contains the commit, run, overall result, test counts, and individual
results; the complete JSON report is attached. SMTP credentials remain in
Actions secrets. If no email settings are provided, the workflow reports that
email delivery was skipped.

### Optional GitHub Pages demo

The `main` branch is deployed to GitHub Pages only after the test job passes.
In the repository settings, enable **Pages → Build and deployment → GitHub
Actions**. The deployed static demo stores its sample submissions in that
browser's local storage; the Flask application remains the full server-backed
portal. The workflow run's deployment step provides the published URL.

## Project layout

- `app.py`: Flask submission portal
- `tests/`: portal, report-generation, and receiver tests
- `scripts/build_report.py`: builds and sends the actual pytest report
- `scripts/send_email.py`: optional SMTP report delivery
- `receiver/receiver.py`: localhost JSON receiver
- `.github/workflows/ci.yml`: CI, report artifact, optional email, and Pages deployment
- `site/`: static Pages demonstration

## Student Information

- Name: Shahab Ahmed
- Registration Number: FA23-BSE-057


