#!/usr/bin/env bash
# ==============================================================================
# Isolated Regression Test Suite for scripts/auto_update_cron.sh
# ==============================================================================
# Verifies all 12 safety requirements against isolated temporary fixtures.
# Never calls production servers, never runs against real working repository.
# ==============================================================================
set -eo pipefail

TEST_ROOT=$(mktemp -d /tmp/auto_update_test_root_XXXXXX)
trap 'rm -rf "$TEST_ROOT"' EXIT

SCRIPT_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/scripts/auto_update_cron.sh"
PYTHON_BIN="$(which python3)"

PASSED_COUNT=0
TOTAL_COUNT=18

log_test() {
    echo "======================================================================"
    echo "TEST $1: $2"
    echo "======================================================================"
}

assert_true() {
    if ! eval "$1"; then
        echo "❌ ASSERTION FAILED: $1"
        exit 1
    fi
}

assert_equals() {
    if [ "$1" != "$2" ]; then
        echo "❌ ASSERTION FAILED: '$1' != '$2'"
        exit 1
    fi
}

# Helper to build a clean mock fixture
setup_fixture() {
    local fixture_dir="$1"
    mkdir -p "$fixture_dir"

    # 1. Bare remote repository
    git init --bare "$fixture_dir/remote.git" >/dev/null 2>&1

    # 2. Seed remote with initial commit on dev branch
    local init_clone="$fixture_dir/init_clone"
    git clone "$fixture_dir/remote.git" "$init_clone" >/dev/null 2>&1
    (
        cd "$init_clone"
        git checkout -b dev >/dev/null 2>&1
        echo "initial" > version.txt
        mkdir -p data
        # Create small valid sqlite databases
        "$PYTHON_BIN" -c "import sqlite3; c=sqlite3.connect('data/live_journal.db'); c.execute('CREATE TABLE t(x);'); c.commit(); c.close()"
        "$PYTHON_BIN" -c "import sqlite3; c=sqlite3.connect('data/radar.db'); c.execute('CREATE TABLE t(x);'); c.commit(); c.close()"
        "$PYTHON_BIN" -c "import sqlite3; c=sqlite3.connect('radar.db'); c.execute('CREATE TABLE t(x);'); c.commit(); c.close()"
        git add . >/dev/null 2>&1
        git commit -m "init" >/dev/null 2>&1
        git push origin dev >/dev/null 2>&1
    )
    rm -rf "$init_clone"

    # 3. Downstream production checkout
    local repo_dir="$fixture_dir/repo"
    git clone -b dev "$fixture_dir/remote.git" "$repo_dir" >/dev/null 2>&1
    mkdir -p "$repo_dir/scripts" "$repo_dir/logs" "$repo_dir/venv/bin"
    cp "$SCRIPT_SRC" "$repo_dir/scripts/auto_update_cron.sh"
    chmod +x "$repo_dir/scripts/auto_update_cron.sh"

    # Mock python in venv that delegates to real python3
    ln -s "$PYTHON_BIN" "$repo_dir/venv/bin/python"

    # 4. Mock bin for systemctl and curl
    mkdir -p "$fixture_dir/bin"

    # Mock systemctl
    cat << 'MOCK_SYS' > "$fixture_dir/bin/systemctl"
#!/usr/bin/env bash
echo "$@" >> "$MOCK_SYS_LOG"
if [ "$SYSTEMCTL_FAILS" = "1" ]; then
    exit 1
fi
if [ "$1" = "is-active" ]; then
    if [ "$SYSTEMCTL_INACTIVE" = "1" ]; then
        exit 1
    fi
    exit 0
fi
exit 0
MOCK_SYS
    chmod +x "$fixture_dir/bin/systemctl"

    # Mock curl
    cat << 'MOCK_CURL' > "$fixture_dir/bin/curl"
#!/usr/bin/env bash
echo "$@" >> "$MOCK_CURL_LOG"
if [ "$CURL_FAILS" = "1" ]; then
    echo "Connection refused"
    exit 1
fi
echo '{"status":"online","application_health":"HEALTHY"}'
exit 0
MOCK_CURL
    chmod +x "$fixture_dir/bin/curl"
}

