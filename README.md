# Reddit OAuth Probe

A minimal, read-only Python prototype for validating Reddit's application-only OAuth flow and public subreddit search API.

The probe:

- requests an OAuth token with the `client_credentials` grant;
- sends authenticated requests to `https://oauth.reddit.com`;
- searches one explicitly supplied public subreddit;
- prints a small JSON result containing titles, scores, comment counts, and Reddit permalinks;
- never prints or stores the OAuth token.

It does not post, comment, vote, send messages, perform moderation actions, access private data, build user profiles, or train machine-learning models.

## Requirements

- Python 3.10 or later
- A Reddit OAuth client approved for this use

No third-party Python packages are required.

## Test

The test suite is fully offline and uses fake OAuth/API responses.

```bash
python3 -m unittest -v
```

## Configuration

Set credentials only in your local shell or secret manager. Never commit them.

```bash
export REDDIT_CLIENT_ID='your-client-id'
export REDDIT_CLIENT_SECRET='your-client-secret'
export REDDIT_USER_AGENT='python:reddit-oauth-probe:v0.1 (by /u/YOUR_REDDIT_USERNAME)'
```

## Usage

Use only subreddits and API actions included in your approved scope.

```bash
python3 reddit_oauth_probe.py pools 'pool cleaning robot' --limit 5
```

The initial evaluation scope is limited to `r/pools`, `r/swimmingpools`, and `r/hottub`. Runs are manual and low volume.

## Data handling

The probe reads public post metadata for immediate technical validation. It does not redistribute bulk Reddit data. Delete any locally saved output when it is no longer required for the approved evaluation.
