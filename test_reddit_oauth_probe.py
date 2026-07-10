from __future__ import annotations

import io
import json
import unittest
from unittest.mock import patch

from reddit_oauth_probe import request_access_token, search_public_posts


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()
        return False


class RedditOAuthProbeTests(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_requests_client_credentials_token(self, urlopen):
        urlopen.return_value = FakeResponse(
            json.dumps({"access_token": "test-token"}).encode()
        )

        token = request_access_token("client-id", "client-secret", "test-agent")

        self.assertEqual(token, "test-token")
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://www.reddit.com/api/v1/access_token")
        self.assertEqual(request.data, b"grant_type=client_credentials")

    @patch("urllib.request.urlopen")
    def test_parses_public_search_results(self, urlopen):
        payload = {
            "data": {
                "children": [
                    {
                        "data": {
                            "title": "Example post",
                            "score": 12,
                            "num_comments": 3,
                            "permalink": "/r/pools/comments/example",
                        }
                    }
                ]
            }
        }
        urlopen.return_value = FakeResponse(json.dumps(payload).encode())

        posts = search_public_posts(
            "test-token", "test-agent", "pools", "pool robot", 5
        )

        self.assertEqual(
            posts,
            [
                {
                    "title": "Example post",
                    "score": 12,
                    "num_comments": 3,
                    "permalink": "https://www.reddit.com/r/pools/comments/example",
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
