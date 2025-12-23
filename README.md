# Assumeptions
* ```\t``` is a literal tab separating fields, log files are UTF-8 encoded, each line represents a single log entry, timestamps are in local time unless specified, and missing or extra fields indicate a malformed line.
* Missing or extra fields indicate a malformed line.
* No restrictions on component type; it can contain any characters.
 ***
 # Tech stack
  * Python- Flask, pytest, uuid
  * Postman for testing api's. Collection link- [Postman public link]( https://www.postman.com/alpines-3277/workspace/log-api/collection/18666523-78594802-1d7b-4e77-9014-f62bdf6f48ce?action=share&creator=18666523&active-environment=18666523-7eb63a6d-29d6-4579-9d39-6026715e795a)
 ***
# Endpoints-
* ```/logs```- Returns all parsed log entries in JSON format. Supports optional filtering by log level, component, and timestamp range.
     * Query Parameters (optional):
    * level – Filter logs by level (e.g., ?level=ERROR)
     * component – Filter logs by component (e.g., ?component=UserAuth)
     * start_time – Filter logs after this timestamp (YYYY-MM-DD HH:MM:SS)
     * end_time – Filter logs before this timestamp (YYYY-MM-DD HH:MM:SS)
* ```/logs/stats```- Returns statistics about the log data, including:
    * Total number of log entries.
    * Counts of log entries per level.
    * Counts of log entries per component.
* ```/logs/<string:log_id>```-  Returns a specific log entry based on a unique log_id. 
 ***
# Setup and run

 *  Environment Setup
   ```bash 
   python -m venv venv
   venv\Scripts\activate     
```
*   Install packages
   ```bash 
   pip install -r requirements.txt
   ```
 *   Run server and test file
   ```bash 
   python app.py        #to run server
   pytest -v           #to run test cases
   ```


    
