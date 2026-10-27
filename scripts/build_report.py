import argparse
from datetime import datetime, timezone
import json
import os
from urllib.request import Request, urlopen


def create_report(pytest_data, metadata=None):
    metadata = metadata or {}
    tests = pytest_data.get("tests", [])
    counts = {"total": len(tests), "passed": 0, "failed": 0, "skipped": 0}
    pytest_exit_code = pytest_data.get("exitcode", 0)
    results = []

    for test in tests:
        outcome = test.get("outcome", "unknown")
        if outcome == "passed":
            counts[outcome] += 1
        elif outcome == "skipped":
            counts[outcome] += 1
        else:
            counts["failed"] += 1

        failure_message = None
        for phase in ("call", "setup", "teardown"):
            phase_result = test.get(phase, {})
            if phase_result.get("outcome") in ("failed", "error"):
                failure_message = phase_result.get("longrepr")
                if failure_message is not None:
                    failure_message = str(failure_message)
                break

        results.append(
            {
                "name": test.get("nodeid", "unknown"),
                "result": outcome,
                "failure_message": failure_message,
            }
        )

    return {
        "repository": metadata.get("repository", "local"),
        "branch": metadata.get("branch", "local"),
        "commit_sha": metadata.get("commit_sha", "unknown"),
        "pipeline_run_id": metadata.get("pipeline_run_id", "local"),
        "execution_timestamp": datetime.now(timezone.utc).isoformat(),
        "status": (
            "failed"
            if counts["failed"] or pytest_exit_code != 0
            else "passed"
        ),
        "pytest_exit_code": pytest_exit_code,
        "test_counts": counts,
        "tests": results,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Send pytest results to the local JSON report receiver."
    )
    parser.add_argument(
        "--input",
        default="pytest-report.json",
        help="pytest-json-report output file (default: pytest-report.json)",
    )
    parser.add_argument(
        "--url",
        default=os.environ.get(
            "REPORT_RECEIVER_URL", "http://127.0.0.1:9000/report"
        ),
        help="report receiver endpoint",
    )
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as report_file:
        pytest_data = json.load(report_file)

    metadata = {
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "branch": os.environ.get(
            "GITHUB_HEAD_REF", os.environ.get("GITHUB_REF_NAME", "local")
        ),
        "commit_sha": os.environ.get("GITHUB_SHA", "unknown"),
        "pipeline_run_id": os.environ.get("GITHUB_RUN_ID", "local"),
    }
    report = create_report(pytest_data, metadata)
    request = Request(
        args.url,
        data=json.dumps(report).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=10) as response:
        if response.status != 201:
            raise RuntimeError(
                f"Report receiver returned unexpected HTTP status "
                f"{response.status}."
            )
        print(response.read().decode("utf-8"))
    print(
        f"Sent {report['test_counts']['total']} test results "
        f"({report['status']})."
    )


if __name__ == "__main__":
    main()