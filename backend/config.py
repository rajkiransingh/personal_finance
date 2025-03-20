import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL (Update with your actual MySQL credentials)
DATABASE_URL = os.getenv("DATABASE_URL")
