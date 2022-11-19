
def is_version_greater(required_version: (int, int), client_version: str):
    try:
        major, minor = (int(v) for v in client_version.split("."))
    except (ValueError, TypeError):
        return None
    
    return required_version[0] <= major and (required_version[0] < major or required_version[1] <= minor)
