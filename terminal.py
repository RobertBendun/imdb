import sys
import textwrap

if sys.stdout.isatty() and sys.stderr.isatty():
    COLOR_RESET  = "\x1b[0m"
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE  = (f"\x1b[{i}m" for i in range(30, 38))
    BRIGHT_BLACK, BRIGHT_RED, BRIGHT_GREEN, BRIGHT_YELLOW  = (f"\x1b[{i};1m" for i in range(30, 34))
    BRIGHT_BLUE, BRIGHT_MAGENTA, BRIGHT_CYAN, BRIGHT_WHITE = (f"\x1b[{i};1m" for i in range(34, 38))
    BOLD, UNDERLINE, REVERSED = "\x1b[1m", "\x1b[4m", "\x1b[7m"
    CLEAR_SCREEN = "\x1b[1;1H\x1b[2J"
else:
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = [""] * 8
    BRIGHT_BLACK, BRIGHT_RED, BRIGHT_GREEN, BRIGHT_YELLOW = [""] * 4
    BRIGHT_BLUE, BRIGHT_MAGENTA, BRIGHT_CYAN, BRIGHT_WHITE = [""] * 4
    BOLD, UNDERLINE, REVERSE, CLEAR_SCREEN, COLOR_RESET = [""] * 5

for prefix in ["", "bright_"]:
    for color in ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]:
        exec(textwrap.dedent(f"""
        def {prefix}{color}(s: str) -> str:
            return {prefix.upper()}{color.upper()} + s + COLOR_RESET
        """.strip(" \n")))

def bold(s: str):
    return BOLD + s + COLOR_RESET

def underline(s: str):
    return UNDERLINE + s + COLOR_RESET

def reverse(s: str):
    return REVERSE + s + COLOR_RESET
