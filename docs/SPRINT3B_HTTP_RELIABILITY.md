# SPRINT 3B – HTTP Reliability & Network Safety Report
**Author:** Lead Software Architect, RAHUUL RADAR  
**Scope:** ONLY `market/paytm_provider.py` (Zero modifications to any other file)  
**Status:** Complete  

---

## Executive Summary
In accordance with Sprint 3B architectural guidelines and strict single-file isolation rules, every HTTP network request within `market/paytm_provider.py` has been audited and upgraded to enforce explicit network timeouts. By establishing a centralized class-level timeout constant (`DEFAULT_HTTP_TIMEOUT = 5.0`) and eliminating unbounded socket waits across all GET and POST requests, the provider architecture now actively prevents hanging threads, socket deadlocks, and cascading application lockups during network degradation or broker downtime. All existing business logic, payload structures, request headers, endpoints, retry loops, authentication protocols, and exception handling behavior have been preserved with 100% fidelity.

---

## Files Changed
* **`market/paytm_provider.py`** *(Sole file modified in Sprint 3B)*
  * Added central constant `DEFAULT_HTTP_TIMEOUT = 5.0` to the `PaytmMoneyProvider` class definition.
  * Updated constructor (`__init__`) to accept an optional `timeout: float = None`, dynamically falling back to the `PAYTM_HTTP_TIMEOUT` environment variable, the `http_timeout` setting in `config.json`, or the central constant `DEFAULT_HTTP_TIMEOUT`.
  * Applied explicit `timeout=self.timeout` parameter across all 10 occurrences of `requests.get()` and `requests.post()`.
  * No other files in the project repository were touched.

---

## HTTP Calls Updated
Every single HTTP network call across the provider module was audited and injected with the centralized timeout parameter:

| Line Number | Provider Method | HTTP Verb & API Endpoint | Timeout Parameter Added |
| :--- | :--- | :--- | :--- |
| **L116** | `connect()` | `POST /accounts/v2/gettoken` | `timeout=self.timeout` |
| **L210** | `get_last_price()` | `GET /data/v1/price/live` (LTP quote) | `timeout=self.timeout` |
| **L218** | `get_last_price()` *(401 Retry)* | `GET /data/v1/price/live` (LTP quote retry) | `timeout=self.timeout` |
| **L248** | `test_connection()` | `GET /data/v1/price/live` (Connection probe) | `timeout=self.timeout` |
| **L293** | `pre_cache()` | `GET /data/v1/price/live` (Bulk 40-symbol quote) | `timeout=self.timeout` |
| **L299** | `pre_cache()` *(401 Retry)* | `GET /data/v1/price/live` (Bulk quote retry) | `timeout=self.timeout` |
| **L341** | `get_volume()` | `GET /data/v1/price/live` (Volume quote) | `timeout=self.timeout` |
| **L346** | `get_volume()` *(401 Retry)* | `GET /data/v1/price/live` (Volume quote retry) | `timeout=self.timeout` |
| **L379** | `get_option_chain()` | `GET /data/fno/v1/option-chain` (F&O option series) | `timeout=self.timeout` |
| **L384** | `get_option_chain()` *(401 Retry)* | `GET /data/fno/v1/option-chain` (Option chain retry)| `timeout=self.timeout` |

---

## Timeout Strategy

### Central Constant vs. Hardcoded Dispersion
To adhere strictly to Clean Architecture principles and eliminate scattered magic numbers, all network executions inherit their timeout bound from a single central source of truth:
```python
DEFAULT_HTTP_TIMEOUT = 5.0
```
Rather than hardcoding arbitrary float numbers across individual request calls, the instance property `self.timeout` initializes directly from this constant while maintaining full configuration extensibility.

