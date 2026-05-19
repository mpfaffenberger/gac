"""Stats recording — functions that write usage data on each gac/commit/token event."""

import logging
from datetime import datetime
from typing import Any

import gac.stats.store as store

logger = logging.getLogger(__name__)

# Module-level accumulator for per-gac token totals.
# record_tokens() adds to this; record_gac() finalizes it and resets.
#
# ⚠️  MAINTAINER NOTE: Any code path that calls record_tokens() but does NOT
# call record_gac() (e.g. dry_run, message_only, user abort, generation
# failure) MUST call reset_gac_token_accumulator() before returning.
# Without this, a long-lived process (MCP server) will leak leftover
# tokens into the next successful request and inflate biggest_gac_tokens.


class TokenAccumulator:
    """Encapsulated mutable state for per-gac token and metadata tracking.

    Collects per-gac data across record_tokens() and record_commit() calls,
    then finalized by record_gac() which writes a history record.
    """

    def __init__(self) -> None:
        self._current_tokens: int = 0
        self._prompt_tokens: int = 0
        self._output_tokens: int = 0
        self._reasoning_tokens: int = 0
        self._duration_ms: int = 0
        self._commits: int = 0
        self._files: int = 0
        self._model: str | None = None
        self._project: str | None = None
        self._started_at: datetime | None = None
        self.is_new_biggest: bool = False

    def add(self, tokens: int) -> None:
        self._current_tokens += tokens

    def add_tokens(self, prompt: int, output: int, reasoning: int, duration_ms: int = 0) -> None:
        """Record token details and duration for the current gac."""
        self._prompt_tokens += prompt
        self._output_tokens += output
        self._reasoning_tokens += reasoning
        self._duration_ms += duration_ms
        self._current_tokens += prompt + output + reasoning

    def add_commit(self) -> None:
        """Increment the commit counter for the current gac."""
        self._commits += 1

    def set_files(self, count: int) -> None:
        """Set the file count for the current gac."""
        self._files = count

    def set_meta(self, model: str | None, project: str | None) -> None:
        """Set model and project for the current gac (first call wins for started_at)."""
        if self._started_at is None:
            self._started_at = datetime.now()
        self._model = model or self._model
        self._project = project or self._project

    def reset(self) -> None:
        self._current_tokens = 0
        self._prompt_tokens = 0
        self._output_tokens = 0
        self._reasoning_tokens = 0
        self._duration_ms = 0
        self._commits = 0
        self._files = 0
        self._model = None
        self._project = None
        self._started_at = None
        self.is_new_biggest = False

    @property
    def current(self) -> int:
        return self._current_tokens

    @property
    def has_data(self) -> bool:
        return self._current_tokens > 0 or self._commits > 0


# Module-level singleton — existing code continues to work
_accumulator = TokenAccumulator()


def reset_gac_token_accumulator() -> None:
    """Reset the per-gac token accumulator.

    Call this on **every** code path where ``record_tokens()`` was invoked
    but ``record_gac()`` will not be (e.g. ``message_only``, ``dry_run``,
    user abort, generation failure).  Without this, a long-lived process
    (MCP server) would leak leftover tokens into the next successful
    request and inflate ``biggest_gac_tokens``.

    One-shot CLI invocations do not strictly need this (the process
    exits), but calling it is good hygiene and keeps code paths
    consistent between CLI and MCP.
    """
    _accumulator.reset()


def _set_new_biggest_gac(value: bool) -> None:
    """Internal setter for _new_biggest_gac flag (used by reset_stats)."""
    _accumulator.is_new_biggest = value