# ------------------------------------------------------------------------------
# TEST 1: No-update path exits without restarting service
# ------------------------------------------------------------------------------
log_test 1 "No-update path exits without restarting the service"
F1="$TEST_ROOT/f1"
setup_fixture "$F1"
(
    cd "$F1/repo"
    export PATH="$F1/bin:$PATH"
    export MOCK_SYS_LOG="$F1/systemctl.log"
    export MOCK_CURL_LOG="$F1/curl.log"
    export SYSTEMCTL_CMD="$F1/bin/systemctl"
    export AUTO_UPDATE_LOCK_FILE="$F1/lock"
    export AUTO_UPDATE_BACKUP_DIR="$F1/backups"

    bash scripts/auto_update_cron.sh
    assert_true "[ ! -f '$F1/systemctl.log' ]"
    assert_true "grep -q 'System is already up to date' logs/auto_update.log"
)
PASSED_COUNT=$((PASSED_COUNT + 1))
echo "✅ Test 1 Passed"

# ------------------------------------------------------------------------------
# TEST 2: Valid fast-forward follows intended sequence
# ------------------------------------------------------------------------------
log_test 2 "Valid fast-forward follows the intended sequence"
F2="$TEST_ROOT/f2"
setup_fixture "$F2"
# Push update to remote
CLONE2="$F2/push_clone"
git clone -b dev "$F2/remote.git" "$CLONE2" >/dev/null 2>&1
(
    cd "$CLONE2"
    echo "v2" >> version.txt
    git commit -am "feat: update to v2" >/dev/null 2>&1
    git push origin dev >/dev/null 2>&1
)
(
    cd "$F2/repo"
    export PATH="$F2/bin:$PATH"
    export MOCK_SYS_LOG="$F2/systemctl.log"
    export MOCK_CURL_LOG="$F2/curl.log"
    export SYSTEMCTL_CMD="$F2/bin/systemctl"
    export AUTO_UPDATE_LOCK_FILE="$F2/lock"
    export AUTO_UPDATE_BACKUP_DIR="$F2/backups"

    bash scripts/auto_update_cron.sh

    assert_true "grep -q 'restart rahuul_radar.service' '$F2/systemctl.log'"
    assert_true "grep -q 'is-active --quiet rahuul_radar.service' '$F2/systemctl.log'"
    assert_true "grep -q 'verified HEALTHY' logs/auto_update.log"
    assert_equals "$(cat version.txt)" "initial
v2"
)
PASSED_COUNT=$((PASSED_COUNT + 1))
echo "✅ Test 2 Passed"

# ------------------------------------------------------------------------------
# TEST 3: Non-fast-forward update is refused
# ------------------------------------------------------------------------------
log_test 3 "Non-fast-forward update is refused"
F3="$TEST_ROOT/f3"
setup_fixture "$F3"
# Create divergent commit on local repo
(
    cd "$F3/repo"
    echo "local-diverge" >> version.txt
    git commit -am "local divergence" >/dev/null 2>&1
)
# Create divergent commit on remote
CLONE3="$F3/push_clone"
git clone -b dev "$F3/remote.git" "$CLONE3" >/dev/null 2>&1
(
    cd "$CLONE3"
    echo "remote-diverge" >> remote.txt
    git add . >/dev/null 2>&1
    git commit -m "remote divergence" >/dev/null 2>&1
    git push origin dev >/dev/null 2>&1
)
(
    cd "$F3/repo"
    export PATH="$F3/bin:$PATH"
    export MOCK_SYS_LOG="$F3/systemctl.log"
    export MOCK_CURL_LOG="$F3/curl.log"
    export SYSTEMCTL_CMD="$F3/bin/systemctl"
    export AUTO_UPDATE_LOCK_FILE="$F3/lock"
    export AUTO_UPDATE_BACKUP_DIR="$F3/backups"

    set +e
    bash scripts/auto_update_cron.sh
    res=$?
    set -e
    assert_true "[ $res -ne 0 ]"
    assert_true "grep -q 'not a fast-forward descendant' logs/auto_update.log"
    assert_true "[ ! -f '$F3/systemctl.log' ]"
)
PASSED_COUNT=$((PASSED_COUNT + 1))
echo "✅ Test 3 Passed"

