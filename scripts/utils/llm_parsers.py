"""
Parsers for LLM conversation exports from ChatGPT, Claude, and Grok.
"""

import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime


class ConversationMessage:
    """Represents a single message in a conversation."""

    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None):
        self.role = role  # 'user' or 'assistant'
        self.content = content
        self.timestamp = timestamp

    def __repr__(self):
        return f"ConversationMessage(role={self.role}, content_length={len(self.content)})"


class Conversation:
    """Represents a parsed conversation."""

    def __init__(self, title: str = None, messages: List[ConversationMessage] = None,
                 metadata: Dict[str, Any] = None):
        self.title = title or "Untitled Conversation"
        self.messages = messages or []
        self.metadata = metadata or {}

    def get_user_messages(self) -> List[ConversationMessage]:
        """Get all user messages."""
        return [msg for msg in self.messages if msg.role == 'user']

    def get_assistant_messages(self) -> List[ConversationMessage]:
        """Get all assistant messages."""
        return [msg for msg in self.messages if msg.role == 'assistant']

    def to_markdown(self) -> str:
        """Convert conversation to Markdown format."""
        lines = []

        for msg in self.messages:
            if msg.role == 'user':
                lines.append(f"**User:** {msg.content}\n")
            else:
                lines.append(f"**Assistant:** {msg.content}\n")

        return "\n".join(lines)

    def __repr__(self):
        return f"Conversation(title={self.title}, messages={len(self.messages)})"


def parse_chatgpt(data: Any) -> Conversation:
    """
    Parse a ChatGPT conversation export.

    ChatGPT exports conversations as JSON with the following structure:
    {
        "title": "Conversation Title",
        "mapping": {
            "id": {
                "message": {
                    "author": {"role": "user" or "assistant"},
                    "content": {"parts": ["message text"]},
                    "create_time": timestamp
                }
            }
        }
    }

    Args:
        data: JSON data (dict) or string containing JSON

    Returns:
        Parsed Conversation object
    """
    if isinstance(data, str):
        data = json.loads(data)

    title = data.get('title', 'Untitled Conversation')
    messages = []

    # ChatGPT uses a mapping structure
    mapping = data.get('mapping', {})

    # Build a list of messages in order
    for node_id, node_data in mapping.items():
        if 'message' not in node_data or node_data['message'] is None:
            continue

        message_data = node_data['message']
        author = message_data.get('author', {})
        role = author.get('role', 'unknown')

        # Skip system messages
        if role == 'system':
            continue

        content_data = message_data.get('content', {})
        parts = content_data.get('parts', [])

        if not parts:
            continue

        # Join all parts (usually just one)
        content = '\n'.join(str(part) for part in parts if part)

        # Parse timestamp
        timestamp = None
        create_time = message_data.get('create_time')
        if create_time:
            timestamp = datetime.fromtimestamp(create_time)

        messages.append(ConversationMessage(role, content, timestamp))

    return Conversation(title=title, messages=messages)


def parse_claude(data: Any) -> Conversation:
    """
    Parse a Claude conversation export.

    Claude exports may vary in format. This handles common formats:
    - JSON with messages array
    - Plain text with role markers

    Args:
        data: JSON data (dict), string containing JSON, or plain text

    Returns:
        Parsed Conversation object
    """
    # Try parsing as JSON first
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            # Not JSON, treat as plain text
            return parse_plain_text_conversation(data)

    # Handle JSON format
    if isinstance(data, dict):
        title = data.get('title') or data.get('name', 'Untitled Conversation')
        messages = []

        # Check for messages array
        messages_data = data.get('messages', [])

        for msg_data in messages_data:
            role = msg_data.get('role') or msg_data.get('sender', 'unknown')
            content = msg_data.get('content') or msg_data.get('text', '')

            # Handle role mapping
            if role in ['human', 'user']:
                role = 'user'
            elif role in ['assistant', 'claude']:
                role = 'assistant'

            # Parse timestamp if available
            timestamp = None
            timestamp_str = msg_data.get('timestamp') or msg_data.get('created_at')
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except:
                    pass

            messages.append(ConversationMessage(role, content, timestamp))

        return Conversation(title=title, messages=messages)

    return Conversation()


