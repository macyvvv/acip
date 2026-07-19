from somia_dataset_generator.planner import create_plan
from somia_dataset_generator.validation import validate_character

def test_create_plan_is_deterministic():
    character = validate_character("specs/characters/airi.yaml")
    policy = {
        "policy_id": "p1",
        "dimensions": {
            "framing": {"close": 1, "full": 1},
            "angle": {"front": 1},
            "expression": {"soft": 1},
            "gaze": {"lowered": 1},
            "environment": {"dim_private_room": 1},
        },
    }
    a = create_plan(character, policy, 3)
    b = create_plan(character, policy, 3)
    assert [x.to_dict() for x in a] == [x.to_dict() for x in b]
    assert a[0].dimensions["framing"] == "close"
    assert a[1].dimensions["framing"] == "full"