def record_gac(project_name: str | None = None, model: str | None = None, files: int = 0) -> None:
    """Record a gac workflow run in the statistics.

    Args:
        project_name: Name of the project. Auto-detected from git if not provided.
        model: Name of the AI model used for this gac (e.g. 'anthropic:claude-haiku-4-5').
        files: Number of files included in this gac.

    This should be called when a gac workflow completes successfully.

    Does nothing if GAC_DISABLE_STATS environment variable is set.
    """
    if not store.stats_enabled():
        return

    if project_name is None:
        project_name = store.get_current_project_name()

    # Track metadata for the per-gac history record.
    # Commits are counted via record_commit(), not here.
    _accumulator.set_meta(model, project_name)

    stats = store.load_stats()
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")

    # Update total gacs
    stats["total_gacs"] += 1

    # Set first_used if this is the first gac
    if stats["first_used"] is None:
        stats["first_used"] = now.isoformat()

    # Update last_used
    stats["last_used"] = now.isoformat()

    # Update daily gac count
    if today not in stats["daily_gacs"]:
        stats["daily_gacs"][today] = 0
    stats["daily_gacs"][today] += 1

    # Update weekly gac count
    iso_week = now.isocalendar()
    week_key = f"{iso_week[0]}-W{iso_week[1]:02d}"
    if week_key not in stats["weekly_gacs"]:
        stats["weekly_gacs"][week_key] = 0
    stats["weekly_gacs"][week_key] += 1

    # Update project stats
    if project_name:
        if project_name not in stats["projects"]:
            stats["projects"][project_name] = {
                "gacs": 0,
                "commits": 0,
                "prompt_tokens": 0,
                "output_tokens": 0,
                "total_files": 0,
            }
        stats["projects"][project_name]["gacs"] += 1
        if files > 0:
            stats["projects"][project_name]["total_files"] = (
                stats["projects"][project_name].get("total_files", 0) + files
            )

    # Update model stats
    if model:
        if model not in stats["models"]:
            stats["models"][model] = {
                "gacs": 0,
                "commits": 0,
                "prompt_tokens": 0,
                "output_tokens": 0,
                "total_duration_ms": 0,
                "duration_count": 0,
                "timed_output_tokens": 0,
                "timed_reasoning_tokens": 0,
                "min_duration_ms": 0,
                "max_duration_ms": 0,
            }
        stats["models"][model]["gacs"] += 1

    # Finalize per-gac records: check if this gac is the biggest ever
    _accumulator.is_new_biggest = False
    if _accumulator.current > 0 and _accumulator.current > stats.get("biggest_gac_tokens", 0):
        stats["biggest_gac_tokens"] = _accumulator.current
        stats["biggest_gac_date"] = now.isoformat()
        _accumulator.is_new_biggest = True
    if _accumulator._commits > 0 and _accumulator._commits > stats.get("biggest_gac_commits", 0):
        stats["biggest_gac_commits"] = _accumulator._commits
        stats["biggest_gac_commits_date"] = now.isoformat()
        _accumulator.is_new_biggest = True
    if files > 0 and files > stats.get("biggest_gac_files", 0):
        stats["biggest_gac_files"] = files
        stats["biggest_gac_files_date"] = now.isoformat()
        _accumulator.is_new_biggest = True

    # Write per-gac history record (ring buffer, capped at HISTORY_CAP)
    if _accumulator.has_data:
        history_record: dict[str, Any] = {
            "ts": (_accumulator._started_at or now).isoformat(),
            "project": project_name,
            "model": model or _accumulator._model,
            "prompt_tokens": _accumulator._prompt_tokens,
            "output_tokens": _accumulator._output_tokens,
            "reasoning_tokens": _accumulator._reasoning_tokens,
            "duration_ms": _accumulator._duration_ms,
            "commits": _accumulator._commits,
        }
        if files > 0:
            history_record["files"] = files
        store.append_history(stats, history_record)

    _accumulator.reset()

    store.save_stats(stats)
    logger.debug(f"Recorded gac. Total gacs: {stats['total_gacs']}")


def record_commit(project_name: str | None = None, model: str | None = None) -> None:
    """Record a successful commit in the statistics.

    Args:
        project_name: Name of the project. Auto-detected from git if not provided.
        model: Name of the AI model used for this commit (e.g. 'anthropic:claude-haiku-4-5').

    This should be called after a commit is successfully created.

    Does nothing if GAC_DISABLE_STATS environment variable is set.
    """
    if not store.stats_enabled():
        return

    if project_name is None:
        project_name = store.get_current_project_name()

    # Track per-gac commit count for history records.
    _accumulator.add_commit()
    _accumulator.set_meta(model, project_name)

    stats = store.load_stats()
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")

    # Update total commits
    stats["total_commits"] += 1

    # Update daily commit count
    if today not in stats["daily_commits"]:
        stats["daily_commits"][today] = 0
    stats["daily_commits"][today] += 1

    # Update weekly commit count
    iso_week = now.isocalendar()
    week_key = f"{iso_week[0]}-W{iso_week[1]:02d}"
    if week_key not in stats["weekly_commits"]:
        stats["weekly_commits"][week_key] = 0
    stats["weekly_commits"][week_key] += 1

    # Update last_used on every commit
    stats["last_used"] = now.isoformat()

    # Update project stats
    if project_name:
        if project_name not in stats["projects"]:
            stats["projects"][project_name] = {
                "gacs": 0,
                "commits": 0,
                "prompt_tokens": 0,
                "output_tokens": 0,
                "total_files": 0,
            }
        stats["projects"][project_name]["commits"] += 1

    # Update model commit stats
    if model:
        if model not in stats["models"]:
            stats["models"][model] = {
                "gacs": 0,
                "commits": 0,
                "prompt_tokens": 0,
                "output_tokens": 0,
                "total_duration_ms": 0,
                "duration_count": 0,
                "timed_output_tokens": 0,
                "timed_reasoning_tokens": 0,
                "min_duration_ms": 0,
                "max_duration_ms": 0,
            }
        stats["models"][model]["commits"] = stats["models"][model].get("commits", 0) + 1

    store.save_stats(stats)
    logger.debug(f"Recorded commit. Total commits: {stats['total_commits']}")


