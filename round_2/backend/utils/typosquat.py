# PURPOSE: Typosquatting detection using Levenshtein distance
from difflib import SequenceMatcher
from typing import List, Tuple

# List of 100+ popular npm packages commonly targeted by typosquatters
POPULAR_PACKAGES = [
    # Top downloads
    "lodash", "react", "react-dom", "express", "axios", "typescript",
    "webpack", "next", "vue", "angular", "moment", "jquery",
    "chalk", "commander", "debug", "request", "async", "bluebird",

    # Common frameworks
    "svelte", "nuxt", "gatsby", "redux", "mobx", "rxjs",
    "passport", "socket.io", "ws", "cors", "helmet", "morgan",

    # Testing & build tools
    "jest", "mocha", "chai", "jasmine", "karma", "ava",
    "eslint", "prettier", "babel", "rollup", "parcel", "vite",
    "esbuild", "gulp", "grunt", "webpack-cli", "nodemon",

    # Type definitions
    "@types/node", "@types/react", "@types/express", "@types/jest",

    # Angular ecosystem
    "@angular/core", "@angular/common", "@angular/router",
    "@angular/forms", "@angular/http", "@angular/platform-browser",

    # Babel ecosystem
    "@babel/core", "@babel/preset-env", "@babel/preset-react",
    "@babel/preset-typescript", "@babel/plugin-transform-runtime",

    # React ecosystem
    "react-router", "react-router-dom", "prop-types", "classnames",
    "react-scripts", "create-react-app", "styled-components",

    # Node.js core utilities
    "dotenv", "fs-extra", "path", "util", "url", "querystring",
    "body-parser", "cookie-parser", "multer", "busboy",

    # Database & ORM
    "mongoose", "sequelize", "typeorm", "prisma", "knex",
    "pg", "mysql", "redis", "mongodb", "sqlite3",

    # Authentication & security
    "jsonwebtoken", "bcrypt", "bcryptjs", "passport-local",
    "passport-jwt", "express-session", "connect-redis",

    # HTTP clients & servers
    "node-fetch", "got", "superagent", "http-proxy",
    "http-server", "serve", "express-static",

    # Date & time
    "dayjs", "date-fns", "luxon", "moment-timezone",

    # Validation
    "joi", "yup", "ajv", "validator", "class-validator",

    # Historical attack targets
    "event-stream", "ua-parser-js", "colors", "faker", "node-ipc",
    "is-promise", "flatmap-stream", "getcookies", "crossenv",
]

# Normalize popular packages list (lowercase, no duplicates)
POPULAR_PACKAGES = list(set([pkg.lower() for pkg in POPULAR_PACKAGES]))


def normalize_package_name(package_name: str) -> str:
    """
    Normalize package name for comparison.

    - Convert to lowercase
    - Remove scope prefix (@scope/)
    - Replace underscores with hyphens
    """
    normalized = package_name.lower().strip()

    # Remove scope for scoped packages
    if normalized.startswith("@"):
        parts = normalized.split("/", 1)
        if len(parts) == 2:
            normalized = parts[1]

    # Normalize separators
    normalized = normalized.replace("_", "-")

    return normalized


def check_typosquatting(
    package_name: str,
    threshold: float = 0.80
) -> List[Tuple[str, float]]:
    """
    Check if package name is similar to popular packages.

    Args:
        package_name: Package name to check
        threshold: Similarity threshold (0.0-1.0), default 0.80

    Returns:
        List of (package_name, similarity_score) tuples for matches
        Sorted by similarity score (highest first)
    """
    normalized = normalize_package_name(package_name)

    # Exact match is not typosquatting
    if normalized in POPULAR_PACKAGES:
        return []

    matches = []

    for popular_pkg in POPULAR_PACKAGES:
        # Calculate similarity using SequenceMatcher (Levenshtein-like)
        ratio = SequenceMatcher(None, normalized, popular_pkg).ratio()

        if ratio >= threshold:
            matches.append((popular_pkg, ratio))

    # Sort by similarity (highest first)
    matches.sort(key=lambda x: x[1], reverse=True)

    return matches
