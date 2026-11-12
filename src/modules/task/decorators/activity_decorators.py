

from datetime import datetime
from enum import Enum
from functools import wraps
from inspect import signature
from collections.abc import Callable

from sqlalchemy.orm import Session

from src.models.task import TaskActivityField
from src.modules.task.services.activity_service import create_task_activity


def convert_value(value):
    """Convert values into strings for activity records."""

    if value is None:
        return None

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    return str(value)


def track_activity(
    field: TaskActivityField | None = None,
    new_value_attr: str | None = None,
    old_value_attr: str | None = None,
    tracked_fields: dict | None = None,
    loader: Callable | None = None,
    loader_args: tuple[str, ...] = (),
):
    """Automatically create activity records after an operation."""

    def decorator(func):
        function_signature = signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_arguments = function_signature.bind(*args, **kwargs)
            bound_arguments.apply_defaults()

            arguments = bound_arguments.arguments
            session: Session = arguments["session"]
            user_id = arguments["user_id"]

            try:
                old_values = {}
                old_value = None
                tracked_object = None

                # Load the record before the operation when needed.
                if tracked_fields or old_value_attr is not None:
                    if loader is None:
                        raise ValueError(
                            "A loader is required to capture old values."
                        )

                    loader_arguments = {
                        name: arguments[name] for name in loader_args
                    }

                    tracked_object = loader(
                        session=session,
                        **loader_arguments,
                    )

                    if tracked_object is None:
                        raise ValueError("Tracked record not found.")

                # Capture old values for field updates.
                if tracked_fields:
                    old_values = {
                        name: getattr(tracked_object, name)
                        for name in tracked_fields
                    }

                # Capture one old value for single activity.
                if old_value_attr is not None:
                    old_value = getattr(tracked_object, old_value_attr)

                # Execute original service function.
                result = func(*args, **kwargs)

                task_id = arguments.get("task_id") or getattr(
                    result, "task_id", None
                )

                if task_id is None:
                    raise ValueError(
                        "Task ID not found for activity tracking."
                    )

                # Create activities for changed fields.
                if tracked_fields:
                    for field_name, activity_field in tracked_fields.items():
                        old_field_value = old_values[field_name]
                        new_field_value = getattr(result, field_name, None)

                        if old_field_value != new_field_value:
                            create_task_activity(
                                session=session,
                                task_id=task_id,
                                user_id=user_id,
                                field=activity_field,
                                old_value=convert_value(old_field_value),
                                new_value=convert_value(new_field_value),
                            )

                # Create a single activity.
                elif field is not None:
                    new_value = (
                        getattr(result, new_value_attr, None)
                        if new_value_attr is not None
                        else None
                    )

                    create_task_activity(
                        session=session,
                        task_id=task_id,
                        user_id=user_id,
                        field=field,
                        old_value=convert_value(old_value),
                        new_value=convert_value(new_value),
                    )

                session.commit()
                return result

            except Exception:
                session.rollback()
                raise

        return wrapper

    return decorator
