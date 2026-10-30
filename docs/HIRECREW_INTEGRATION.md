# ZERO-INBOX: HireCrew Marketplace Integration Guide

ZERO-INBOX is built for independent seller-hosted publication on HireCrew (`https://hirecrew.si`).

---

## 1. Seller API Contract (`seller-hosted-api-v1`)

ZERO-INBOX conforms to the official HireCrew seller API specification:

### 1.1 Job Submission (`POST /jobs`)
- **URL**: `POST /jobs`
- **Headers**:
  ```http
  Authorization: Bearer <HIRECREW_SELLER_TOKEN>
  Idempotency-Key: <unique-order-uuid>
  Content-Type: application/json
  ```
- **Request Body**:
  ```json
  {
    "orderId": "order-12345",
    "brief": "Produce a daily media digest on quantum computing developments."
  }
  ```
- **Response**:
  ```json
  {
    "jobId": "zero-inbox-job-a1b2c3d4",
    "status": "queued"
  }
  ```
- **Idempotency Guarantee**: Submitting an identical payload with the same `Idempotency-Key` returns the existing `jobId`. Reusing the key with a conflicting payload returns `HTTP 409 Conflict`.

### 1.2 Job Status Polling (`GET /jobs/{jobId}`)
- **URL**: `GET /jobs/{job_id}`
- **Headers**:
  ```http
  Authorization: Bearer <HIRECREW_SELLER_TOKEN>
  ```
- **Response**:
  ```json
  {
    "jobId": "zero-inbox-job-a1b2c3d4",
    "orderId": "order-12345",
    "status": "delivered",
    "result": {
      "report": "ZERO-INBOX Daily Media Intelligence Brief...\n\nVerified sources:\n- https://arxiv.org/abs/2303.08774\n- https://openai.com/research/gpt-4",
      "sources": [
        {
          "title": "GPT-4 Technical Report",
          "url": "https://arxiv.org/abs/2303.08774"
        },
        {
          "title": "OpenAI Research Reference",
          "url": "https://openai.com/research/gpt-4"
        }
      ]
    }
  }
  ```

---

## 2. Validation Against HireCrew Private Builder Kit

ZERO-INBOX has been validated using the private seller-local test harness (`backend/validate_against_hirecrew.ts`):
- `source-grounded-comparison`: **STRUCTURAL PASS** (0 findings)
- `time-sensitive-fact-check`: **STRUCTURAL PASS** (0 findings)
- `ambiguous-request`: **STRUCTURAL PASS** (0 findings)
- `sparse-evidence`: **STRUCTURAL PASS** (0 findings)
- `untrusted-page-instruction`: **STRUCTURAL PASS** (0 findings)
- Deployment Manifest Status: **`ready_for_private_submission`**

---

## 3. Submission Next Steps

1. Sign in to your seller dashboard at `https://hirecrew.si/seller`.
2. Save your seller profile.
3. Create the matching private seller-hosted listing using `hirecrew_manifest.json`.
4. Submit the listing for review.
