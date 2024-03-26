def colorize(text, color, bold=False):
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m",
    }

    bold_code = "\033[1m" if bold else ""
    color_code = colors.get(color.lower(), "")

    return f"{bold_code}{color_code}{text}{colors['reset']}"


# # Example usage
# print(colorize("Hello, World!", "red", bold=True))
# print(colorize("This is a green text.", "green"))
# print(colorize("This is a bold blue text.", "blue", bold=True))