# ------------------------------------------------------------------------------
# TEST 4: Modified database state is preserved if incoming commit does not touch it
# ------------------------------------------------------------------------------
log_test 4 "Modified database state is preserved if incoming commit does not touch that path"
F4="$TEST_ROOT/f4"
setup_fixture "$F4"
# Simulate runtime mutation on local data/radar.db
(
    cd "$F4/repo"
    "$PYTHON_BIN" -c "import sqlite3; c=sqlite3.connect('data/radar.db'); c.execute('INSERT INTO t VALUES (999);'); c.commit(); c.close()"
)
# Remote updates unrelated file
CLONE4="$F4/push_clone"
git clone -b dev "$F4/remote.git" "$CLONE4" >/dev/null 2>&1
(
    cd "$CLONE4"
    echo "code update" > new_feature.py
    git add new_feature.py >/dev/null 2>&1
    git commit -m "new feature" >/dev/null 2>&1
    git push origin dev >/dev/null 2>&1
)
(
    cd "$F4/repo"
    export PATH="$F4/bin:$PATH"
    export MOCK_SYS_LOG="$F4/systemctl.log"
    export MOCK_CURL_LOG="$F4/curl.log"
    export SYSTEMCTL_CMD="$F4/bin/systemctl"
    export AUTO_UPDATE_LOCK_FILE="$F4/lock"
    export AUTO_UPDATE_BACKUP_DIR="$F4/backups"

    bash scripts/auto_update_cron.sh
    # Check that runtime database record 999 remains intact
    db_val=$("$PYTHON_BIN" -c "import sqlite3; c=sqlite3.connect('data/radar.db'); print(c.execute('SELECT x FROM t').fetchone()[0]); c.close()")
    assert_equals "$db_val" "999"
    assert_true "[ -f new_feature.py ]"
)
PASSED_COUNT=$((PASSED_COUNT + 1))
echo "✅ Test 4 Passed"

# ------------------------------------------------------------------------------
# TEST 5: Conflicting incoming change is refused
# ------------------------------------------------------------------------------
log_test 5 "Incoming change that conflicts with modified or untracked local state is refused"
F5="$TEST_ROOT/f5"
setup_fixture "$F5"
# Local modifies tracked version.txt without committing
(
    cd "$F5/repo"
    echo "local uncommitted edit" >> version.txt
)
# Remote also modifies version.txt
CLONE5="$F5/push_clone"
git clone -b dev "$F5/remote.git" "$CLONE5" >/dev/null 2>&1
(
    cd "$CLONE5"
    echo "remote conflicting edit" >> version.txt
    git commit -am "remote conflict" >/dev/null 2>&1
    git push origin dev >/dev/null 2>&1
)
(
    cd "$F5/repo"
    export PATH="$F5/bin:$PATH"
    export MOCK_SYS_LOG="$F5/systemctl.log"
    export MOCK_CURL_LOG="$F5/curl.log"
    export SYSTEMCTL_CMD="$F5/bin/systemctl"
    export AUTO_UPDATE_LOCK_FILE="$F5/lock"
    export AUTO_UPDATE_BACKUP_DIR="$F5/backups"

    set +e
    bash scripts/auto_update_cron.sh
    res=$?
    set -e
    assert_true "[ $res -ne 0 ]"
    assert_true "grep -q 'conflicts with local' logs/auto_update.log"
    # Working tree preserved
    assert_true "grep -q 'local uncommitted edit' version.txt"
)
PASSED_COUNT=$((PASSED_COUNT + 1))
echo "✅ Test 5 Passed"

# ------------------------------------------------------------------------------
# TEST 6: Overlapping updater execution is prevented by lock
# ------------------------------------------------------------------------------
log_test 6 "Overlapping updater execution is prevented by lock"
F6="$TEST_ROOT/f6"
setup_fixture "$F6"
(
    cd "$F6/repo"
    export PATH="$F6/bin:$PATH"
    export AUTO_UPDATE_LOCK_FILE="$F6/lock"

    # Pre-acquire the lock
    mkdir -p "${AUTO_UPDATE_LOCK_FILE}.lockdir"

    bash scripts/auto_update_cron.sh
    assert_true "grep -q 'Auto-update is already running' logs/auto_update.log"

    rmdir "${AUTO_UPDATE_LOCK_FILE}.lockdir"
)
PASSED_COUNT=$((PASSED_COUNT + 1))
echo "✅ Test 6 Passed"

