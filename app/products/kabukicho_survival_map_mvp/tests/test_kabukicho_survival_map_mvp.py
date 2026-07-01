from app.products.kabukicho_survival_map_mvp.src import build_product_brief
from app.products.kabukicho_survival_map_mvp.src.kabukicho_survival_map_mvp import (
    load_map_places,
)


def test_build_product_brief() -> None:
    brief = build_product_brief()
    assert "Kabukicho Survival Map MVP" in brief
    assert "Audience" in brief
    assert "Value Proposition" in brief
    assert "Safety and Disclaimer" in brief
    assert "Expanded Map Data" in brief
    assert "Kabukicho Information Point" in brief
    assert "Confirmed information" in brief
    assert "Caution / uncertainty" in brief
    assert "Gray-zone notes" in brief


def test_load_map_places() -> None:
    places = load_map_places()
    assert len(places) >= 5
    assert places[0]["name"] == "Kabukicho Information Point"
    assert "category" in places[0]
    assert "availability_type" in places[0]
    assert "hours_note" in places[0]
    assert "gray_zone_note" in places[0]
    assert "caution_note" in places[0]
    assert "source_note" in places[0]
    assert "last_verified_note" in places[0]
