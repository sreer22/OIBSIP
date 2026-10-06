# Advanced SQL Injection Exercise (Local DVWA Only)

## Executive summary

This exercise studies SQL injection in **DVWA, a deliberately vulnerable training application**. If a similar defect exists in a business application, an attacker may read data beyond their authorization, expose personal or confidential records, or disrupt database-backed services. The business risk can include incident response costs, operational downtime, legal obligations, regulatory consequences, and loss of customer trust. The practical risk depends on the affected application, reachable database privileges, data sensitivity, and external exposure.

**Risk in the intentionally vulnerable lab: High.** DVWA is built to be vulnerable and must remain isolated. This rating describes the lab’s deliberate configuration, not a finding about any production system. Never expose DVWA or use the included exercise against systems you do not own or have written authorization to test.

## Scope and status

- Target scope: only a DVWA instance bound to this machine (`127.0.0.1` or `localhost`).
- Intended module: **SQL Injection**, security level **Medium**, database backend **MySQL/MariaDB**.
- The official DVWA Medium source constructs a numeric `user_id` query without quoting the value. It calls `mysqli_real_escape_string`, but that is not a substitute for parameter binding; numeric SQL syntax can still be injected.
- DVWA's SQL Injection module is a record lookup, **not a login form**. It does not provide a login-authentication-bypass result. Do not report an authentication bypass as successful based on this page. The broad-result test below demonstrates unauthorized record enumeration in the lab instead.
- **Execution status: not run.** No endpoint URL or Burp evidence was supplied in this session. No live request was sent, no sqlmap scan was run, and no response output or screenshot has been fabricated. Fill in the results report only after recording actual observations.

## Set up the lab safely

1. Use the current official [DVWA project](https://github.com/digininja/DVWA) and follow its setup documentation.
2. Run it on a local machine or isolated VM; bind the web service to loopback or use host-only/NAT networking that does not expose it to the public Internet.
3. Log in to DVWA, use **DVWA Security** to select **Medium**, and reset/create the lab database if the setup page requires it.
4. Open the **SQL Injection** page, not a login screen. Confirm the configured database is MySQL/MariaDB before using the schema-enumeration examples below. SQLite-backed instances use different metadata syntax.
5. Record the exact local base URL, DVWA revision, backend, and security level in `exploit_report.md`.

Do not use real credentials or real data in the lab. Keep the browser and any interception proxy limited to the local DVWA origin.

## Manual exercise

Run `sql_injection_exploit.sh` to print the lab-scope reminder. The script intentionally sends **no HTTP requests**; use the DVWA form and Burp Repeater manually.

On DVWA's SQL Injection page, submit each value in the **User ID** field and record the exact response:

1. Baseline: `1`
2. Predicate expansion: `1 OR 1=1`
3. MySQL/MariaDB table-name enumeration:
   `1 UNION SELECT table_name, table_schema FROM information_schema.tables WHERE table_schema=database()`
4. MySQL/MariaDB column-name enumeration for the DVWA `users` table:
   `1 UNION SELECT table_name, column_name FROM information_schema.columns WHERE table_schema=database() AND table_name='users'`

The DVWA Medium query selects two output columns (`first_name`, `last_name`), so each `UNION SELECT` example also selects two expressions. If this local DVWA version, database backend, or server SQL mode produces a different result, document what actually happened; do not silently alter the recorded payload or claim an expected result was observed. The page’s ordinary baseline and injected results are rendered as `ID`, `First name`, and `Surname` entries. Capture the actual rows and errors in the report.

### Authentication-bypass requirement

The requested authentication-bypass step is **not applicable to the chosen DVWA SQL Injection form**: its vulnerable input selects user records and is not used to authenticate a session. This project records that distinction instead of inventing a successful login bypass. If the course requires an authentication-bypass demonstration, use a separate, deliberately vulnerable login lab that you own, and document that target and authorization independently.

### Burp evidence

1. Start Burp Suite and use its built-in browser, or configure a browser proxy, without changing the DVWA target from localhost.
2. Enable interception and submit the baseline and a test value through DVWA.
3. In Proxy history, select the request to the local SQL Injection page. Confirm the host is loopback before sending it to Repeater.
4. Save a screenshot showing the local request and the corresponding lab response. Redact cookies/session tokens before storing or sharing it.
5. Add the screenshot under `evidence/` and record its filename and test case in `exploit_report.md`.

No screenshot is included until an actual local request has been captured.

### Optional sqlmap comparison

sqlmap is not run by the supplied script. If you separately use it, keep it on the local DVWA page, use only your own DVWA session, start with a non-destructive enumeration request, and record the exact command, version, session handling, findings, and output in `exploit_report.md`. Never target an address that is not loopback. Do not run database modification, file access, operating-system takeover, or data-dumping options for this exercise.

## Remediation

The underlying defect occurs when an application combines SQL syntax with user input to assemble a query. Escaping is context-sensitive and easy to misuse. DVWA Medium escapes the input but inserts it as an unquoted numeric expression, so SQL syntax remains possible. **Use parameterized/prepared queries** so the database treats supplied values as data, not executable SQL. Validate input for business rules as an additional control, not as a replacement for binding parameters.

### Python (`sqlite3`)

```python
import sqlite3

def find_user(connection: sqlite3.Connection, user_id: int):
    row = connection.execute(
        "SELECT first_name, last_name FROM users WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    return row
```

The placeholder is part of the fixed SQL statement; the parameter value is bound separately. For another database driver, use that driver's documented parameter placeholder syntax.

### PHP (`mysqli`)

```php
<?php
function findUser(mysqli $db, int $userId): ?array
{
    $stmt = $db->prepare(
        'SELECT first_name, last_name FROM users WHERE user_id = ?'
    );
    $stmt->bind_param('i', $userId);
    $stmt->execute();

    $result = $stmt->get_result();
    $row = $result->fetch_assoc();
    $stmt->close();

    return $row ?: null;
}
```

Use a database account with only the privileges the application needs, avoid returning database errors or internal details to end users, and log security-relevant failures without logging secrets. These measures reduce impact and improve detection but do not replace parameterized queries.

## Files

- `exploit_report.md` — results/evidence template; complete it with observations from the local run.
- `sql_injection_exploit.sh` — safe scope reminder and commented manual test notes; it does not execute payloads.

## References

- [Official DVWA repository and safety guidance](https://github.com/digininja/DVWA)
- [DVWA Medium SQL Injection source](https://github.com/digininja/DVWA/blob/master/vulnerabilities/sqli/source/medium.php)
- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [PortSwigger Web Security Academy: SQL injection](https://portswigger.net/web-security/sql-injection)
- [Python `sqlite3`: placeholders for bound values](https://docs.python.org/3/library/sqlite3.html#how-to-use-placeholders-to-bind-values-in-sql-queries)
- [PHP `mysqli`: prepared statements](https://www.php.net/manual/en/mysqli.quickstart.prepared-statements.php)
