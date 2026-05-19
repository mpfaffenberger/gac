"""Tests for biggest_gac_commits and biggest_gac_files tracking (v5 schema)."""

from unittest.mock import patch

import gac.stats.store as store
from gac.stats import load_stats, record_commit, record_gac, record_tokens, save_stats
from gac.stats.recorder import _accumulator


class TestBiggestGacSchema:
    """Schema-level tests for v5 biggest_gac_commits/files fields."""

    def test_empty_stats_has_new_fields(self):
        """_empty_stats() includes biggest_gac_commits and biggest_gac_files."""
        empty = store._empty_stats()
        assert empty["biggest_gac_commits"] == 0
        assert empty["biggest_gac_commits_date"] is None
        assert empty["biggest_gac_files"] == 0
        assert empty["biggest_gac_files_date"] is None
        assert empty["_version"] == 5

    def test_load_stats_returns_new_fields(self, tmp_path):
        """load_stats() populates new fields from persisted data."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            data = store._empty_stats()
            data["biggest_gac_commits"] = 5
            data["biggest_gac_commits_date"] = "2025-05-20T10:00:00"
            data["biggest_gac_files"] = 42
            data["biggest_gac_files_date"] = "2025-05-20T10:00:00"
            save_stats(data)

            loaded = load_stats()
            assert loaded["biggest_gac_commits"] == 5
            assert loaded["biggest_gac_commits_date"] == "2025-05-20T10:00:00"
            assert loaded["biggest_gac_files"] == 42
            assert loaded["biggest_gac_files_date"] == "2025-05-20T10:00:00"

    def test_load_stats_defaults_new_fields(self, tmp_path):
        """load_stats() returns 0/None for missing new fields."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            data = store._empty_stats()
            # Simulate v4 data by removing the new fields
            del data["biggest_gac_commits"]
            del data["biggest_gac_commits_date"]
            del data["biggest_gac_files"]
            del data["biggest_gac_files_date"]
            data["_version"] = 4
            save_stats(data)

            loaded = load_stats()
            # Migration should backfill from empty history
            assert loaded["biggest_gac_commits"] == 0
            assert loaded["biggest_gac_commits_date"] is None
            assert loaded["biggest_gac_files"] == 0
            assert loaded["biggest_gac_files_date"] is None


