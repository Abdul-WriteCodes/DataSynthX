# DataSynthX — Access Key & Credits Setup Guide

## Overview

The app uses a **Google Sheet** as a live key/credits database.
Each row = one user key. Streamlit secrets hold the credentials to read/write it.

---

## 1. Google Sheet Structure

Create a Google Sheet. Add a tab named exactly: `datasynthx_keys`

The tab must have these **exact column headers** in row 1:

| access_key | credits_remaining | owner | plan |
|---|---|---|---|
| DSX-STARTER-001 | 20 | Alice | Starter |
| DSX-PRO-002 | 100 | Bob | Pro |
| DSX-TEAM-003 | 500 | Acme Corp | Team |

- **access_key** — unique string you issue to each customer (e.g. `DSX-XXXX-XXXX-XXXX`)
- **credits_remaining** — integer; decrements by 1 on each Generate run
- **owner** — display name shown in the sidebar
- **plan** — plan label shown in the sidebar

---

## 2. Google Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → create a project
2. Enable **Google Sheets API** and **Google Drive API**
3. Create a **Service Account** → download the JSON key file
4. Share your Google Sheet with the service account email (Editor permission)

---

## 3. Streamlit Secrets

In `.streamlit/secrets.toml` (local) or the Streamlit Cloud secrets editor, add:

```toml
[datasynthx]
google_sheet_id = "YOUR_GOOGLE_SHEET_ID"
# The Sheet ID is in the URL: docs.google.com/spreadsheets/d/THIS_PART/edit

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "key-id"
private_key = "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
client_email = "your-sa@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-sa%40your-project.iam.gserviceaccount.com"
```

---

## 4. Payment Links (Stripe)

In `app_v3.py`, find the `PLANS` list (~line 300) and replace the placeholder links:

```python
PLANS = [
    { ..., "link": "https://buy.stripe.com/YOUR_STARTER_LINK" },
    { ..., "link": "https://buy.stripe.com/YOUR_PRO_LINK"     },
    { ..., "link": "https://buy.stripe.com/YOUR_TEAM_LINK"    },
]
```

In Stripe, create Payment Links for each plan. After a customer pays,
manually (or via Stripe webhook) add their key row to the Google Sheet.

---

## 5. Dependencies

Add to `requirements.txt`:

```
gspread>=6.0
google-auth>=2.0
```

---

## 6. Credit Flow

```
User enters key → Google Sheet lookup → credits > 0 → access granted
                                      → credits = 0 → blocked, prompt to buy

Generate button clicked → credit check → run generation → deduct_credit() writes back to Sheet
```

Each generate run deducts **1 credit**. The `CREDITS_PER_RUN` constant at the top of `app_v3.py` can be changed.
