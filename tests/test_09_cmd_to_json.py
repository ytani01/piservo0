# (c) 2025 Yoichi Tanibayashi
#
"""
Unit test for piservo0.helper.CmdToJson
"""
import pytest
from piservo0.helper.cmd_to_json import CmdToJson


class TestCmdToJson:
    """Unit test for CmdToJson."""

    def test_init_no_angle_factor(self):
        """Test constructor with default angle_factor."""
        c2j = CmdToJson(debug=True)
        assert c2j.angle_factor == []

    def test_init_with_angle_factor(self):
        """Test constructor with a given angle_factor."""
        angle_factor = [1, -1, 1]
        c2j = CmdToJson(angle_factor=angle_factor, debug=True)
        assert c2j.angle_factor == angle_factor

    @pytest.mark.parametrize(
        "cmdstr, expected_json",
        [
            # Normal cases for 'mv'
            ("mv:10,20", {"cmd": "move_angle_sync", "angles": [10, 20]}),
            ("mv:-10,c,x,n,.", {"cmd": "move_angle_sync", "angles": [-10, "center", "max", "min", None]}),
            ("MV:0,90,-90", {"cmd": "move_angle_sync", "angles": [0, 90, -90]}),

            # Normal cases for other commands
            ("sl:0.5", {"cmd": "sleep", "sec": 0.5}),
            ("ms:1.2", {"cmd": "move_sec", "sec": 1.2}),
            ("is:0.1", {"cmd": "interval", "sec": 0.1}),
            ("st:10", {"cmd": "step_n", "n": 10}),
            ("ca", {"cmd": "cancel"}),
            ("zz", {"cmd": "cancel"}),

            # Edge cases
            ("mv:10", {"cmd": "move_angle_sync", "angles": [10]}),
            ("sl:0", {"cmd": "sleep", "sec": 0.0}),
        ],
    )
    def test_json_valid_commands(self, cmdstr, expected_json):
        """Test json() with valid command strings."""
        c2j = CmdToJson(debug=True)
        assert c2j.json(cmdstr) == expected_json

    @pytest.mark.parametrize(
        "cmdstr, angle_factor, expected_angles",
        [
            ("mv:30,40", [1, -1], [30, -40]),
            ("mv:x,n", [1, -1], ["max", "max"]),
            ("mv:n,x", [1, -1], ["min", "min"]),
            ("mv:30,40", [-1, 1], [-30, 40]),
            ("mv:x,n", [-1, 1], ["min", "min"]),
            ("mv:n,x", [-1, 1], ["max", "max"]),
            ("mv:10,20,30", [1, -1], [10, -20, 30]), # angle_factor shorter
            ("mv:10,20", [1, -1, 1], [10, -20]), # angle_factor longer
        ],
    )
    def test_json_with_angle_factor(self, cmdstr, angle_factor, expected_angles):
        """Test json() with angle_factor."""
        c2j = CmdToJson(angle_factor=angle_factor, debug=True)
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
            "st:",
            # Invalid parameters for 'mv'
            "mv:91",
            "mv:-91",
            "mv:a",
            "mv:10,,20",
            # Invalid parameters for others
            "sl:a",
            "sl:-1",
            "ms:a",
            "is:a",
            "st:a",
            "st:0",
            "st:-1",
            # Parameters where none are expected
            "ca:1",
            "zz:1",
        ],
    )
    def test_json_invalid_commands(self, cmdstr):
        """Test json() with invalid command strings."""
        c2j = CmdToJson(debug=True)
        assert c2j.json(cmdstr) == {"err": cmdstr}

    def test_jsonstr(self):
        """Test jsonstr() method."""
        c2j = CmdToJson(debug=True)
        cmdstr = "mv:10,20"
        # In Python 3.6+ dict insertion order is preserved, so this is reliable
        expected_str = '{"cmd": "move_angle_sync", "angles": [10, 20]}'
        assert c2j.jsonstr(cmdstr) == expected_str