class TestBiggestGacMigration:
    """Tests for v4→v5 migration."""

    def test_migration_adds_fields(self, tmp_path):
        """v4→v5 migration adds biggest_gac_commits and biggest_gac_files."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            data = store._empty_stats()
            del data["biggest_gac_commits"]
            del data["biggest_gac_commits_date"]
            del data["biggest_gac_files"]
            del data["biggest_gac_files_date"]
            data["_version"] = 4
            save_stats(data)

            loaded = load_stats()
            assert loaded["_version"] == 5
            assert "biggest_gac_commits" in loaded
            assert "biggest_gac_commits_date" in loaded
            assert "biggest_gac_files" in loaded
            assert "biggest_gac_files_date" in loaded

    def test_migration_backfills_from_history(self, tmp_path):
        """v4→v5 migration backfills biggest_gac_commits/files from history records."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            data = store._empty_stats()
            del data["biggest_gac_commits"]
            del data["biggest_gac_commits_date"]
            del data["biggest_gac_files"]
            del data["biggest_gac_files_date"]
            data["_version"] = 4
            data["history"] = [
                {"ts": "2025-05-01T10:00:00", "commits": 3, "files": 10},
                {"ts": "2025-05-10T10:00:00", "commits": 7, "files": 5},
                {"ts": "2025-05-15T10:00:00", "commits": 2, "files": 25},
            ]
            save_stats(data)

            loaded = load_stats()
            assert loaded["biggest_gac_commits"] == 7
            assert loaded["biggest_gac_commits_date"] == "2025-05-10T10:00:00"
            assert loaded["biggest_gac_files"] == 25
            assert loaded["biggest_gac_files_date"] == "2025-05-15T10:00:00"

    def test_migration_handles_empty_history(self, tmp_path):
        """v4→v5 migration defaults to 0/None when no history exists."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            data = store._empty_stats()
            del data["biggest_gac_commits"]
            del data["biggest_gac_commits_date"]
            del data["biggest_gac_files"]
            del data["biggest_gac_files_date"]
            data["_version"] = 4
            data["history"] = []
            save_stats(data)

            loaded = load_stats()
            assert loaded["biggest_gac_commits"] == 0
            assert loaded["biggest_gac_commits_date"] is None
            assert loaded["biggest_gac_files"] == 0
            assert loaded["biggest_gac_files_date"] is None

    def test_migration_idempotent(self, tmp_path):
        """Running migration twice doesn't corrupt existing values."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            data = store._empty_stats()
            data["biggest_gac_commits"] = 99
            data["biggest_gac_commits_date"] = "2025-01-01T00:00:00"
            data["biggest_gac_files"] = 100
            data["biggest_gac_files_date"] = "2025-01-01T00:00:00"
            data["_version"] = 5
            save_stats(data)

            loaded = load_stats()
            assert loaded["biggest_gac_commits"] == 99
            assert loaded["biggest_gac_files"] == 100

    def test_migration_v1_to_v5(self, tmp_path):
        """Full migration chain from v1 to v5 includes new fields."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            # Minimal v1 data
            data = {
                "total_gacs": 5,
                "total_commits": 5,
                "total_prompt_tokens": 1000,
                "total_output_tokens": 500,
                "total_reasoning_tokens": 0,
                "biggest_gac_tokens": 500,
                "biggest_gac_date": None,
                "first_used": "2025-01-01T00:00:00",
                "last_used": "2025-01-01T00:00:00",
                "daily_gacs": {},
                "daily_commits": {},
                "daily_prompt_tokens": {},
                "daily_output_tokens": {},
                "daily_reasoning_tokens": {},
                "weekly_gacs": {},
                "weekly_commits": {},
                "weekly_prompt_tokens": {},
                "weekly_output_tokens": {},
                "weekly_reasoning_tokens": {},
                "projects": {},
                "models": {},
                "_version": 1,
            }
            save_stats(data)

            loaded = load_stats()
            assert loaded["_version"] == 5
            assert "biggest_gac_commits" in loaded
            assert "biggest_gac_files" in loaded


class TestBiggestGacRecording:
    """Tests for record_gac updating biggest_gac_commits/files."""

    def setup_method(self):
        """Reset accumulator before each test."""
        _accumulator.reset()

    def test_record_gac_updates_biggest_commits(self, tmp_path):
        """record_gac() updates biggest_gac_commits when a new high is set."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            # Record a gac with 3 commits
            record_tokens(100, 50, model="test:model")
            record_commit(model="test:model")
            record_commit(model="test:model")
            record_commit(model="test:model")
            record_gac(model="test:model", files=5)

            stats = load_stats()
            assert stats["biggest_gac_commits"] == 3
            assert stats["biggest_gac_commits_date"] is not None

    def test_record_gac_updates_biggest_files(self, tmp_path):
        """record_gac() updates biggest_gac_files when a new high is set."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            record_tokens(100, 50, model="test:model")
            record_commit(model="test:model")
            record_gac(model="test:model", files=20)

            stats = load_stats()
            assert stats["biggest_gac_files"] == 20
            assert stats["biggest_gac_files_date"] is not None

    def test_record_gac_preserves_bigger_records(self, tmp_path):
        """A smaller gac doesn't overwrite the existing record."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            # First, set a high record
            record_tokens(100, 50, model="test:model")
            record_commit(model="test:model")
            record_commit(model="test:model")
            record_commit(model="test:model")
            record_commit(model="test:model")
            record_commit(model="test:model")
            record_gac(model="test:model", files=30)

            # Now a smaller gac
            _accumulator.reset()
            record_tokens(50, 25, model="test:model")
            record_commit(model="test:model")
            record_gac(model="test:model", files=5)

            stats = load_stats()
            assert stats["biggest_gac_commits"] == 5
            assert stats["biggest_gac_files"] == 30

    def test_record_gac_no_commits_doesnt_update_biggest_commits(self, tmp_path):
        """A gac with 0 commits doesn't set biggest_gac_commits."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            record_tokens(100, 50, model="test:model")
            # No record_commit() calls
            record_gac(model="test:model", files=3)

            stats = load_stats()
            assert stats["biggest_gac_commits"] == 0

    def test_record_gac_no_files_doesnt_update_biggest_files(self, tmp_path):
        """A gac with 0 files doesn't set biggest_gac_files."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            record_tokens(100, 50, model="test:model")
            record_commit(model="test:model")
            record_gac(model="test:model", files=0)

            stats = load_stats()
            assert stats["biggest_gac_files"] == 0

    def test_is_new_biggest_flag_set_for_all_dimensions(self, tmp_path):
        """is_new_biggest is True when any record is set."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            record_tokens(100, 50, model="test:model")
            record_commit(model="test:model")
            record_gac(model="test:model", files=5)

            # is_new_biggest was True during record_gac but reset after
            # We can verify indirectly through the stats
            stats = load_stats()
            assert stats["biggest_gac_tokens"] > 0
            assert stats["biggest_gac_commits"] == 1
            assert stats["biggest_gac_files"] == 5

    def test_reset_stats_clears_biggest_records(self, tmp_path):
        """reset_stats() clears biggest_gac_commits and biggest_gac_files."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            record_tokens(100, 50, model="test:model")
            record_commit(model="test:model")
            record_gac(model="test:model", files=10)

            from gac.stats import reset_stats

            reset_stats()

            stats = load_stats()
            assert stats["biggest_gac_commits"] == 0
            assert stats["biggest_gac_commits_date"] is None
            assert stats["biggest_gac_files"] == 0
            assert stats["biggest_gac_files_date"] is None


