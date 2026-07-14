from __future__ import annotations

from datetime import datetime, timedelta, timezone
import subprocess

from system.core.business_registry import get_business
from system.core.path_resolver import get_repo_root
from system.scripts.analytics.providers import AnalyticsFetchError, AnalyticsFetchResult, AnalyticsProvider, register_provider

# Every real platform provider (X, Threads, note.com) needs paid/gated API
# access this repo does not have yet (see providers.py's DryRunProvider
# docstring). That left pdca with literally nothing non-dry_run to Check
# against for any business, ever. This provider is an honest interim proxy,
# not a placeholder pretending to be real platform data: it reports actual,
# verifiable repository activity for a business's own content/code paths
# (commit cadence, distinct files touched, days since last commit), sourced
# from local git history. Clearly labeled as such in `notes` so it is never
# mistaken for audience/engagement metrics.

LOOKBACK_DAYS = 30


class GitActivityProvider(AnalyticsProvider):
    """Real (non-dry_run), credential-free proxy metrics from this business's
    own git history. Not a substitute for real platform analytics (no
    audience/impression/engagement data here) -- a Check signal for pdca
    that costs nothing and needs no vendor API access."""

    name = "git_activity"

    def fetch(self, business_id: str) -> AnalyticsFetchResult:
        record = get_business(business_id)
        if record is None:
            raise AnalyticsFetchError(f"Unknown business_id '{business_id}' in business_registry.")

        paths = list(dict.fromkeys(p for p in (record.content_root, record.product_code_path) if p))
        if not paths:
            return AnalyticsFetchResult(
                provider=self.name,
                business_id=business_id,
                metrics={},
                fetched_at=datetime.now(timezone.utc).isoformat(),
                notes=(
                    f"'{business_id}' has no content_root/product_code_path in business_registry yet "
                    "(greenfield business) -- nothing to measure."
                ),
            )

        since = (datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")
        repo_root = get_repo_root()

        commit_hashes: set[str] = set()
        touched_files: set[str] = set()
        for path in paths:
            log_output = self._git_log(repo_root, path, since)
            for line in log_output.splitlines():
                if line.startswith("commit:"):
                    commit_hashes.add(line.split(":", 1)[1])
                elif line.strip():
                    touched_files.add(line.strip())

        last_commit_iso = self._last_commit_date(repo_root, paths)
        if last_commit_iso:
            last_commit_dt = datetime.fromisoformat(last_commit_iso)
            days_since_last_commit = (datetime.now(timezone.utc) - last_commit_dt).days
        else:
            days_since_last_commit = -1  # no commits ever touched these paths

        metrics = {
            f"commits_last_{LOOKBACK_DAYS}d": float(len(commit_hashes)),
            f"files_touched_last_{LOOKBACK_DAYS}d": float(len(touched_files)),
            "days_since_last_commit": float(days_since_last_commit),
        }
        return AnalyticsFetchResult(
            provider=self.name,
            business_id=business_id,
            metrics=metrics,
            fetched_at=datetime.now(timezone.utc).isoformat(),
            notes=(
                "Repository-activity proxy, not real platform audience/engagement data -- "
                f"measured over {', '.join(paths)}. No real platform (X/Threads/note.com) "
                "provider is configured yet; see providers.py."
            ),
        )

    @staticmethod
    def _git_log(repo_root, path: str, since: str) -> str:
        result = subprocess.run(
            ["git", "log", f"--since={since}", "--pretty=format:commit:%H", "--name-only", "--", path],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout

    @staticmethod
    def _last_commit_date(repo_root, paths: list[str]) -> str | None:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%aI", "--", *paths],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        output = result.stdout.strip()
        return output or None


register_provider(GitActivityProvider)
