"""
Flask-based log viewer API.

Endpoints:
- List and filter logs (/logs)
- View individual log by ID (/logs/<id>)
- Get basic statistics (/logs/stats)
- List with pagination (/logs/pagination)


Author: Nagdatt Gajjam
Created: 2025-12-23 
"""

from log_parser import LogParser
import uuid
from flask import Flask, jsonify, request, abort
from datetime import datetime
import os

parser = LogParser()

app = Flask(__name__)

LOG_DIR = "logs"
logs = []

#  Reads all log files from LOG_DIR and parses them into memory.
def load_logs():
    
    global logs

    for file_name in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, file_name)

        if not os.path.isfile(file_path):
            continue

        with open(file_path, "r") as file:
            for line in file:
                try:
                    parsed = parser.parse_line(line)
                    logs.append({
                        "id": str(uuid.uuid4()),
                        "timestamp": parsed["timestamp"],
                        "level": parsed["level"],
                        "component": parsed["component"],
                        "message": parsed["message"]
                    })
                except ValueError as e:
                    # Skip invalid log entries 
                    print(f"Skipping invalid log line: {e}")


def parse_time(time_str):
    return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")


@app.route("/logs", methods=["GET"])
def get_logs():
    load_logs()
    result = logs

    level = request.args.get("level")
    component = request.args.get("component")
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")

    if level:
        result = [log for log in result if log["level"] == level]

    if component:
        result = [log for log in result if log["component"] == component]

    if start_time:
        try:
            start_dt = parse_time(start_time)
            result = [
                log for log in result
                if parse_time(log["timestamp"]) >= start_dt
            ]
        except ValueError:
            abort(400, "Invalid start_time format")

    if end_time:
        try:
            end_dt = parse_time(end_time)
            result = [
                log for log in result
                if parse_time(log["timestamp"]) <= end_dt
            ]
        except ValueError:
            abort(400, "Invalid end_time format")  

    return jsonify(result)


@app.route("/logs/stats", methods=["GET"])
def get_stats():
    total = len(logs)
    by_level = {}
    by_component = {}

    for log in logs:
        by_level[log["level"]] = by_level.get(log["level"], 0) + 1
        by_component[log["component"]] = by_component.get(log["component"], 0) + 1

    return jsonify({
        "total_logs": total,
        "logs_by_level": by_level,
        "logs_by_component": by_component
    })


@app.route("/logs/<string:log_id>", methods=["GET"])
def get_log_by_id(log_id):
    for log in logs:
        if log["id"] == log_id:
            return jsonify(log)

    abort(404, "Log ID not found")


@app.route("/logs/pagination", methods=["GET"])
def logs_with_pagination():
    result = logs

    level = request.args.get("level")
    component = request.args.get("component")
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")

    if level:
        result = [log for log in result if log["level"] == level]
    if component:
        result = [log for log in result if log["component"] == component]
    if start_time:
        try:
            start_dt = parse_time(start_time)
            result = [log for log in result if parse_time(log["timestamp"]) >= start_dt]
        except ValueError:
            abort(400, "Invalid start_time format")
    if end_time:
        try:
            end_dt = parse_time(end_time)
            result = [log for log in result if parse_time(log["timestamp"]) <= end_dt]
        except ValueError:
            abort(400, "Invalid end_time format")

    try:
        # Default to page 1 and size 10 if not provided
        page_number = int(request.args.get("page_number", 1))
        page_size = int(request.args.get("page_size", 5))
    except ValueError:
        abort(400, "page_number and page_size must be integers")

    if page_number < 1 or page_size < 1:
        abort(400, "page_number and page_size must be positive integers")

    # Calculate start and end indices
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size
    
    paginated_results = result[start_index:end_index]

    return jsonify({
        "page": page_number,
        "page_size": page_size,
        "total_results": len(result),
        "total_pages": (len(result) + page_size - 1) // page_size,
        "data": paginated_results
    })


@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e)), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify(error=str(e)), 404



if __name__ == "__main__":
    
    app.run(debug=True)