# ------------------------------------------------------------------------------
# TEST 7: SQLite backup failure stops update before fast-forward
# ------------------------------------------------------------------------------
log_test 7 "SQLite backup failure stops the update before fast-forward"
F7="$TEST_ROOT/f7"
setup_fixture "$F7"
# Push remote update
CLONE7="$F7/push_clone"
git clone -b dev "$F7/remote.git" "$CLONE7" >/dev/null 2>&1
(
    cd "$CLONE7"
    echo "v7" >> version.txt
    git commit -am "v7" >/dev/null 2>&1
    git push origin dev >/dev/null 2>&1
)
(
    cd "$F7/repo"
    export PATH="$F7/bin:$PATH"
    export MOCK_SYS_LOG="$F7/systemctl.log"
    export SYSTEMCTL_CMD="$F7/bin/systemctl"
    export AUTO_UPDATE_LOCK_FILE="$F7/lock"
    # Point backup dir to read-only non-creatable path to force failure
    mkdir -p "$F7/readonly_dir"
    chmod 500 "$F7/readonly_dir"
    export AUTO_UPDATE_BACKUP_DIR="$F7/readonly_dir/forbidden_backups"

    set +e
    bash scripts/auto_update_cron.sh
    res=$?
    set -e
    assert_true "[ $res -ne 0 ]"
    assert_true "grep -q 'Pre-update database backup failed' logs/auto_update.log"
    # Git merge was aborted before fast-forward
    assert_true "[ \"$(cat version.txt)\" = 'initial' ]"
    assert_true "[ ! -f '$F7/systemctl.log' ]"
    chmod 700 "$F7/readonly_dir"
)
PASSED_COUNT=$((PASSED_COUNT + 1))
echo "✅ Test 7 Passed"

# ------------------------------------------------------------------------------
# TEST 8: Missing venv/bin/python is reported safely
# ------------------------------------------------------------------------------
log_test 8 "Missing venv/bin/python is reported safely"
F8="$TEST_ROOT/f8"
setup_fixture "$F8"
(
    cd "$F8/repo"
    rm -f venv/bin/python
    export PATH="$F8/bin:$PATH"
    export VENV_PYTHON="$F8/repo/venv/bin/nonexistent_python"
    export AUTO_UPDATE_LOCK_FILE="$F8/lock"

    set +e
    bash scripts/auto_update_cron.sh
    res=$?
    set -e
    assert_true "[ $res -ne 0 ]"
    assert_true "grep -q 'Production Python environment not found or not executable' logs/auto_update.log"
)
PASSED_COUNT=$((PASSED_COUNT + 1))
echo "✅ Test 8 Passed"

# ------------------------------------------------------------------------------
# TEST 9: Sudo restart failure is reported without launching second server
# ------------------------------------------------------------------------------
log_test 9 "Sudo restart failure is reported without launching a second server"
F9="$TEST_ROOT/f9"
setup_fixture "$F9"
# Push remote update
CLONE9="$F9/push_clone"
git clone -b dev "$F9/remote.git" "$CLONE9" >/dev/null 2>&1
(
    cd "$CLONE9"
    echo "v9" >> version.txt
    git commit -am "v9" >/dev/null 2>&1
    git push origin dev >/dev/null 2>&1
)
(
    cd "$F9/repo"
    export PATH="$F9/bin:$PATH"
    export MOCK_SYS_LOG="$F9/systemctl.log"
    export SYSTEMCTL_CMD="$F9/bin/systemctl"
    export SYSTEMCTL_FAILS="1"
    export AUTO_UPDATE_LOCK_FILE="$F9/lock"
    export AUTO_UPDATE_BACKUP_DIR="$F9/backups"

    set +e
    bash scripts/auto_update_cron.sh
    res=$?
    set -e
    assert_true "[ $res -ne 0 ]"
    assert_true "grep -q 'Failed to restart rahuul_radar.service' logs/auto_update.log"
    assert_true "[ -f logs/auto_update_intervention_required ]"
    # Never launches server_supervisor.py
    assert_true "! pgrep -f server_supervisor.py"
)
PASSED_COUNT=$((PASSED_COUNT + 1))
echo "✅ Test 9 Passed"

