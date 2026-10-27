import json
from http.server import HTTPServer
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from receiver import receiver
from scripts.build_report import create_report


def test_report_summarizes_passed_and_failed_tests():
    pytest_data = {
        "tests": [
            {"nodeid": "test_app.py::test_pass", "outcome": "passed"},
            {
                "nodeid": "test_app.py::test_fail",
                "outcome": "failed",
                "call": {
                    "outcome": "failed",
                    "longrepr": "assert 1 == 2",
                },
            },
            {"nodeid": "test_app.py::test_skip", "outcome": "skipped"},
        ]
    }

    report = create_report(
        pytest_data,
        {
            "repository": "example/project",
            "branch": "main",
            "commit_sha": "abc123",
            "pipeline_run_id": "42",
        },
    )

    assert report["status"] == "failed"
    assert report["repository"] == "example/project"
    assert report["commit_sha"] == "abc123"
    assert report["test_counts"] == {
        "total": 3,
        "passed": 1,
        "failed": 1,
        "skipped": 1,
    }
    assert report["tests"][1]["failure_message"] == "assert 1 == 2"
    assert report["execution_timestamp"]


def test_report_marks_collection_error_as_failed():
    report = create_report({"exitcode": 2, "tests": []})

    assert report["status"] == "failed"
    assert report["pytest_exit_code"] == 2


def test_report_receiver_saves_json(tmp_path, monkeypatch):
    output_path = tmp_path / "test-report.json"
    monkeypatch.setattr(receiver, "REPORT_PATH", output_path)
    server = HTTPServer(("127.0.0.1", 0), receiver.ReportHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        report = {"status": "passed", "test_counts": {"total": 1}}
        request = Request(
            f"http://127.0.0.1:{server.server_port}/report",
            data=json.dumps(report).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urlopen(request, timeout=5) as response:
            assert response.status == 201

        assert json.loads(output_path.read_text(encoding="utf-8")) == report
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_report_receiver_rejects_invalid_json():
    server = HTTPServer(("127.0.0.1", 0), receiver.ReportHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        request = Request(
            f"http://127.0.0.1:{server.server_port}/report",
            data=b"not-json",
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with pytest.raises(HTTPError) as error:
            urlopen(request, timeout=5)

        assert error.value.code == 400
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
