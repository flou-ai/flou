from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod


class Widget(ABC):
    """Base widget class that all widgets must inherit from"""

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert widget to dictionary representation for frontend"""
        pass


class ChatWidget(Widget):
    """Widget to display a chat interface with messages"""

    def __init__(
        self,
        field: str,
        user_field: str = "user",
        content_field: str = "content",
        avatar_field: Optional[str] = None,
        timestamp_field: Optional[str] = "timestamp",
        title: Optional[str] = None,
    ):
        self.field = field
        self.user_field = user_field
        self.content_field = content_field
        self.avatar_field = avatar_field
        self.timestamp_field = timestamp_field
        self.title = title

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "chat",
            "field": self.field,
            "userField": self.user_field,
            "contentField": self.content_field,
            "avatarField": self.avatar_field,
            "timestampField": self.timestamp_field,
            "title": self.title,
        }


class TableWidget(Widget):
    """Widget to display tabular data"""

    def __init__(
        self,
        field: str,
        columns: List[Union[str, Dict[str, str]]],
        sortable: bool = True,
        filterable: bool = False,
        title: Optional[str] = None,
    ):
        self.field = field
        self.columns = columns
        self.sortable = sortable
        self.filterable = filterable
        self.title = title

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "table",
            "field": self.field,
            "columns": self.columns,
            "sortable": self.sortable,
            "filterable": self.filterable,
            "title": self.title,
        }


class ButtonsWidget(Widget):
    """Widget to display action buttons"""

    def __init__(
        self,
        buttons: List[Dict[str, str]],
        layout: str = "horizontal",  # horizontal, vertical, grid
        title: Optional[str] = None,
    ):
        self.buttons = buttons
        self.layout = layout
        self.title = title

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "buttons",
            "buttons": self.buttons,
            "layout": self.layout,
            "title": self.title,
        }


class SubLTMWidget(Widget):
    """Widget to display nested LTM state"""

    def __init__(
        self,
        pattern: str,  # e.g., "user_{id}"
        display: str = "inline",  # inline, link, modal
        max_items: Optional[int] = None,
        title: Optional[str] = None,
    ):
        self.pattern = pattern
        self.display = display
        self.max_items = max_items
        self.title = title

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "subLTM",
            "pattern": self.pattern,
            "display": self.display,
            "maxItems": self.max_items,
            "title": self.title,
        }


class KeyValueWidget(Widget):
    """Widget to display key-value pairs"""

    def __init__(
        self,
        field: Optional[str] = None,
        keys: Optional[List[str]] = None,
        exclude_keys: List[str] = None,
        title: Optional[str] = None,
    ):
        self.field = field
        self.keys = keys
        self.exclude_keys = exclude_keys or []
        self.title = title

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "keyValue",
            "field": self.field,
            "keys": self.keys,
            "excludeKeys": self.exclude_keys,
            "title": self.title,
        }


class ListWidget(Widget):
    """Widget to display a list of items"""

    def __init__(
        self,
        field: str,
        item_key: Optional[str] = None,
        item_template: Optional[str] = None,
        title: Optional[str] = None,
    ):
        self.field = field
        self.item_key = item_key
        self.item_template = item_template
        self.title = title

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "list",
            "field": self.field,
            "itemKey": self.item_key,
            "itemTemplate": self.item_template,
            "title": self.title,
        }