# ------------------------------------------------------------------------------
# TEST 10: Health-check failure is reported without deleting or resetting data
# ------------------------------------------------------------------------------
log_test 10 "Health-check failure is reported without deleting or resetting data"
F10="$TEST_ROOT/f10"
setup_fixture "$F10"
# Push remote update
CLONE10="$F10/push_clone"
git clone -b dev "$F10/remote.git" "$CLONE10" >/dev/null 2>&1
(
    cd "$CLONE10"
    echo "v10" >> version.txt
    git commit -am "v10" >/dev/null 2>&1
    git push origin dev >/dev/null 2>&1
)
(
    cd "$F10/repo"
    export PATH="$F10/bin:$PATH"
    export MOCK_SYS_LOG="$F10/systemctl.log"
    export MOCK_CURL_LOG="$F10/curl.log"
    export SYSTEMCTL_CMD="$F10/bin/systemctl"
    export CURL_FAILS="1"
    export AUTO_UPDATE_LOCK_FILE="$F10/lock"
    export AUTO_UPDATE_BACKUP_DIR="$F10/backups"

    set +e
    bash scripts/auto_update_cron.sh
    res=$?
    set -e
    assert_true "[ $res -ne 0 ]"
    assert_true "grep -q 'Health check failed or timed out' logs/auto_update.log"
    assert_true "[ -f logs/auto_update_intervention_required ]"
    # Data is not reset or deleted
    assert_true "[ -f data/radar.db ]"
    assert_true "[ -f data/live_journal.db ]"
)
PASSED_COUNT=$((PASSED_COUNT + 1))
echo "✅ Test 10 Passed"

# ------------------------------------------------------------------------------
# TEST 11: Successful health verification allows script to report success
# ------------------------------------------------------------------------------
log_test 11 "Successful health verification allows the script to report success"
F11="$TEST_ROOT/f11"
setup_fixture "$F11"
# Push remote update
CLONE11="$F11/push_clone"
git clone -b dev "$F11/remote.git" "$CLONE11" >/dev/null 2>&1
(
    cd "$CLONE11"
    echo "v11" >> version.txt
    git commit -am "v11" >/dev/null 2>&1
    git push origin dev >/dev/null 2>&1
)
(
    cd "$F11/repo"
    export PATH="$F11/bin:$PATH"
    export MOCK_SYS_LOG="$F11/systemctl.log"
    export MOCK_CURL_LOG="$F11/curl.log"
    export SYSTEMCTL_CMD="$F11/bin/systemctl"
    export AUTO_UPDATE_LOCK_FILE="$F11/lock"
    export AUTO_UPDATE_BACKUP_DIR="$F11/backups"

    bash scripts/auto_update_cron.sh
    assert_true "grep -q 'verified HEALTHY' logs/auto_update.log"
    assert_true "[ ! -f logs/auto_update_intervention_required ]"
)
PASSED_COUNT=$((PASSED_COUNT + 1))
echo "✅ Test 11 Passed"

# ------------------------------------------------------------------------------
# TEST 12: Updater never invokes server_supervisor.py or wrong service name
# ------------------------------------------------------------------------------
log_test 12 "The updater never invokes server_supervisor.py or the wrong service name"
F12="$TEST_ROOT/f12"
setup_fixture "$F12"
# Static code check on script source
assert_true "! grep -q 'server_supervisor.py' '$SCRIPT_SRC'"
assert_true "! grep -q 'rahuul-radar.service' '$SCRIPT_SRC'"
assert_true "grep -q 'rahuul_radar.service' '$SCRIPT_SRC'"
PASSED_COUNT=$((PASSED_COUNT + 1))
echo "✅ Test 12 Passed"

# ------------------------------------------------------------------------------
# TEST 13: Missing data/live_journal.db blocks pending update before merge
# ------------------------------------------------------------------------------
log_test 13 "Missing data/live_journal.db blocks pending update before merge"
F13="$TEST_ROOT/f13"
setup_fixture "$F13"
CLONE13="$F13/push_clone"
git clone -b dev "$F13/remote.git" "$CLONE13" >/dev/null 2>&1
(
    cd "$CLONE13"
    echo "v13" >> version.txt
    git commit -am "v13" >/dev/null 2>&1
    git push origin dev >/dev/null 2>&1
)
(
    cd "$F13/repo"
    rm -f data/live_journal.db
    export PATH="$F13/bin:$PATH"
    export MOCK_SYS_LOG="$F13/systemctl.log"
    export SYSTEMCTL_CMD="$F13/bin/systemctl"
    export AUTO_UPDATE_LOCK_FILE="$F13/lock"
    export AUTO_UPDATE_BACKUP_DIR="$F13/backups"

    set +e
    bash scripts/auto_update_cron.sh
    res=$?
    set -e
    assert_true "[ $res -ne 0 ]"
    assert_true "grep -q 'REQUIRED_DATABASE_MISSING:data/live_journal.db' logs/auto_update.log"
    assert_equals "$(cat version.txt)" "initial"
    assert_true "[ ! -f '$F13/systemctl.log' ]"
)
PASSED_COUNT=$((PASSED_COUNT + 1))
echo "✅ Test 13 Passed"

