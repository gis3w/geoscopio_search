"""
Utils founctions for plugin
"""

import re

TAG_RE = re.compile(r'<[^>]+>')


def remove_tags(text):
    """
    Remove html tags from string
    """
    return TAG_RE.sub('', text)
