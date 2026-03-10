import xmltodict
from typing import Any
from models.paste.paste_item import PasteItem

def parse_paste_list_xml(content: str) -> list[PasteItem]:
    """Parse XML content and return a list of pastes."""
    xml_doc = f"<pastes>{content}</pastes>"
    items_list = xmltodict.parse(xml_doc)["pastes"]["paste"]
    paste_list = map(lambda x: __parse_paste_item(x), items_list)

    return list(paste_list)

def __parse_paste_item(paste_dict: dict[str, Any]) -> PasteItem:
    paste_item = PasteItem(
        key=paste_dict['paste_key'],
        title=paste_dict['paste_title'],
        date=paste_dict['paste_date'],
        size=paste_dict['paste_size'],
        expire_date=paste_dict['paste_expire_date'],
        private=paste_dict['paste_private'],
        format_long=paste_dict['paste_format_long'],
        format_short=paste_dict['paste_format_short'],
        url=paste_dict['paste_url'],
        hits=paste_dict['paste_hits'],
    )
    return paste_item