# ------------------------------------------------------------------------------
# TEST 14: Missing data/radar.db blocks pending update before merge
# ------------------------------------------------------------------------------
log_test 14 "Missing data/radar.db blocks pending update before merge"
F14="$TEST_ROOT/f14"
setup_fixture "$F14"
CLONE14="$F14/push_clone"
git clone -b dev "$F14/remote.git" "$CLONE14" >/dev/null 2>&1
(
    cd "$CLONE14"
    echo "v14" >> version.txt
    git commit -am "v14" >/dev/null 2>&1
    git push origin dev >/dev/null 2>&1
)
(
    cd "$F14/repo"
    rm -f data/radar.db
    export PATH="$F14/bin:$PATH"
    export MOCK_SYS_LOG="$F14/systemctl.log"
    export SYSTEMCTL_CMD="$F14/bin/systemctl"
    export AUTO_UPDATE_LOCK_FILE="$F14/lock"
    export AUTO_UPDATE_BACKUP_DIR="$F14/backups"

    set +e
    bash scripts/auto_update_cron.sh
    res=$?
    set -e
    assert_true "[ $res -ne 0 ]"
    assert_true "grep -q 'REQUIRED_DATABASE_MISSING:data/radar.db' logs/auto_update.log"
    assert_equals "$(cat version.txt)" "initial"
    assert_true "[ ! -f '$F14/systemctl.log' ]"
)
PASSED_COUNT=$((PASSED_COUNT + 1))
echo "✅ Test 14 Passed"

# ------------------------------------------------------------------------------
# TEST 15: Missing radar.db blocks pending update before merge
# ------------------------------------------------------------------------------
log_test 15 "Missing radar.db blocks pending update before merge"
F15="$TEST_ROOT/f15"
setup_fixture "$F15"
CLONE15="$F15/push_clone"
git clone -b dev "$F15/remote.git" "$CLONE15" >/dev/null 2>&1
(
    cd "$CLONE15"
    echo "v15" >> version.txt
    git commit -am "v15" >/dev/null 2>&1
    git push origin dev >/dev/null 2>&1
)
(
    cd "$F15/repo"
    rm -f radar.db
    export PATH="$F15/bin:$PATH"
    export MOCK_SYS_LOG="$F15/systemctl.log"
    export SYSTEMCTL_CMD="$F15/bin/systemctl"
    export AUTO_UPDATE_LOCK_FILE="$F15/lock"
    export AUTO_UPDATE_BACKUP_DIR="$F15/backups"

    set +e
    bash scripts/auto_update_cron.sh
    res=$?
    set -e
    assert_true "[ $res -ne 0 ]"
    assert_true "grep -q 'REQUIRED_DATABASE_MISSING:radar.db' logs/auto_update.log"
    assert_equals "$(cat version.txt)" "initial"
    assert_true "[ ! -f '$F15/systemctl.log' ]"
)
PASSED_COUNT=$((PASSED_COUNT + 1))
echo "✅ Test 15 Passed"

# ------------------------------------------------------------------------------
# TEST 16: Inaccessible/unreadable required database blocks update before merge
# ------------------------------------------------------------------------------
log_test 16 "Inaccessible/unreadable required database blocks update before merge"
F16="$TEST_ROOT/f16"
setup_fixture "$F16"
CLONE16="$F16/push_clone"
git clone -b dev "$F16/remote.git" "$CLONE16" >/dev/null 2>&1
(
    cd "$CLONE16"
    echo "v16" >> version.txt
    git commit -am "v16" >/dev/null 2>&1
    git push origin dev >/dev/null 2>&1
)
(
    cd "$F16/repo"
    chmod 000 data/radar.db
    export PATH="$F16/bin:$PATH"
    export MOCK_SYS_LOG="$F16/systemctl.log"
    export SYSTEMCTL_CMD="$F16/bin/systemctl"
    export AUTO_UPDATE_LOCK_FILE="$F16/lock"
    export AUTO_UPDATE_BACKUP_DIR="$F16/backups"

    set +e
    bash scripts/auto_update_cron.sh
    res=$?
    set -e
    assert_true "[ $res -ne 0 ]"
    assert_true "grep -q 'REQUIRED_DATABASE_UNREADABLE:data/radar.db' logs/auto_update.log"
    assert_equals "$(cat version.txt)" "initial"
    assert_true "[ ! -f '$F16/systemctl.log' ]"
    chmod 644 data/radar.db
)
PASSED_COUNT=$((PASSED_COUNT + 1))
echo "✅ Test 16 Passed"

