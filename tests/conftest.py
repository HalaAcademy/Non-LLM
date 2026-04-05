"""Conftest cho toàn bộ test suite."""
import sys
import os

# Thêm src/ vào path để import copl
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
