# 1. Create a virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 2. Install required packages
pip install -r requirements.txt

# 3. Run the application
python app.py

# 4. Run tests
pytest -v
