def print_result(value, message):
    if value:
        return "ok"
    else:
        return f"ERROR: {message}"


def make_row_style(version):
    return "dim" if version == "3.0.0" else None