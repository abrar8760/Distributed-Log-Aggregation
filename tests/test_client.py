import subprocess
import sys

CLIENT = "client/log_client.py"


def run_client(*args):
    return subprocess.run(
        [sys.executable, CLIENT, *args],
        capture_output=True,
        text=True,
    )


def test_invalid_log_level():
    result = run_client("DEBUG", "Test message")
    assert result.returncode != 0
    assert "Invalid level" in result.stdout
    print("PASS: Invalid log level is rejected.")


def test_missing_message():
    result = run_client("INFO")
    assert result.returncode != 0
    assert "Usage:" in result.stdout
    print("PASS: Missing message is rejected.")


def test_valid_level():
    # The client validates its arguments before sending a UDP message.
    # Use an invalid test destination to avoid depending on a running server.
    result = run_client("INFO", "Test message")
    assert result.returncode == 0
    assert "Sent log to" in result.stdout
    print("PASS: Valid log level is accepted.")


if __name__ == "__main__":
    test_invalid_log_level()
    test_missing_message()
    test_valid_level()
    print("\nAll 3 tests passed.")
