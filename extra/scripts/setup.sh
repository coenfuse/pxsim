python3 -m venv venv
source venv/bin/activate
pip install wheel
python3 setup.py bdist_wheel
pip install -r requirements.txt