def record_tokens(
    prompt_tokens: int,
    output_tokens: int,
    model: str | None = None,
    project_name: str | None = None,
    duration_ms: int | None = None,
    reasoning_tokens: int = 0,
) -> None:
    """Record token usage for an AI generation call.

    Args:
        prompt_tokens: Number of prompt (input) tokens used.
        output_tokens: Number of output (text) tokens used (excludes reasoning).
        model: Name of the AI model used (e.g. 'anthropic:claude-haiku-4-5').
        project_name: Name of the project. Auto-detected from git if not provided.
        duration_ms: Wall-clock duration of the API call in milliseconds. When provided and > 0,
            per-model speed tracking fields are updated.
        reasoning_tokens: Number of reasoning/thinking tokens used by the model.

    Does nothing if GAC_DISABLE_STATS environment variable is set.
    """
    if not store.stats_enabled():
        return

    if prompt_tokens <= 0 and output_tokens <= 0 and reasoning_tokens <= 0:
        return

    if project_name is None:
        project_name = store.get_current_project_name()

    stats = store.load_stats()
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    iso_week = now.isocalendar()
    week_key = f"{iso_week[0]}-W{iso_week[1]:02d}"

    stats["total_prompt_tokens"] += prompt_tokens
    stats["total_output_tokens"] = stats.get("total_output_tokens", 0) + output_tokens
    stats["total_reasoning_tokens"] = stats.get("total_reasoning_tokens", 0) + reasoning_tokens

    # Accumulate into per-gac token total (finalized by record_gac)
    _accumulator.add_tokens(prompt_tokens, output_tokens, reasoning_tokens, duration_ms or 0)
    _accumulator.set_meta(model, project_name)

    stats["daily_prompt_tokens"][today] = stats["daily_prompt_tokens"].get(today, 0) + prompt_tokens
    stats["daily_output_tokens"][today] = stats.get("daily_output_tokens", {}).get(today, 0) + output_tokens
    stats["daily_reasoning_tokens"][today] = stats.get("daily_reasoning_tokens", {}).get(today, 0) + reasoning_tokens
    stats["weekly_prompt_tokens"][week_key] = stats["weekly_prompt_tokens"].get(week_key, 0) + prompt_tokens
    stats["weekly_output_tokens"][week_key] = stats.get("weekly_output_tokens", {}).get(week_key, 0) + output_tokens
    stats["weekly_reasoning_tokens"][week_key] = (
        stats.get("weekly_reasoning_tokens", {}).get(week_key, 0) + reasoning_tokens
    )

    if project_name:
        if project_name not in stats["projects"]:
            stats["projects"][project_name] = {
                "gacs": 0,
                "commits": 0,
                "prompt_tokens": 0,
                "output_tokens": 0,
                "reasoning_tokens": 0,
                "total_files": 0,
            }
        proj = stats["projects"][project_name]
        proj["prompt_tokens"] = proj.get("prompt_tokens", 0) + prompt_tokens
        proj["output_tokens"] = proj.get("output_tokens", 0) + output_tokens
        proj["reasoning_tokens"] = proj.get("reasoning_tokens", 0) + reasoning_tokens

    if model:
        if model not in stats["models"]:
            stats["models"][model] = {
                "gacs": 0,
                "commits": 0,
                "prompt_tokens": 0,
                "output_tokens": 0,
                "reasoning_tokens": 0,
                "total_duration_ms": 0,
                "duration_count": 0,
                "timed_output_tokens": 0,
                "timed_reasoning_tokens": 0,
                "min_duration_ms": 0,
                "max_duration_ms": 0,
            }
        m = stats["models"][model]
        m["prompt_tokens"] = m.get("prompt_tokens", 0) + prompt_tokens
        m["output_tokens"] = m.get("output_tokens", 0) + output_tokens
        m["reasoning_tokens"] = m.get("reasoning_tokens", 0) + reasoning_tokens
        if duration_ms is not None and duration_ms > 0:
            m["total_duration_ms"] = m.get("total_duration_ms", 0) + duration_ms
            m["duration_count"] = m.get("duration_count", 0) + 1
            m["timed_output_tokens"] = m.get("timed_output_tokens", 0) + output_tokens
            m["timed_reasoning_tokens"] = m.get("timed_reasoning_tokens", 0) + reasoning_tokens
            if m.get("duration_count", 0) == 1:
                m["min_duration_ms"] = duration_ms
                m["max_duration_ms"] = duration_ms
            else:
                m["min_duration_ms"] = min(m.get("min_duration_ms", 0), duration_ms)
                m["max_duration_ms"] = max(m.get("max_duration_ms", 0), duration_ms)

    store.save_stats(stats)
    logger.debug(
        f"Recorded tokens. Total prompt: {stats['total_prompt_tokens']}, output: {stats.get('total_output_tokens', 0)}"
    )
