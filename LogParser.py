from datetime import datetime
import re

#Robust log parser with strict validations.
class LogParser:
 
    VALID_LOG_LEVELS = {"INFO", "WARNING", "ERROR", "DEBUG", "CRITICAL"}
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
    COMPONENT_REGEX = re.compile(r"^[A-Za-z0-9_]+$")

    #Ensures the log line has exactly 4 fields.
    def validate_field_count(self, parts: list) -> None:
        
        if len(parts) != 4:
            raise ValueError(
                f"Invalid field count. Expected 4, got {len(parts)}"
            )
        
    #Validates timestamp format.
    def validate_timestamp(self, timestamp: str) -> datetime:
       
        try:
            return datetime.strptime(timestamp, self.TIMESTAMP_FORMAT)
        except ValueError:
            raise ValueError(
                f"Invalid timestamp format: {timestamp}. "
                f"Expected format: YYYY-MM-DD HH:MM:SS"
            )
        
    #Validates log level against allowed values.
    def validate_log_level(self, level: str) -> None:

        if level not in self.VALID_LOG_LEVELS:
            raise ValueError(
                f"Invalid log level: {level}. "
                f"Allowed values: {', '.join(self.VALID_LOG_LEVELS)}"
            )
        
    #Validates component naming and message content.
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
        
    #Parses and validates a single log line.
    def parse_line(self, line: str) -> dict:
        
        if not line or not line.strip():
            raise ValueError("Empty log line")

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