class TestBiggestGacSummary:
    """Tests for get_stats_summary including new biggest fields."""

    def test_summary_includes_biggest_commits(self, tmp_path):
        """get_stats_summary includes biggest_gac_commits and date."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            record_tokens(100, 50, model="test:model")
            record_commit(model="test:model")
            record_commit(model="test:model")
            record_gac(model="test:model", files=5)

            from gac.stats.summary import get_stats_summary

            summary = get_stats_summary()
            assert summary["biggest_gac_commits"] == 2
            assert summary["biggest_gac_commits_date"] is not None

    def test_summary_includes_biggest_files(self, tmp_path):
        """get_stats_summary includes biggest_gac_files and date."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            record_tokens(100, 50, model="test:model")
            record_commit(model="test:model")
            record_gac(model="test:model", files=15)

            from gac.stats.summary import get_stats_summary

            summary = get_stats_summary()
            assert summary["biggest_gac_files"] == 15
            assert summary["biggest_gac_files_date"] is not None

    def test_summary_defaults_when_no_gacs(self, tmp_path):
        """get_stats_summary returns 0/None for new fields when no gacs recorded."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            from gac.stats.summary import get_stats_summary

            summary = get_stats_summary()
            assert summary["biggest_gac_commits"] == 0
            assert summary["biggest_gac_commits_date"] is None
            assert summary["biggest_gac_files"] == 0
            assert summary["biggest_gac_files_date"] is None

    def test_summary_date_formatting(self, tmp_path):
        """Dates in summary are formatted as YYYY-MM-DD."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            record_tokens(100, 50, model="test:model")
            record_commit(model="test:model")
            record_gac(model="test:model", files=5)

            from gac.stats.summary import get_stats_summary

            summary = get_stats_summary()
            # Date should be formatted, not raw ISO
            date = summary["biggest_gac_commits_date"]
            if date is not None:
                assert "T" not in date  # formatted as YYYY-MM-DD
            date = summary["biggest_gac_files_date"]
            if date is not None:
                assert "T" not in date


class TestBiggestGacGroupedWorkflow:
    """Tests simulating grouped commit workflow patterns."""

    def setup_method(self):
        """Reset accumulator before each test."""
        _accumulator.reset()

    def test_grouped_gac_multiple_commits_sets_record(self, tmp_path):
        """A grouped gac with multiple commits sets the biggest_gac_commits record."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            # Simulate grouped workflow: tokens recorded once, then multiple commits
            record_tokens(500, 200, model="test:model", reasoning_tokens=50)
            record_commit(model="test:model")
            record_commit(model="test:model")
            record_commit(model="test:model")
            record_commit(model="test:model")
            record_gac(model="test:model", files=12)

            stats = load_stats()
            assert stats["biggest_gac_commits"] == 4
            assert stats["biggest_gac_files"] == 12

    def test_subsequent_smaller_grouped_gac_preserves_record(self, tmp_path):
        """A smaller grouped gac doesn't overwrite the record."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            # First: big grouped gac
            record_tokens(500, 200, model="test:model")
            for _ in range(6):
                record_commit(model="test:model")
            record_gac(model="test:model", files=25)

            _accumulator.reset()

            # Second: smaller gac
            record_tokens(100, 50, model="test:model")
            record_commit(model="test:model")
            record_gac(model="test:model", files=3)

            stats = load_stats()
            assert stats["biggest_gac_commits"] == 6
            assert stats["biggest_gac_files"] == 25

    def test_new_record_only_for_exceeded_dimensions(self, tmp_path):
        """Only the dimensions that exceed previous records are updated."""
        stats_file = tmp_path / "stats.json"
        with patch("gac.stats.store.STATS_FILE", stats_file):
            # First: 3 commits, 10 files
            record_tokens(100, 50, model="test:model")
            record_commit(model="test:model")
            record_commit(model="test:model")
            record_commit(model="test:model")
            record_gac(model="test:model", files=10)

            _accumulator.reset()

            # Second: 2 commits (less), 15 files (more)
            record_tokens(100, 50, model="test:model")
            record_commit(model="test:model")
            record_commit(model="test:model")
            record_gac(model="test:model", files=15)

            stats = load_stats()
            assert stats["biggest_gac_commits"] == 3  # Unchanged
            assert stats["biggest_gac_files"] == 15  # Updated
