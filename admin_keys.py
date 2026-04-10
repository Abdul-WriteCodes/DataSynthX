"""
DataSynthX — Admin Key Management CLI
======================================
Issue unique access keys, top up credits, list all keys, revoke keys.

Usage:
    python admin_keys.py issue   --email user@example.com --plan Pro
    python admin_keys.py issue   --email user@example.com --plan Starter --credits 50
    python admin_keys.py topup   --key DSX-XXXX-XXXX-XXXX --credits 100
    python admin_keys.py list
    python admin_keys.py info    --key DSX-XXXX-XXXX-XXXX
    python admin_keys.py revoke  --key DSX-XXXX-XXXX-XXXX

Config:
    Place your service-account JSON at  ./service_account.json
    Set SHEET_ID in the CONFIG block below, or export it as an env var:
        export DSX_SHEET_ID="your-google-sheet-id"
"""

import argparse
import json
import os
import random
import re
import string
import sys
from datetime import datetime, timezone
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials
from tabulate import tabulate   # pip install tabulate

# ═══════════════════════════════════════════════════════════════════════════
#  CONFIG  — edit these or set env vars
# ═══════════════════════════════════════════════════════════════════════════

SHEET_ID             = os.environ.get("DSX_SHEET_ID", "1DwhsaYqT7B0TObUOoC_a4cnGpMQlS4yZiQjkSE3h0RQ")
SERVICE_ACCOUNT_FILE = os.environ.get("DSX_SA_FILE",  "./service_account.json")
SHEET_TAB            = "datasynthx_keys"

PLAN_DEFAULTS = {
    # plan name (case-insensitive) → default credits
    "starter": 20,
    "pro":     100,
    "team":    500,
}

# Columns — must match the sheet headers exactly
COL_KEY      = "access_key"
COL_CREDITS  = "credits_remaining"
COL_OWNER    = "owner"          # stores email address
COL_PLAN     = "plan"
COL_ISSUED   = "issued_at"      # ISO-8601 timestamp
COL_STATUS   = "status"         # active | revoked

REQUIRED_HEADERS = [COL_KEY, COL_CREDITS, COL_OWNER, COL_PLAN, COL_ISSUED, COL_STATUS]

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]

# ─── ANSI colours (graceful fallback on Windows) ────────────────────────────
def _c(code: str, text: str) -> str:
    if sys.stdout.isatty():
        return f"\033[{code}m{text}\033[0m"
    return text

GREEN  = lambda t: _c("32",   t)
CYAN   = lambda t: _c("36",   t)
YELLOW = lambda t: _c("33",   t)
RED    = lambda t: _c("31",   t)
BOLD   = lambda t: _c("1",    t)
DIM    = lambda t: _c("2",    t)


# ═══════════════════════════════════════════════════════════════════════════
#  GOOGLE SHEETS CONNECTION
# ═══════════════════════════════════════════════════════════════════════════

def _connect() -> gspread.Worksheet:
    sa_path = Path(SERVICE_ACCOUNT_FILE)
    if not sa_path.exists():
        sys.exit(
            RED(f"✗ Service account file not found: {sa_path.resolve()}\n")
            + DIM("  Set DSX_SA_FILE env var or place service_account.json here.")
        )

    if SHEET_ID in ("YOUR_GOOGLE_SHEET_ID_HERE", ""):
        sys.exit(
            RED("✗ SHEET_ID is not configured.\n")
            + DIM("  Edit CONFIG in admin_keys.py or: export DSX_SHEET_ID=your-id")
        )

    creds = Credentials.from_service_account_file(str(sa_path), scopes=SCOPES)

    # ✅ FIX: proper client initialization
    gc = gspread.authorize(creds)

    sh = gc.open_by_key(SHEET_ID)

    try:
        ws = sh.worksheet(SHEET_TAB)
    except gspread.WorksheetNotFound:
        print(YELLOW(f"⚠  Tab '{SHEET_TAB}' not found — creating it…"))
        ws = sh.add_worksheet(title=SHEET_TAB, rows=1000, cols=len(REQUIRED_HEADERS))
        ws.append_row(REQUIRED_HEADERS)
        _format_header(ws)
        print(GREEN(f"✓  Tab '{SHEET_TAB}' created with headers."))

    _ensure_headers(ws)
    return ws


