def color_swatch(color: Color, size: int = 2, with_name: bool = False) -> str:
    block = "█" * size
    span = (
        f'<span style="font-family: monospace; color: {color.code}">'
        f"{block}"
        "</span>"
    )
    if with_name:
        span += (
            f'<span style="color: {color.code}">'
            f"&nbsp;{color.name.title()}"
            "</span>"
        )
    return span
