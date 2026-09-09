import ast
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src/worklog"
ALLOWED_IMPORTS = {
    "domain": {"domain"},
    "ports": {"domain", "ports"},
    "application": {"domain", "ports", "application"},
    "adapters": {"domain", "ports", "application", "adapters"},
}


def test_clean_architecture_dependencies_point_inward() -> None:
    violations: list[str] = []
    for source in SOURCE_ROOT.rglob("*.py"):
        layer = source.relative_to(SOURCE_ROOT).parts[0]
        if layer not in ALLOWED_IMPORTS:
            continue
        for imported_layer in worklog_imports(source):
            if imported_layer not in ALLOWED_IMPORTS[layer]:
                violations.append(f"{source.name}: {layer} -> {imported_layer}")
    assert violations == []


def worklog_imports(source: Path) -> set[str]:
    imported_layers: set[str] = set()
    tree = ast.parse(source.read_text())
    for node in ast.walk(tree):
        modules: list[str] = []
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            modules.append(node.module)
        for module in modules:
            if not module.startswith("worklog."):
                continue
            parts = module.split(".")
            if len(parts) > 1:
                imported_layers.add(parts[1])
    return imported_layers
