from datetime import datetime
import re

# Robust log parser with strict validations + advanced checks
class LogParser:

    VALID_LOG_LEVELS = {"INFO", "WARNING", "ERROR", "DEBUG", "CRITICAL"}
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
    COMPONENT_REGEX = re.compile(r"^[A-Za-z0-9_]+$")

    # Ensures the log line has exactly 4 fields.
    def validate_field_count(self, parts: list) -> None:

        # Existing validation (kept as-is)
        if len(parts) != 4:
            raise ValueError(
                f"Invalid field count. Expected 4, got {len(parts)}"
            )

        # Additional complex validations
        for index, part in enumerate(parts):
            if part is None:
                raise ValueError(f"Field at index {index} is None")

            if not isinstance(part, str):
                raise ValueError(f"Field at index {index} must be a string")

            if part.strip() == "":
                raise ValueError(f"Field at index {index} cannot be empty")

    # Validates timestamp format.
    def validate_timestamp(self, timestamp: str) -> datetime:

        
        try:
            parsed_time = datetime.strptime(timestamp, self.TIMESTAMP_FORMAT)
        except ValueError:
            raise ValueError(
                f"Invalid timestamp format: {timestamp}. "
                f"Expected format: YYYY-MM-DD HH:MM:SS"
            )

        # Additional complex validations
        now = datetime.utcnow()
        earliest_allowed = datetime(2000, 1, 1)

        if parsed_time > now:
            raise ValueError("Timestamp cannot be in the future")

        if parsed_time < earliest_allowed:
            raise ValueError("Timestamp is unrealistically old")

        return parsed_time

    # Validates log level against allowed values.
    def validate_log_level(self, level: str) -> None:

        # Existing validation (kept as-is)
        if level not in self.VALID_LOG_LEVELS:
            raise ValueError(
                f"Invalid log level: {level}. "
                f"Allowed values: {', '.join(self.VALID_LOG_LEVELS)}"
            )

        # Additional complex validations
        if level != level.strip():
            raise ValueError("Log level must not contain leading/trailing spaces")

        if not level.isupper():
            raise ValueError("Log level must be uppercase")

    # Validates component naming and message content.
    def validate_component_and_message(self, component: str, message: str) -> None:

        if not component:
            raise ValueError("Component cannot be empty")

        if not self.COMPONENT_REGEX.match(component):
            raise ValueError(
                f"Invalid component name: {component}. "
                "Only alphanumeric characters and underscores are allowed."
            )

        if not message or not message.strip():
            raise ValueError("Log message cannot be empty")

        if len(message) > 10_000:
            raise ValueError("Log message exceeds maximum allowed length")

        # Additional complex validations
        if component[0].isdigit():
            raise ValueError("Component name cannot start with a digit")

        if "__" in component:
            raise ValueError("Component name should not contain consecutive underscores")

        # Detect possible log injection patterns
        suspicious_patterns = [
            r"\n",           # multiline injection
            r"\r",
            r"\x00",         # null byte
            r"\t{2,}",       # excessive tabs
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, message):
                raise ValueError("Log message contains suspicious or unsafe characters")

        # Ensure message is not only symbols
        if re.fullmatch(r"[^\w\s]+", message):
            raise ValueError("Log message cannot consist only of special characters")

    # Parses and validates a single log line.
    def parse_line(self, line: str) -> dict:

        # Existing validation (kept as-is)
        if not line or not line.strip():
            raise ValueError("Empty log line")

        # Additional complex validations
        if len(line) > 12000:
            raise ValueError("Log line exceeds maximum allowed size")

        if "\0" in line:
            raise ValueError("Log line contains null byte")

        parts = line.strip().split("\t")

        # Validation 1
        self.validate_field_count(parts)

        timestamp, level, component, message = parts

        # Validation 2
        parsed_timestamp = self.validate_timestamp(timestamp)

        # Validation 3
        self.validate_log_level(level)

        # Validation 4
        self.validate_component_and_message(component, message)

        return {
            "timestamp": timestamp,
            "level": level,
            "component": component,
            "message": message,
            "parsed_timestamp": parsed_timestamp
        }
