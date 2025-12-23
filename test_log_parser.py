"""
Unit tests for LogParser class.

Tests cover valid parsing, field validation, timestamp rules, message content,
and security checks against injection attacks.

Author: Nagdatt Gajjam
Email: nagdatt.h.gajjam@gmail.com
Created: 2025-12-23
"""

import pytest
from log_parser import LogParser  
from datetime import datetime


@pytest.fixture
def parser():
    return LogParser()


# Test valid log line parsing
def test_valid_log_line(parser):
    log = "2025-05-07 10:00:00\tINFO\tUserAuth\tUser logged in successfully"
    result = parser.parse_line(log)

    assert result["level"] == "INFO"
    assert result["component"] == "UserAuth"
    assert isinstance(result["parsed_timestamp"], datetime)


# Test invalid number of fields
@pytest.mark.parametrize("log", [
    "2025-05-07 10:00:00\tINFO\tUserAuth",                        
    "2025-05-07 10:00:00\tINFO\tUserAuth\tMsg\tExtra",          
])
def test_invalid_field_count(parser, log):
    with pytest.raises(ValueError, match="Invalid field count"):
        parser.parse_line(log)


# Test empty fields
def test_empty_field(parser):
    log = "2025-05-07 10:00:00\tINFO\t\tMessage"
    with pytest.raises(ValueError):
        parser.parse_line(log)


# Test completely empty log lines
@pytest.mark.parametrize("log", ["", "   "])
def test_empty_log_line(parser, log):
    with pytest.raises(ValueError, match="Empty log line"):
        parser.parse_line(log)


# Test null byte injection
def test_null_byte_in_line(parser):
    log = "2025-05-07 10:00:00\tINFO\tUserAuth\tTest\0Message"
    with pytest.raises(ValueError):
        parser.parse_line(log)


# Test invalid timestamp formats
@pytest.mark.parametrize("log", [
    "07-05-2025 10:00:00\tINFO\tUserAuth\tBad format",
    "2025-02-30 10:00:00\tINFO\tUserAuth\tInvalid date",
])
def test_invalid_timestamp_format(parser, log):
    with pytest.raises(ValueError):
        parser.parse_line(log)



# Test invalid log levels
@pytest.mark.parametrize("log", [
    "2025-05-07 10:00:00\tTRACE\tUserAuth\tInvalid level",
    "2025-05-07 10:00:00\tinfo\tUserAuth\tLowercase level",
    "2025-05-07 10:00:00\t INFO \tUserAuth\tSpaced level",
])
def test_invalid_log_level(parser, log):
    with pytest.raises(ValueError):
        parser.parse_line(log)


# Test invalid component names
@pytest.mark.parametrize("log", [
    "2025-05-07 10:00:00\tINFO\t\tEmpty component",
    "2025-05-07 10:00:00\tINFO\tUser-Auth\tInvalid char",
    "2025-05-07 10:00:00\tINFO\t1UserAuth\tStarts with digit",
    "2025-05-07 10:00:00\tINFO\tUser__Auth\tDouble underscore",
])
def test_invalid_component(parser, log):
    with pytest.raises(ValueError):
        parser.parse_line(log)


# Test invalid message content
@pytest.mark.parametrize("log", [
    "2025-05-07 10:00:00\tINFO\tUserAuth\t",           # empty message
    "2025-05-07 10:00:00\tINFO\tUserAuth\t    ",       # spaces only
    "2025-05-07 10:00:00\tINFO\tUserAuth\t@@@@@@@",    # only symbols
])
def test_invalid_message_content(parser, log):
    with pytest.raises(ValueError):
        parser.parse_line(log)


# Test newline injection attempts
def test_message_with_newline_injection(parser):
    log = "2025-05-07 10:00:00\tINFO\tUserAuth\tUser logged in\nInjected"
    with pytest.raises(ValueError):
        parser.parse_line(log)


# Test carriage return injection
def test_message_with_carriage_return(parser):
    log = "2025-05-07 10:00:00\tINFO\tUserAuth\tCRLF\rAttack"
    with pytest.raises(ValueError):
        parser.parse_line(log)


# Test excessive tabs in message
def test_message_with_excessive_tabs(parser):
    log = "2025-05-07 10:00:00\tINFO\tUserAuth\tTab\t\tInjection"
    with pytest.raises(ValueError):
        parser.parse_line(log)


# Test excessively long message
def test_message_too_long(parser):
    long_message = "A" * 10001
    log = f"2025-05-07 10:00:00\tINFO\tUserAuth\t{long_message}"
    with pytest.raises(ValueError):
        parser.parse_line(log)


# Test excessively long entire log line
def test_log_line_too_long(parser):
    long_line = "A" * 12001
    with pytest.raises(ValueError):
        parser.parse_line(long_line)

# Test invalid log level fails
def test_invalid_log_level_fails(parser):
    log = "2025-05-07 10:00:00\tTRACE\tUserAuth\tInvalid log level"
    with pytest.raises(ValueError, match="Invalid log level"):
        parser.parse_line(log)