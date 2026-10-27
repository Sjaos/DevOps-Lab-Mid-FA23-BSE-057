from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path

REPORT_PATH = Path("test-report.json")
MAX_REPORT_BYTES = 5 * 1024 * 1024


class ReportHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != "/health":
            self._send_json(404, {"error": "Not found."})
            return

        self._send_json(200, {"status": "ready"})

    def do_POST(self):
        if self.path != "/report":
            self._send_json(404, {"error": "Not found."})
            return

        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self._send_json(400, {"error": "A valid Content-Length is required."})
            return

        if length < 0:
            self._send_json(400, {"error": "Content-Length cannot be negative."})
            return
        if length > MAX_REPORT_BYTES:
            self._send_json(413, {"error": "Report exceeds the 5 MiB limit."})
            return

        try:
            report = json.loads(self.rfile.read(length))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "Request body must be valid JSON."})
            return

        if not isinstance(report, dict):
            self._send_json(400, {"error": "Report must be a JSON object."})
            return

        REPORT_PATH.write_text(
            json.dumps(report, indent=2) + "\n",
            encoding="utf-8",
        )
        self._send_json(201, {"status": "saved", "path": str(REPORT_PATH)})


if __name__ == "__main__":
    port = int(os.environ.get("REPORT_RECEIVER_PORT", "9000"))
    server = HTTPServer(("127.0.0.1", port), ReportHandler)
    print(f"Report receiver listening on http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping report receiver.")
    finally:
        server.server_close()