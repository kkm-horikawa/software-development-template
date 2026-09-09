import ast
from pathlib import Path
from textwrap import dedent

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src"


def test_method_flow_http_entry_uses_only_named_stages() -> None:
    source = SOURCE_ROOT / "worklog/adapters/http/activity_endpoint.py"
    assert (
        validate_method_flow(source.read_text(), "ActivityEndpoint", "post_activity")
        == []
    )


def test_method_flow_usecase_uses_only_named_stages() -> None:
    source = SOURCE_ROOT / "worklog/application/start_activity.py"
    assert validate_method_flow(source.read_text(), "StartActivity", "run") == []


def test_method_flow_accepts_methods_on_the_responsible_object() -> None:
    source = """
    class Flow:
        def run(self):
            value = self.read()
            result = self.decide(value)
            return self.write(result)
    """
    assert validate_method_flow(dedent(source), "Flow", "run") == []


def test_method_flow_rejects_free_function_call() -> None:
    source = """
    class Flow:
        def run(self):
            value = self.read()
            result = helper(value)
            return self.write(result)
    """
    assert "selfの段ではない呼び出し" in validate_method_flow(
        dedent(source), "Flow", "run"
    )


def test_method_flow_rejects_low_level_package_call() -> None:
    source = """
    class Flow:
        def run(self):
            value = self.read()
            print(value)
            return self.write(value)
    """
    assert "selfの段ではない呼び出し" in validate_method_flow(
        dedent(source), "Flow", "run"
    )


def validate_method_flow(source: str, class_name: str, method_name: str) -> list[str]:
    tree = ast.parse(source)
    method = find_method(tree, class_name, method_name)
    if method is None:
        return [f"{class_name}.{method_name} がありません"]

    stage_calls = 0
    violations: list[str] = []
    for node in ast.walk(method):
        if not isinstance(node, ast.Call):
            continue
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "self"
        ):
            stage_calls += 1
            continue
        violations.append("selfの段ではない呼び出し")
    if stage_calls == 0:
        violations.append("利用の流れを示す段がありません")
    return violations


def find_method(
    tree: ast.Module, class_name: str, method_name: str
) -> ast.FunctionDef | None:
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for member in node.body:
            if isinstance(member, ast.FunctionDef) and member.name == method_name:
                return member
    return None