# ------------------------------------------------------------------------------
# TEST 17: Backup integrity failure blocks update before merge
# ------------------------------------------------------------------------------
log_test 17 "Backup integrity failure blocks update before merge"
F17="$TEST_ROOT/f17"
setup_fixture "$F17"
CLONE17="$F17/push_clone"
git clone -b dev "$F17/remote.git" "$CLONE17" >/dev/null 2>&1
(
    cd "$CLONE17"
    echo "v17" >> version.txt
    git commit -am "v17" >/dev/null 2>&1
    git push origin dev >/dev/null 2>&1
)
(
    cd "$F17/repo"
    echo "corrupted_non_sqlite_header_data" > data/radar.db
    export PATH="$F17/bin:$PATH"
    export MOCK_SYS_LOG="$F17/systemctl.log"
    export SYSTEMCTL_CMD="$F17/bin/systemctl"
    export AUTO_UPDATE_LOCK_FILE="$F17/lock"
    export AUTO_UPDATE_BACKUP_DIR="$F17/backups"

    set +e
    bash scripts/auto_update_cron.sh
    res=$?
    set -e
    assert_true "[ $res -ne 0 ]"
    assert_true "grep -q 'Pre-update database backup failed' logs/auto_update.log"
    assert_equals "$(cat version.txt)" "initial"
    assert_true "[ ! -f '$F17/systemctl.log' ]"
)
PASSED_COUNT=$((PASSED_COUNT + 1))
echo "✅ Test 17 Passed"

# ------------------------------------------------------------------------------
# TEST 18: When all three required databases exist and validate, fast-forward succeeds
# ------------------------------------------------------------------------------
log_test 18 "When all three required databases exist and validate, fast-forward succeeds"
F18="$TEST_ROOT/f18"
setup_fixture "$F18"
CLONE18="$F18/push_clone"
git clone -b dev "$F18/remote.git" "$CLONE18" >/dev/null 2>&1
(
    cd "$CLONE18"
    echo "v18" >> version.txt
    git commit -am "v18" >/dev/null 2>&1
    git push origin dev >/dev/null 2>&1
)
(
    cd "$F18/repo"
    export PATH="$F18/bin:$PATH"
    export MOCK_SYS_LOG="$F18/systemctl.log"
    export MOCK_CURL_LOG="$F18/curl.log"
    export SYSTEMCTL_CMD="$F18/bin/systemctl"
    export AUTO_UPDATE_LOCK_FILE="$F18/lock"
    export AUTO_UPDATE_BACKUP_DIR="$F18/backups"

    set +e
    bash scripts/auto_update_cron.sh
    res=$?
    set -e
    assert_true "[ $res -eq 0 ]"
    assert_true "grep -q 'BACKUP_SUCCESS:3' logs/auto_update.log"
    assert_true "grep -q 'restart rahuul_radar.service' '$F18/systemctl.log'"
    assert_true "grep -q 'is-active --quiet rahuul_radar.service' '$F18/systemctl.log'"
    assert_true "grep -q 'verified HEALTHY' logs/auto_update.log"
    assert_equals "$(cat version.txt)" "initial
v18"
    assert_true "[ -f '$F18/backups/'*/data_live_journal.db ]"
    assert_true "[ -f '$F18/backups/'*/data_radar.db ]"
    assert_true "[ -f '$F18/backups/'*/root_radar.db ]"
)
PASSED_COUNT=$((PASSED_COUNT + 1))
echo "✅ Test 18 Passed"

echo "======================================================================"
echo "🎉 ALL $PASSED_COUNT / $TOTAL_COUNT REGRESSION TESTS PASSED CLEANLY!"
echo "======================================================================"