def _ensure_headers(ws: gspread.Worksheet):
    """Create header row if missing; add any missing columns to the right."""
    existing = ws.row_values(1)
    if not existing:
        ws.append_row(REQUIRED_HEADERS)
        _format_header(ws)
        return
    missing = [h for h in REQUIRED_HEADERS if h not in existing]
    if missing:
        # existing length is stable — compute next col index before adding any columns
        next_col = len(existing) + 1
        ws.add_cols(len(missing))
        for offset, col_name in enumerate(missing):
            ws.update_cell(1, next_col + offset, col_name)
        print(YELLOW(f"⚠  Added missing columns: {missing}"))


def _format_header(ws: gspread.Worksheet):
    """Bold + freeze the header row."""
    try:
        ws.format("1:1", {"textFormat": {"bold": True}})
        ws.freeze(rows=1)
    except Exception:
        pass   # non-critical


def _all_records(ws: gspread.Worksheet) -> tuple[list[dict], list[str]]:
    """Return (records, header) with header preserved for index lookups."""
    header  = ws.row_values(1)
    records = ws.get_all_records(expected_headers=REQUIRED_HEADERS)
    return records, header


# ═══════════════════════════════════════════════════════════════════════════
#  KEY GENERATION
# ═══════════════════════════════════════════════════════════════════════════

def _generate_key(existing_keys: set[str]) -> str:
    """
    Generate a unique DSX-XXXX-XXXX-XXXX key.
    Each segment is 4 uppercase alphanumeric characters (ambiguous chars removed).
    """
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"   # no 0/O/I/1
    for _ in range(1_000):
        seg = lambda: "".join(random.choices(alphabet, k=4))
        key = f"DSX-{seg()}-{seg()}-{seg()}"
        if key not in existing_keys:
            return key
    sys.exit(RED("✗ Could not generate a unique key after 1000 attempts."))


def _validate_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))




# ═══════════════════════════════════════════════════════════════════════════
#  COMMANDS
# ═══════════════════════════════════════════════════════════════════════════

def cmd_issue(args):
    email   = args.email.strip().lower()
    plan    = args.plan.strip()
    plan_lc = plan.lower()

    if not _validate_email(email):
        sys.exit(RED(f"✗ '{email}' doesn't look like a valid email address."))

    # Resolve credits: CLI flag overrides plan default
    if args.credits is not None:
        credits = args.credits
    elif plan_lc in PLAN_DEFAULTS:
        credits = PLAN_DEFAULTS[plan_lc]
    else:
        sys.exit(
            RED(f"✗ Unknown plan '{plan}'.")
            + f"\n  Known plans: {', '.join(PLAN_DEFAULTS.keys())}"
            + "\n  Or pass --credits N to set manually."
        )

    ws = _connect()
    records, _ = _all_records(ws)
    existing_keys   = {r[COL_KEY] for r in records}
    existing_emails = {r[COL_OWNER].lower() for r in records if r.get(COL_STATUS) == "active"}

    # Warn if email already has an active key (don't block — top-up path is separate)
    if email in existing_emails:
        print(YELLOW(f"⚠  {email} already has an active key. Issuing a new one anyway."))

    key       = _generate_key(existing_keys)
    issued_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    new_row   = [key, credits, email, plan, issued_at, "active"]

    ws.append_row(new_row, value_input_option="USER_ENTERED")

    print()
    print(BOLD("  ✓  Key issued successfully"))
    print()
    print(f"  {'Key':<18}  {CYAN(key)}")
    print(f"  {'Email':<18}  {email}")
    print(f"  {'Plan':<18}  {plan}")
    print(f"  {'Credits':<18}  {GREEN(str(credits))}")
    print(f"  {'Issued at':<18}  {issued_at}")
    print()
    print(DIM("  Send the key above to the customer. They enter it on the DataSynthX landing page."))
    print()


