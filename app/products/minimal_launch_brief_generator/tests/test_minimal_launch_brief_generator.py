from app.products.minimal_launch_brief_generator.src import build_launch_brief


def test_build_launch_brief() -> None:
    brief = build_launch_brief()
    assert "Minimal Launch Brief" in brief
    assert "Objective" in brief
    assert "Audience" in brief
    assert "Value Proposition" in brief
