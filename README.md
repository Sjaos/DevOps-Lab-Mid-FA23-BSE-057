
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

## Push changes to GitHub

This project is already connected to its GitHub repository. To publish changes,
stage only the files you intend to include, then commit and push. For example:

```powershell
git add .github/workflows/ci.yml README.md pytest.ini tests/test_reports.py demo_tests/test_failure_email.py
git commit -m "Add manual failing report email demo"
git push
```

## GitHub Actions

The workflow runs on every push, pull request, and manual dispatch. It uses a
self-hosted Windows runner so the localhost report receiver and its
`test-report.json` run on your computer. To register the runner, open your
GitHub repository's **Settings → Actions → Runners → New self-hosted runner**,
select Windows, and follow GitHub's setup steps on this computer. Keep the
runner online while pushing or triggering a workflow. The runner saves
`test-report.json` directly in its checked-out project folder, including when
tests fail. The GitHub artifact-upload step is omitted because your runner
cannot resolve GitHub's artifact service (`ENOTFOUND`); this does not affect
test execution or saving the local report.

To email yourself an example of a failed test report without changing the
portal or breaking normal test runs:

1. Open **Actions → Assignment Portal CI → Run workflow** on the `main` branch.
2. Select **Send a deliberate failing-test report email** and start the run.
3. The workflow adds one dedicated failing test, saves and emails the report,
   and is expected to show a red failed-test result.
4. Run the workflow again with the option unchecked to get a normal passing
   result.

The demo test is not collected by normal pushes or pull requests. The failed
email is sent only to the configured `REPORT_EMAIL_TO` address.

### Optional email reports

Add these repository Actions secrets to email reports after both successful and
failed test runs:

- `REPORT_EMAIL_TO`: one or more comma-separated recipient addresses
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`
- `REPORT_EMAIL_FROM`: optional sender address (defaults to `SMTP_USERNAME`)
- `SMTP_USE_SSL`: optional `true` for implicit TLS (otherwise STARTTLS is used)

For Gmail, use `smtp.gmail.com` as `SMTP_HOST`, port `587`, and `false` for
`SMTP_USE_SSL` (STARTTLS). `SMTP_USERNAME` and `REPORT_EMAIL_FROM` should be
the Gmail address. Use a Google App Password for `SMTP_PASSWORD`, not the
account's regular password. Store each value under **Repository Settings →
Secrets and variables → Actions**. The self-hosted runner must also be able to
resolve `smtp.gmail.com` and connect to the selected SMTP port.

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
- `demo_tests/`: deliberate test used only for the manual failure-email demo
- `pytest.ini`: keeps the demo test out of regular runs
- `scripts/build_report.py`: builds and sends the actual pytest report
- `scripts/send_email.py`: optional SMTP report delivery
- `receiver/receiver.py`: localhost JSON receiver
- `.github/workflows/ci.yml`: CI, local report, optional email, and Pages deployment
- `site/`: static Pages demonstration

## Student Information

- Name: Shahab Ahmed
- Registration Number: FA23-BSE-057
-Updated on 2026-10-28
