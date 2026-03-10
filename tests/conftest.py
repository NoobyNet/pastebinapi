"""Pytest configuration and fixtures."""

import os
import pytest

# Set mock environment variables before any imports
os.environ["PASTEBIN_BASE_URL"] = "https://pastebin.com/api"
os.environ["DEV_API_KEY"] = "test_dev_key"
os.environ["USER_NAME"] = "test_user"
os.environ["USER_PASSWORD"] = "test_pass"
