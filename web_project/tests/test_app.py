from app.main import app


def test_app_imports_and_has_routes():
    assert app.url_map is not None
    paths = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/" in paths
    assert "/players" in paths
    assert "/compare" in paths
    assert "/quiz" in paths