def cmd_topup(args):
    key     = args.key.strip().upper()
    add     = args.credits

    if add <= 0:
        sys.exit(RED("✗ --credits must be a positive integer."))

    ws = _connect()
    records, header = _all_records(ws)
    credits_col_idx = header.index(COL_CREDITS) + 1

    for i, row in enumerate(records):
        if row.get(COL_KEY, "").strip().upper() == key:
            if row.get(COL_STATUS) == "revoked":
                sys.exit(RED(f"✗ Key {key} is revoked. Reinstate it first."))
            row_number  = i + 2
            current     = int(row.get(COL_CREDITS, 0))
            new_balance = current + add
            ws.update_cell(row_number, credits_col_idx, new_balance)
            print()
            print(BOLD(f"  ✓  Credits added to {CYAN(key)}"))
            print()
            print(f"  {'Owner':<18}  {row.get(COL_OWNER)}")
            print(f"  {'Plan':<18}  {row.get(COL_PLAN)}")
            print(f"  {'Previous balance':<18}  {current}")
            print(f"  {'Added':<18}  +{add}")
            print(f"  {'New balance':<18}  {GREEN(str(new_balance))}")
            print()
            return

    sys.exit(RED(f"✗ Key not found: {key}"))


def cmd_list(args):
    ws = _connect()
    records, _ = _all_records(ws)

    if not records:
        print(YELLOW("  No keys found in the sheet."))
        return

    # Optional filter
    plan_filter   = args.plan.lower()  if args.plan   else None
    status_filter = args.status.lower() if args.status else None

    rows = []
    for r in records:
        if plan_filter   and r.get(COL_PLAN,   "").lower() != plan_filter:   continue
        if status_filter and r.get(COL_STATUS,  "").lower() != status_filter: continue

        status = r.get(COL_STATUS, "active")
        cred   = r.get(COL_CREDITS, 0)

        status_fmt = GREEN("active")  if status == "active"  else RED("revoked")
        cred_fmt   = (GREEN(str(cred)) if int(cred) > 10
                      else YELLOW(str(cred)) if int(cred) > 0
                      else RED(str(cred)))

        rows.append([
            CYAN(r.get(COL_KEY, "")),
            r.get(COL_OWNER, ""),
            r.get(COL_PLAN, ""),
            cred_fmt,
            status_fmt,
            r.get(COL_ISSUED, "")[:10],   # date only
        ])

    headers = [BOLD("Access Key"), BOLD("Email"), BOLD("Plan"),
               BOLD("Credits"), BOLD("Status"), BOLD("Issued")]
    print()
    print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    print(DIM(f"\n  {len(rows)} key(s) shown."))
    print()


def cmd_info(args):
    key = args.key.strip().upper()
    ws  = _connect()
    records, _ = _all_records(ws)

    for r in records:
        if r.get(COL_KEY, "").strip().upper() == key:
            status = r.get(COL_STATUS, "active")
            cred   = int(r.get(COL_CREDITS, 0))

            status_fmt = GREEN("active") if status == "active" else RED("revoked")
            cred_fmt   = (GREEN(str(cred)) if cred > 10
                          else YELLOW(str(cred)) if cred > 0
                          else RED("0  ← no credits remaining"))
            print()
            print(BOLD(f"  Key info: {CYAN(key)}"))
            print()
            print(f"  {'Email':<20}  {r.get(COL_OWNER)}")
            print(f"  {'Plan':<20}  {r.get(COL_PLAN)}")
            print(f"  {'Credits remaining':<20}  {cred_fmt}")
            print(f"  {'Status':<20}  {status_fmt}")
            print(f"  {'Issued at':<20}  {r.get(COL_ISSUED)}")
            print()
            return

    sys.exit(RED(f"✗ Key not found: {key}"))


def cmd_revoke(args):
    key = args.key.strip().upper()
    ws  = _connect()
    records, header = _all_records(ws)
    status_col_idx  = header.index(COL_STATUS) + 1

    for i, row in enumerate(records):
        if row.get(COL_KEY, "").strip().upper() == key:
            if row.get(COL_STATUS) == "revoked":
                print(YELLOW(f"  ⚠  Key {key} is already revoked."))
                return
            row_number = i + 2
            ws.update_cell(row_number, status_col_idx, "revoked")
            print()
            print(RED(BOLD(f"  ✓  Key {key} has been revoked.")))
            print(DIM(f"  Owner: {row.get(COL_OWNER)}  |  Plan: {row.get(COL_PLAN)}"))
            print()
            return

    sys.exit(RED(f"✗ Key not found: {key}"))


