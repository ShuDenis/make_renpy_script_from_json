import json
import pytest

from dialoggen.validator import validate, ValidationError


def test_validator_accepts_valid(dialog_project):
    validate(dialog_project)


def test_validator_detects_missing_entry(dialog_project):
    invalid = json.loads(json.dumps(dialog_project))
    invalid["dialog_trees"][0].pop("entry_node", None)
    with pytest.raises(ValidationError):
        validate(invalid)


def test_validator_detects_unknown_link(dialog_project):
    invalid = json.loads(json.dumps(dialog_project))
    invalid["dialog_trees"][0]["nodes"][0]["next"] = "missing_node"
    with pytest.raises(ValidationError):
        validate(invalid)
