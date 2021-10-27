from dataclasses import dataclass
from pathlib import Path
from typing import List

from sqlfmt.mode import Mode


@dataclass
class SqlFormatResult:
    source_path: Path
    source_string: str
    formatted_string: str

    @property
    def has_changed(self) -> bool:
        return self.source_string != self.formatted_string


@dataclass
class Report:
    """
    An abstraction for a summary of results generated by a sqlfmt run.
    Can be printed using str()
    """

    results: List[SqlFormatResult]
    mode: Mode

    def __str__(self) -> str:
        report = []
        formatted = (
            "formatted" if self.mode.output == "update" else "failed formatting check"
        )
        unchanged = (
            "left unchanged"
            if self.mode.output == "update"
            else "passed formatting check"
        )
        if self.number_changed > 0:
            report.append(f"{self._pluralize_file(self.number_changed)} {formatted}.")
        report.append(f"{self._pluralize_file(self.number_unchanged)} {unchanged}.")
        for res in self.changed_results:
            report.append(f"{res.source_path} {formatted}.")
        if self.mode.verbose:
            for res in self.unchanged_results:
                report.append(f"{res.source_path} {unchanged}.")
        return "\n".join(report)

    @staticmethod
    def _pluralize_file(n: int) -> str:
        suffix = "s" if n != 1 else ""
        return f"{n} file{suffix}"

    @property
    def number_of_results(self) -> int:
        return len(self.results)

    @property
    def changed_results(self) -> List[SqlFormatResult]:
        return self._filtered_results(has_changed=True)

    @property
    def unchanged_results(self) -> List[SqlFormatResult]:
        return self._filtered_results(has_changed=False)

    def _filtered_results(self, has_changed: bool = True) -> List[SqlFormatResult]:
        filtered = [r for r in self.results if r.has_changed == has_changed]
        return sorted(filtered, key=lambda res: res.source_path)

    @property
    def number_changed(self) -> int:
        return len(self.changed_results)

    @property
    def number_unchanged(self) -> int:
        return self.number_of_results - self.number_changed