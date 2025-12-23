from LogParser import LogParser
file_path='./logs/sample.log'
parser = LogParser()


from flask import Flask, jsonify, request, abort
from datetime import datetime
import os

app = Flask(__name__)

LOG_DIR = "logs"
logs = []


def load_logs():
    """
    Reads all log files from LOG_DIR and parses them into memory.
    """
    global logs
    log_id = 1

    for file_name in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, file_name)

        if not os.path.isfile(file_path):
            continue

        with open(file_path, "r") as file:
            for line in file:
                try:
                    parsed = parser.parse_line(line)
                    logs.append({
                        "id": log_id,
                        "timestamp": parsed["timestamp"],
                        "level": parsed["level"],
                        "component": parsed["component"],
                        "message": parsed["message"]
                    })
                    log_id += 1
                except ValueError as e:
                    # Skip invalid log entries (or log this somewhere)
                    print(f"Skipping invalid log line: {e}")
                log_id += 1


def parse_time(time_str):
    return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")


@app.route("/logs", methods=["GET"])
def get_logs():
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


@app.route("/logs/<int:log_id>", methods=["GET"])
def get_log_by_id(log_id):
    for log in logs:
        if log["id"] == log_id:
            return jsonify(log)

    abort(404, "Log ID not found")


@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e)), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify(error=str(e)), 404


if __name__ == "__main__":
    load_logs()
    app.run(debug=True)
