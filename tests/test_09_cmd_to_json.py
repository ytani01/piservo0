# (c) 2025 Yoichi Tanibayashi
#
"""
Unit test for piservo0.helper.StrCmdToJson
"""
import pytest
from piservo0.helper.str_cmd_to_json import StrCmdToJson

# Fixture for a default instance
@pytest.fixture
def c2j_default():
    """Returns a StrCmdToJson instance with default settings."""
    return StrCmdToJson(debug=True)

# Fixture for an instance with a specific angle_factor
@pytest.fixture
def c2j_with_af():
    """Returns a StrCmdToJson instance with a sample angle_factor."""
    return StrCmdToJson(angle_factor=[1, -1, 1, -1], debug=True)


class TestStrCmdToJsonInit:
    """Tests for StrCmdToJson initialization and properties."""

    def test_init_default(self, c2j_default):
        """Test constructor with default angle_factor."""
        assert c2j_default.angle_factor == []

    def test_init_with_angle_factor(self, c2j_with_af):
        """Test constructor with a given angle_factor."""
        assert c2j_with_af.angle_factor == [1, -1, 1, -1]

    def test_angle_factor_property(self, c2j_default):
        """Test the angle_factor property setter."""
        new_af = [-1, 1, -1]
        c2j_default.angle_factor = new_af
        assert c2j_default.angle_factor == new_af


class TestParseAngles:
    """Tests for the private method _parse_angles."""

    @pytest.mark.parametrize(
        "param_str, angle_factor, expected",
        [
            # Basic cases
            ("10,20,30", [], [10, 20, 30]),
            ("-90,0,90", [], [-90, 0, 90]),
            ("10,.,-10", [], [10, None, -10]),
            # Aliases
            ("x,n,c", [], ["max", "min", "center"]),
            ("max,min,center", [], ["max", "min", "center"]),
            # Mixed
            ("x,10,n,.,c,-20", [], ["max", 10, "min", None, "center", -20]),
            # With angle_factor
            ("10,20,30", [1, -1, 1], [10, -20, 30]),
            ("10,20,30", [-1, 1], [-10, 20, 30]),
            ("x,n,c", [1, -1, 1], ["max", "max", "center"]),
            ("n,x,c", [-1, 1, -1], ["max", "max", "center"]),
            # Edge cases
            (" 10 , -20 ", [], [10, -20]),
        ]
    )
    def test_parse_angles_valid(self, param_str, angle_factor, expected):
        c2j = StrCmdToJson(angle_factor=angle_factor, debug=True)
        assert c2j._parse_angles(param_str) == expected

    @pytest.mark.parametrize(
        "param_str",
        [
            "91",           # Out of range
            "-91",          # Out of range
            "abc",          # Invalid literal
            "10,,20",       # Empty element
            "",             # Empty string
        ]
    )
    def test_parse_angles_invalid(self, param_str):
        c2j = StrCmdToJson(debug=True)
        assert c2j._parse_angles(param_str) is None


class TestJsonConversion:
    """Tests for the main json() and jsonstr() methods."""

    @pytest.mark.parametrize(
        "cmdstr, expected_json",
        [
            # mv
            ("mv:10,20", {"cmd": "move_angle_sync", "angles": [10, 20]}),
            ("mv:-10,c,x,n,.", {"cmd": "move_angle_sync", "angles": [-10, "center", "max", "min", None]}),
            ("MV:0,90,-90", {"cmd": "move_angle_sync", "angles": [0, 90, -90]}),
            # sl
            ("sl:0.5", {"cmd": "sleep", "sec": 0.5}),
            ("sl:10", {"cmd": "sleep", "sec": 10.0}),
            # ms
            ("ms:1.2", {"cmd": "move_sec", "sec": 1.2}),
            # st
            ("st:10", {"cmd": "step_n", "n": 10}),
            # is
            ("is:0.1", {"cmd": "interval", "sec": 0.1}),
            # ca, zz
            ("ca", {"cmd": "cancel"}),
            ("zz", {"cmd": "cancel"}),
        ],
    )
    def test_json_valid_commands(self, c2j_default, cmdstr, expected_json):
        """Test json() with valid command strings."""
        assert c2j_default.json(cmdstr) == expected_json

    @pytest.mark.parametrize(
        "cmdstr, angle_factor, expected_angles",
        [
            ("mv:30,40", [1, -1], [30, -40]),
            ("mv:x,n", [1, -1], ["max", "max"]),
            ("mv:n,x", [1, -1], ["min", "min"]),
            ("mv:10,20,30", [1, -1], [10, -20, 30]),
            ("mv:10,20", [1, -1, 1], [10, -20]),
        ],
    )
    def test_json_with_angle_factor(self, cmdstr, angle_factor, expected_angles):
        """Test json() with angle_factor affecting 'mv' command."""
        c2j = StrCmdToJson(angle_factor=angle_factor, debug=True)
        result = c2j.json(cmdstr)
        assert result["cmd"] == "move_angle_sync"
        assert result["angles"] == expected_angles

    @pytest.mark.parametrize(
        "cmdstr",
        [
            # Invalid command name
            "xx:10",
            # Invalid format
            "mv 10,20",
            "mv:",
            "sl:",
            # Invalid parameters
            "mv:91", "mv:-91", "mv:a", "mv:10,,20",
            "sl:a", "sl:-1",
            "st:a", "st:0", "st:-1",
            # Unexpected parameters
            "ca:1", "zz:1",
        ],
    )
    def test_json_invalid_commands(self, c2j_default, cmdstr):
        """Test json() with invalid command strings should return an error dict."""
        assert c2j_default.json(cmdstr) == {"err": cmdstr}

    def test_jsonstr(self, c2j_default):
        """Test jsonstr() for valid and invalid commands."""
        # Valid
        cmdstr_valid = "mv:10,20"
        expected_str_valid = '{"cmd": "move_angle_sync", "angles": [10, 20]}'
        assert c2j_default.jsonstr(cmdstr_valid) == expected_str_valid
        # Invalid
        cmdstr_invalid = "invalid cmd"
        expected_str_invalid = '{"err": "invalid cmd"}'
        assert c2j_default.jsonstr(cmdstr_invalid) == expected_str_invalid