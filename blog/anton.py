import re

TAG_RE = re.compile(r'<[^>]+>')


def remove_tags(text):
    return TAG_RE.sub('', text)


def make_md5(text):
    import hashlib
    return hashlib.md5(text.encode('utf-8')).hexdigest()
