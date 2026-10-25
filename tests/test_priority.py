import ast
from pathlib import Path

SERVER_FILE = Path(__file__).resolve().parents[1] / "server" / "log_server.py"


def test_priority_values():
    source = SERVER_FILE.read_text(encoding="utf-8")
    tree = ast.parse(source)

    priorities = None

    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(
                isinstance(target, ast.Name) and target.id == "PRIORITY"
                for target in node.targets
            ):
                priorities = ast.literal_eval(node.value)
                break

    assert priorities is not None, "PRIORITY dictionary not found"

    expected = {
        "CRITICAL": 1,
        "ERROR": 2,
        "WARNING": 3,
        "INFO": 4,
    }

    assert priorities == expected, (
        f"Expected {expected}, got {priorities}"
    )

    print("PASS: All severity priorities are correct.")


if __name__ == "__main__":
    test_priority_values()
    print("All priority tests passed.")
