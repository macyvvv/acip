import subprocess
import sys

from somia_dataset_generator.paths import (
    character_schema_path,
    character_spec_path,
    runtime_config_path,
    sampling_policy_path,
)


def test_default_paths_resolve_to_real_files():
    assert character_spec_path("airi").is_file()
    assert sampling_policy_path("airi").is_file()
    assert character_schema_path().is_file()
    assert runtime_config_path().is_file()


def test_validate_command_is_cwd_independent(tmp_path):
    """The whole point of paths.py: this must work no matter which directory
    the process is invoked from."""
    result = subprocess.run(
        [sys.executable, "-m", "somia_dataset_generator", "validate", "--character", "airi"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "valid: airi" in result.stdout
