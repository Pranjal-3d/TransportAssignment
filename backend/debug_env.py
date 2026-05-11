import os
from dotenv import load_dotenv
load_dotenv()
for k, v in os.environ.items():
    print(f"{k}={v}")
