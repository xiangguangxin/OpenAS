def paginate(items, page, page_size):
    """Deliberately broken fixture for the isolated repair walkthrough."""
    start = page * page_size
    return items[start:start + page_size]
