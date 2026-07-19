from somia_dataset_generator.paths import character_spec_path
from somia_dataset_generator.planner import coverage_report, coverage_violations, create_plan
from somia_dataset_generator.validation import validate_character


def _policy():
    return {
        "policy_id": "p1",
        "dimensions": {
            "framing": {"close": 1, "full": 1},
            "angle": {"front": 1},
            "expression": {"soft": 1},
            "gaze": {"lowered": 1},
            "environment": {"dim_private_room": 1},
        },
        "constraints": {"minimum_per_bucket": 1},
    }


def test_create_plan_is_deterministic_given_the_same_seed():
    character = validate_character(character_spec_path("airi"))
    policy = _policy()
    a = create_plan(character, policy, 3, seed=42)
    b = create_plan(character, policy, 3, seed=42)
    assert [x.to_dict() for x in a] == [x.to_dict() for x in b]


def test_create_plan_different_seeds_can_differ():
    character = validate_character(character_spec_path("airi"))
    policy = _policy()
    policy["dimensions"]["framing"] = {"close": 5, "full": 5}
    a = create_plan(character, policy, 10, seed=1)
    b = create_plan(character, policy, 10, seed=2)
    assert [item.dimensions["framing"] for item in a] != [item.dimensions["framing"] for item in b]


def test_create_plan_respects_exact_bucket_weights_when_count_matches_total():
    character = validate_character(character_spec_path("airi"))
    policy = _policy()
    policy["dimensions"]["framing"] = {"close": 3, "full": 7}
    plan = create_plan(character, policy, 10, seed=0)
    close_count = sum(1 for item in plan if item.dimensions["framing"] == "close")
    full_count = sum(1 for item in plan if item.dimensions["framing"] == "full")
    assert close_count == 3
    assert full_count == 7


def test_create_plan_apportions_proportionally_for_arbitrary_count():
    character = validate_character(character_spec_path("airi"))
    policy = _policy()
    policy["dimensions"]["framing"] = {"close": 1, "full": 1}
    plan = create_plan(character, policy, 3, seed=0)
    assert len(plan) == 3
    close_count = sum(1 for item in plan if item.dimensions["framing"] == "close")
    full_count = sum(1 for item in plan if item.dimensions["framing"] == "full")
    assert close_count + full_count == 3
    assert abs(close_count - full_count) <= 1


def test_create_plan_rejects_non_positive_count():
    character = validate_character(character_spec_path("airi"))
    policy = _policy()
    try:
        create_plan(character, policy, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for count=0")


def test_coverage_report_and_violations():
    records = [
        {"dimensions": {"framing": "close"}},
        {"dimensions": {"framing": "close"}},
        {"dimensions": {"framing": "full"}},
    ]
    report = coverage_report(records, ["framing"])
    assert report == {"framing": {"close": 2, "full": 1}}

    policy = {"dimensions": {"framing": {"close": 1, "full": 1}}, "constraints": {"minimum_per_bucket": 2}}
    violations = coverage_violations(report, policy)
    assert violations == ["framing.full: 1 accepted, minimum 2 required"]


def test_coverage_violations_empty_when_minimum_not_set():
    report = {"framing": {"close": 0}}
    policy = {"dimensions": {"framing": {"close": 1}}, "constraints": {}}
    assert coverage_violations(report, policy) == []