def cmd_reinstate(args):
    key = args.key.strip().upper()
    ws  = _connect()
    records, header = _all_records(ws)
    status_col_idx  = header.index(COL_STATUS) + 1

    for i, row in enumerate(records):
        if row.get(COL_KEY, "").strip().upper() == key:
            if row.get(COL_STATUS) == "active":
                print(YELLOW(f"  ⚠  Key {key} is already active."))
                return
            row_number = i + 2
            ws.update_cell(row_number, status_col_idx, "active")
            print()
            print(GREEN(BOLD(f"  ✓  Key {key} reinstated to active.")))
            print(DIM(f"  Owner: {row.get(COL_OWNER)}  |  Credits: {row.get(COL_CREDITS)}"))
            print()
            return

    sys.exit(RED(f"✗ Key not found: {key}"))


# ═══════════════════════════════════════════════════════════════════════════
#  CLI ENTRYPOINT
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        prog="admin_keys.py",
        description=BOLD("DataSynthX — Admin Key Management"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python admin_keys.py issue  --email alice@example.com --plan Pro
  python admin_keys.py issue  --email bob@example.com   --plan Starter --credits 50
  python admin_keys.py topup  --key DSX-AB12-CD34-EF56  --credits 100
  python admin_keys.py list
  python admin_keys.py list   --plan Pro --status active
  python admin_keys.py info   --key DSX-AB12-CD34-EF56
  python admin_keys.py revoke --key DSX-AB12-CD34-EF56
        """,
    )
    sub = parser.add_subparsers(dest="command", metavar="command")
    sub.required = True

    # ── issue ────────────────────────────────────────────────────────────────
    p_issue = sub.add_parser("issue", help="Issue a new access key to a customer")
    p_issue.add_argument("--email",   required=True,  help="Customer email address")
    p_issue.add_argument("--plan",    required=True,  help="Plan name: Starter | Pro | Team")
    p_issue.add_argument("--credits", type=int, default=None,
                         help="Override default credits for the plan")
    p_issue.set_defaults(func=cmd_issue)

    # ── topup ────────────────────────────────────────────────────────────────
    p_topup = sub.add_parser("topup", help="Add credits to an existing key")
    p_topup.add_argument("--key",     required=True, help="Access key (DSX-XXXX-XXXX-XXXX)")
    p_topup.add_argument("--credits", required=True, type=int, help="Credits to add")
    p_topup.set_defaults(func=cmd_topup)

    # ── list ─────────────────────────────────────────────────────────────────
    p_list = sub.add_parser("list", help="List all keys (with optional filters)")
    p_list.add_argument("--plan",   default=None, help="Filter by plan name")
    p_list.add_argument("--status", default=None, help="Filter by status: active | revoked")
    p_list.set_defaults(func=cmd_list)

    # ── info ─────────────────────────────────────────────────────────────────
    p_info = sub.add_parser("info", help="Show full details for one key")
    p_info.add_argument("--key", required=True, help="Access key (DSX-XXXX-XXXX-XXXX)")
    p_info.set_defaults(func=cmd_info)

    # ── revoke ───────────────────────────────────────────────────────────────
    p_revoke = sub.add_parser("revoke", help="Revoke a key (blocks login, keeps row)")
    p_revoke.add_argument("--key", required=True, help="Access key (DSX-XXXX-XXXX-XXXX)")
    p_revoke.set_defaults(func=cmd_revoke)

    # ── reinstate ────────────────────────────────────────────────────────────
    p_reinstate = sub.add_parser("reinstate", help="Re-activate a previously revoked key")
    p_reinstate.add_argument("--key", required=True, help="Access key (DSX-XXXX-XXXX-XXXX)")
    p_reinstate.set_defaults(func=cmd_reinstate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
