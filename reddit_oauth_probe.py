#!/usr/bin/env python3
"""Minimal read-only Reddit OAuth probe using only the Python standard library."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
API_BASE_URL = "https://oauth.reddit.com"
DEFAULT_LIMIT = 5
MAX_LIMIT = 25


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def request_access_token(client_id: str, client_secret: str, user_agent: str) -> str:
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    request = urllib.request.Request(
        TOKEN_URL,
        data=urllib.parse.urlencode({"grant_type": "client_credentials"}).encode(),
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": user_agent,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        payload = json.load(response)

    token = payload.get("access_token")
    if not token:
        raise RuntimeError("Reddit did not return an access_token")
    return str(token)


def search_public_posts(
    token: str,
    user_agent: str,
    subreddit: str,
    query: str,
    limit: int,
) -> list[dict[str, object]]:
    params = urllib.parse.urlencode(
        {
            "q": query,
            "restrict_sr": "1",
            "sort": "relevance",
            "limit": str(limit),
        }
    )
    url = f"{API_BASE_URL}/r/{subreddit}/search?{params}"
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": user_agent,
        },
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        payload = json.load(response)

    posts = []
    for child in payload.get("data", {}).get("children", []):
        item = child.get("data", {})
        posts.append(
            {
                "title": item.get("title"),
                "score": item.get("score", 0),
                "num_comments": item.get("num_comments", 0),
                "permalink": f"https://www.reddit.com{item.get('permalink', '')}",
            }
        )
    return posts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Get an application-only OAuth token and search public Reddit posts."
    )
    parser.add_argument("subreddit", help="Subreddit name without the r/ prefix")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    args = parser.parse_args()
    if not 1 <= args.limit <= MAX_LIMIT:
        parser.error(f"--limit must be between 1 and {MAX_LIMIT}")
    return args


def main() -> int:
    args = parse_args()
    try:
        client_id = required_env("REDDIT_CLIENT_ID")
        client_secret = required_env("REDDIT_CLIENT_SECRET")
        user_agent = required_env("REDDIT_USER_AGENT")
        token = request_access_token(client_id, client_secret, user_agent)
        posts = search_public_posts(
            token,
            user_agent,
            args.subreddit,
            args.query,
            args.limit,
        )
    except (RuntimeError, urllib.error.URLError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(posts, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
