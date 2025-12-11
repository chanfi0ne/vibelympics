# PURPOSE: Dangerous command pattern detection for install scripts
from typing import List, Tuple

# Dangerous commands that should raise security concerns
DANGEROUS_COMMANDS = [
    # Network operations
    "curl", "wget", "nc ", "nc.traditional", "netcat", "telnet", "ftp",

    # Shell execution
    "bash -c", "/bin/sh", "/bin/bash", "sh -c", "/bin/dash",
    "eval(", "eval ", "exec(", "exec ",

    # Encoding/obfuscation
    "base64", "base32", "rot13", "atob", "btoa",
    "echo", "printf",  # Often used with base64

    # Windows shells
    "powershell", "cmd.exe", "cmd /c", "cmd.exe /c",

    # Destructive operations
    "rm -rf", "rm -fr", "del /f", "rmdir /s",
    "format ", "> /dev/", "| /dev/", "dd if=",

    # Persistence mechanisms
    "crontab", "systemctl", "launchctl", "at ", "schtasks",
    "service ", "chkconfig", "update-rc.d",

    # Data exfiltration
    "scp", "sftp", "rsync", "tar czf", "zip -r",

    # Process manipulation
    "kill ", "pkill", "killall", "nohup",

    # Permission changes
    "chmod +x", "chmod 777", "chown", "chgrp",

    # Network listeners
    "python -m http.server", "python -m SimpleHTTPServer",
    "php -S", "ruby -run", "nc -l",
]

# Install script lifecycle hooks that execute code
DANGEROUS_SCRIPTS = [
    "preinstall",
    "install",
    "postinstall",
    "preuninstall",
    "uninstall",
    "postuninstall",
]


def check_dangerous_patterns(script_content: str) -> List[Tuple[str, str]]:
    """
    Check script content for dangerous command patterns.

    Args:
        script_content: Shell script content to analyze

    Returns:
        List of (pattern, context) tuples for dangerous patterns found
        Pattern: The dangerous command pattern matched
        Context: Surrounding text showing where it was found
    """
    if not script_content:
        return []

    found_patterns = []
    script_lower = script_content.lower()

    for dangerous_cmd in DANGEROUS_COMMANDS:
        if dangerous_cmd.lower() in script_lower:
            # Find context around the dangerous command
            index = script_lower.find(dangerous_cmd.lower())

            # Extract context (50 chars before and after)
            start = max(0, index - 50)
            end = min(len(script_content), index + len(dangerous_cmd) + 50)
            context = script_content[start:end].strip()

            # Truncate context if too long
            if len(context) > 150:
                context = context[:147] + "..."

            found_patterns.append((dangerous_cmd, context))

    return found_patterns