### Configurable Override Hierarchy
When `PaytmMoneyProvider` is instantiated, its explicit HTTP timeout bound resolves via a robust 4-level precedence cascade:
1. **Explicit Constructor Argument:** If a developer or scanner injects a timeout directly during instantiation (`PaytmMoneyProvider(timeout=2.5)`), this value takes top priority.
2. **Environment Variable Overwrite:** Operating system environment variables check for `PAYTM_HTTP_TIMEOUT` (e.g., `export PAYTM_HTTP_TIMEOUT=3.0`), enabling container and cloud runtime configuration without file edits.
3. **Application Config Resolution:** If neither of the above is provided, `_load_credentials_from_config()` inspects the `"paytm"` configuration block in `config.json` for an optional `"http_timeout"` numeric entry.
4. **Central Default Constant:** If all configuration layers are unspecified, `self.timeout` binds safely to `self.DEFAULT_HTTP_TIMEOUT` (5.0 seconds).

---

## Compatibility Verification
* **Zero Architecture Modifications:** No asynchronous programming models (`asyncio`, `aiohttp`), background threads (`ThreadPool`, `ThreadPoolExecutor`), or third-party circuit-breaking libraries were introduced into the provider layer.
* **100% Request Payload & Header Integrity:** All JWT token transmission headers (`{"x-jwt-token": jwt_token}`), parameter dictionaries (`mode`, `pref`, `symbol`, `expiry`), and JSON authentication bodies (`api_key`, `api_secret_key`, `requestToken`) remain identical byte-for-byte.
* **Preserved Business & Exception Handling Logic:** When an explicit timeout occurs during execution, `requests.exceptions.Timeout` (a subclass of `requests.exceptions.RequestException`) is intercepted natively by the existing `try...except Exception as e:` catch blocks. Error logs are emitted without application termination, and appropriate default structures (`0.0` prices, `0` volumes, empty sets `{}`) or automated fallbacks to `YahooFinanceProvider` execute precisely as originally designed.

---

## Validation Steps

### 1. Static AST and Pattern Inspection
* Executed regular expression searches (`requests\.(get|post)`) across `market/paytm_provider.py`. Confirmed exactly 10 matching target lines exist, and 100% of these calls explicitly include `timeout=self.timeout`.
* Confirmed no additional files or external modules outside `market/paytm_provider.py` were edited during this sprint.

### 2. Provider Unit and Verification Testing
* Tested provider instantiation and central constant exposure inside the dedicated project virtual environment (`.venv/bin/python3`). Confirmed `PaytmMoneyProvider.DEFAULT_HTTP_TIMEOUT == 5.0`.
* Ran existing test suites via `pytest tests/ -v`. Verified provider methods cleanly trigger scheduled exception handlers (such as raising initial validation errors on missing credentials per Sprint 1 rules or logging 400 Client Error responses on mock connection attempts) without encountering runtime attribute failures or structural regressions.

---

## Rollback Plan
If an unanticipated network routing setup (e.g., extremely high-latency VPN tunnels or ultra-slow proxy gateways) necessitates removing explicit timeout restraints from the provider API, follow this direct 4-step revert procedure:

1. **Remove Central Constant & Constructor Parameter:**
   Open `market/paytm_provider.py` and strip `DEFAULT_HTTP_TIMEOUT = 5.0`, returning `__init__` to its original parameterless signature:
   ```python
   # Change from:
   DEFAULT_HTTP_TIMEOUT = 5.0
   def __init__(self, timeout: float = None):
       ...
       self.timeout = float(...)
       
   # Revert back to:
   def __init__(self):
       ...
   ```
2. **Remove Config Parser Overlay:**
   In `_load_credentials_from_config()`, delete the lines checking for `"http_timeout"` inside `paytm_block`.
3. **Strip Timeout Arguments from HTTP Requests:**
   Execute a bulk deletion removing the trailing `, timeout=self.timeout` argument from all 10 occurrences of `requests.get` and `requests.post` across `connect`, `get_last_price`, `test_connection`, `pre_cache`, `get_volume`, and `get_option_chain`.
4. **Version Control Reset:**
   Alternatively, restore `market/paytm_provider.py` to its exact pre-Sprint 3B commit state via Git:
   ```bash
   git checkout -- market/paytm_provider.py
   ```

---
*Report certified by Lead Software Architect for RAHUUL RADAR.*
