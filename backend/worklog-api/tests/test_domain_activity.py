import pytest
from worklog.domain.activity import ActivityTitle, EmptyActivityTitle


class TestActivityTitle:
    def test_activity_title_trims_surrounding_spaces(self) -> None:
        assert ActivityTitle.create("  設計を書く  ").value == "設計を書く"

    def test_activity_title_refuses_empty_value(self) -> None:
        with pytest.raises(EmptyActivityTitle, match="作業名を空にはできません"):
            ActivityTitle.create("   ")
