
from enum import Enum


class UpdateResult:
    class Status(Enum):
        UPDATED = "updated"
        UNCHANGED = "unchanged"
        FAILED = "failed"

    def __init__(self):
        # Create default empty array for each status
        self._result = {status: [] for status in UpdateResult.Status}

    def __str__(self):
        return self.summary

    @property
    def updated(self) -> list[dict]:
        return self._result.get(UpdateResult.Status.UPDATED)

    @property
    def unchanged(self) -> list[dict]:
        return self._result.get(UpdateResult.Status.UNCHANGED)

    @property
    def failed(self) -> list[dict]:
        return self._result.get(UpdateResult.Status.FAILED)

    @property
    def error(self) -> str:
        if len(self.failed) > 0:
            failed_records = "\n".join(
                [f"  {record.get('error')}" for record in self.failed])
            return f"failed record(s): \n{failed_records}"

    @property
    def summary(self) -> str:
        result = []
        if len(self.updated) > 0:
            result.append(f"updated: {len(self.updated)}")
        if len(self.unchanged) > 0:
            result.append(f"unchanged: {len(self.unchanged)}")
        if len(self.failed) > 0:
            result.append(f"failed: {len(self.failed)}")

        return ", ".join(result)

    @property
    def updates(self) -> str:
        updates = []
        for update in self.updated:
            changes = update.get('changes')
            change_list = []
            for field, change in changes.items():
                change_list.append(
                    f"    {field}: {change.get('old')} -> {change.get('new')}")
            change_str = '\n'.join(change_list)
            updates.append(
                f"  Record - id:{update.get('id')} issue_number:{update.get('issue_number')} \n{change_str}")
        return '\n'.join(updates)

    def add_record_status(self, context: dict, status: Status):
        self._result.get(status).append(context)
