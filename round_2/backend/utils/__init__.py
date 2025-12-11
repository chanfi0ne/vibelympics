# PURPOSE: Package initialization for utility modules
from .typosquat import check_typosquatting, POPULAR_PACKAGES
from .patterns import DANGEROUS_COMMANDS, DANGEROUS_SCRIPTS, check_dangerous_patterns

__all__ = [
    "check_typosquatting",
    "POPULAR_PACKAGES",
    "DANGEROUS_COMMANDS",
    "DANGEROUS_SCRIPTS",
    "check_dangerous_patterns",
]
