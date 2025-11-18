class Colors:
    """ANSI color codes"""

    ROBOT = "\033[94m"  # Blue
    CB = "\033[92m"  # Green
    MAIN = "\033[90m"  # Gray
    ERROR = "\033[91m"  # Red
    WARNING = "\033[93m"  # Orange
    RESET = "\033[0m"  # Reset
    BOLD = "\033[1m"


def robot_log(message):
    """Log message from robot controller"""
    print(f"{Colors.ROBOT}{message}{Colors.RESET}")


def cb_log(message):
    """Log message from CB controller"""
    print(f"{Colors.CB}{message}{Colors.RESET}")


def main_log(message):
    """Log message from main orchestrator"""
    print(f"{Colors.MAIN}{message}{Colors.RESET}")


def error_log(message):
    """Log error message (any component)"""
    print(f"{Colors.ERROR}{Colors.BOLD}{message}{Colors.RESET}")


def warning_log(message):
    """Log warning message (any component)"""
    print(f"{Colors.WARNING}{message}{Colors.RESET}")