def parse_grok(data: Any) -> Conversation:
    """
    Parse a Grok conversation export.

    Grok format is similar to other LLM exports but may have X/Twitter-specific structure.

    Args:
        data: JSON data (dict) or string containing JSON

    Returns:
        Parsed Conversation object
    """
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return parse_plain_text_conversation(data)

    title = data.get('title', 'Untitled Conversation')
    messages = []

    # Try to find messages in various possible locations
    messages_data = (
        data.get('messages') or
        data.get('conversation') or
        data.get('exchanges') or
        []
    )

    for msg_data in messages_data:
        role = msg_data.get('role') or msg_data.get('author', 'unknown')
        content = msg_data.get('content') or msg_data.get('text', '')

        # Normalize role
        if role.lower() in ['user', 'human']:
            role = 'user'
        elif role.lower() in ['assistant', 'grok', 'ai']:
            role = 'assistant'

        timestamp = None
        timestamp_str = msg_data.get('timestamp') or msg_data.get('created_at')
        if timestamp_str:
            try:
                if isinstance(timestamp_str, (int, float)):
                    timestamp = datetime.fromtimestamp(timestamp_str)
                else:
                    timestamp = datetime.fromisoformat(str(timestamp_str).replace('Z', '+00:00'))
            except:
                pass

        messages.append(ConversationMessage(role, content, timestamp))

    return Conversation(title=title, messages=messages)


def parse_plain_text_conversation(text: str) -> Conversation:
    """
    Parse a plain text conversation with role markers.

    Supports formats like:
    - "User: message"
    - "Assistant: message"
    - "Human: message"
    - "AI: message"

    Args:
        text: Plain text conversation

    Returns:
        Parsed Conversation object
    """
    lines = text.split('\n')
    messages = []
    current_role = None
    current_content = []

    role_patterns = {
        r'^(User|Human|You):\s*(.*)$': 'user',
        r'^(Assistant|AI|Claude|ChatGPT|Grok):\s*(.*)$': 'assistant',
    }

    def add_message():
        if current_role and current_content:
            content = '\n'.join(current_content).strip()
            if content:
                messages.append(ConversationMessage(current_role, content))

    for line in lines:
        matched = False

        for pattern, role in role_patterns.items():
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                # Save previous message
                add_message()

                # Start new message
                current_role = role
                current_content = [match.group(2)] if match.group(2) else []
                matched = True
                break

        if not matched and current_role:
            # Continue current message
            current_content.append(line)

    # Add last message
    add_message()

    return Conversation(title="Plain Text Conversation", messages=messages)


def auto_detect_and_parse(data: Any) -> Conversation:
    """
    Automatically detect the format and parse the conversation.

    Args:
        data: Conversation data (JSON dict, JSON string, or plain text)

    Returns:
        Parsed Conversation object
    """
    # If it's a string, try to parse as JSON
    if isinstance(data, str):
        try:
            json_data = json.loads(data)
            return auto_detect_and_parse(json_data)
        except json.JSONDecodeError:
            # Not JSON, treat as plain text
            return parse_plain_text_conversation(data)

    # If it's a dict, try to detect the source
    if isinstance(data, dict):
        # ChatGPT has 'mapping' key
        if 'mapping' in data:
            return parse_chatgpt(data)

        # Check for common Claude/Grok patterns
        if 'messages' in data or 'conversation' in data:
            # Try Claude first
            conv = parse_claude(data)
            if conv.messages:
                return conv

            # Try Grok
            conv = parse_grok(data)
            if conv.messages:
                return conv

    # Fallback to empty conversation
    return Conversation()
