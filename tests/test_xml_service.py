from pathlib import Path
from services.xml_service import parse_paste_list_xml

def read_paste_list() -> str:
    """Read a file and return its content."""
    file_path = Path(__file__).parent / "data" / "paste_list.txt"
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")

def test_read_paste_list():
    """Test reading a list of pastes from a file."""
    raw = read_paste_list()
    past_list = parse_paste_list_xml(raw)
    assert past_list is not None
    assert len(past_list) == 3
