"""
ZERO-INBOX: HireCrew Seller API Contract & Benchmark Test Suite
"""

import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


class TestHireCrewSellerAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.token = settings.hirecrew_seller_token
        self.auth_headers = {"Authorization": f"Bearer {self.token}"}

    def test_auth_rejection(self):
        # Missing auth header
        resp = self.client.post("/jobs", json={"orderId": "order-1", "brief": "test brief"})
        self.assertEqual(resp.status_code, 401)

        # Invalid token
        bad_headers = {"Authorization": "Bearer bad-token-999"}
        resp2 = self.client.post("/jobs", json={"orderId": "order-1", "brief": "test brief"}, headers=bad_headers)
        self.assertEqual(resp2.status_code, 403)

    def test_job_submission_and_poll(self):
        headers = dict(self.auth_headers)
        headers["Idempotency-Key"] = "idemp-key-test-001"

        payload = {
            "orderId": "order-hc-100",
            "brief": "Please provide an executive research brief on quantum computing."
        }

        # 1. Submit
        resp = self.client.post("/jobs", json=payload, headers=headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        job_id = data["jobId"]
        self.assertEqual(data["status"], "queued")

        # 2. Idempotent replay with same key
        replay_resp = self.client.post("/jobs", json=payload, headers=headers)
        self.assertEqual(replay_resp.status_code, 200)
        self.assertEqual(replay_resp.json()["jobId"], job_id)

        # 3. Conflicting payload with same key returns 409
        conflict_payload = {"orderId": "order-hc-DIFFERENT", "brief": "different brief"}
        conflict_resp = self.client.post("/jobs", json=conflict_payload, headers=headers)
        self.assertEqual(conflict_resp.status_code, 409)

        # 4. Poll
        poll_resp = self.client.get(f"/jobs/{job_id}", headers=self.auth_headers)
        self.assertEqual(poll_resp.status_code, 200)
        poll_data = poll_resp.json()
        self.assertIn(poll_data["status"], ["queued", "running", "delivered"])

    def test_benchmark_solutions(self):
        benchmark_cases = [
            "source-grounded-comparison",
            "time-sensitive-fact-check",
            "ambiguous-request",
            "sparse-evidence",
            "untrusted-page-instruction"
        ]

        for case_id in benchmark_cases:
            resp = self.client.post(
                "/jobs",
                json={"orderId": f"bench-{case_id}", "brief": f"Execute benchmark {case_id}"},
                headers=self.auth_headers
            )
            self.assertEqual(resp.status_code, 200)
            job_id = resp.json()["jobId"]

            poll = self.client.get(f"/jobs/{job_id}", headers=self.auth_headers)
            self.assertEqual(poll.status_code, 200)
            data = poll.json()
            self.assertEqual(data["status"], "delivered")
            result = data["result"]
            self.assertGreaterEqual(len(result["report"]), 100)
            self.assertGreaterEqual(len(result["sources"]), 1)

            # Check HireCrew requirement: every source URL must appear verbatim in the report
            for s in result["sources"]:
                self.assertIn(s["url"], result["report"], f"Source URL {s['url']} must be cited verbatim in report.")


if __name__ == "__main__":
    unittest.main()
