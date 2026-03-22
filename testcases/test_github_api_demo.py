from __future__ import annotations

import os

import pytest

from utils.assertions import Assert


@pytest.mark.smoke
def test_github_rate_limit(github_api):
    # 无 token 也能跑（但频率更低）
    r = github_api.get_rate_limit()
    Assert.status_code(r.response, 200)
    Assert.is_true(r.json)


@pytest.mark.smoke
def test_github_user_requires_token(github_api, github_token):
    if not github_token:
        pytest.skip("Set GITHUB_TOKEN to run authenticated endpoint test")

    r = github_api.get_authenticated_user()
    Assert.status_code(r.response, 200)
    Assert.equal(r.json.get("type"), "User")


def test_github_list_user_repos(github_api):
    # 公共端点：列出用户公开仓库
    username = os.getenv("GITHUB_USERNAME", "octocat").strip() or "octocat"
    r = github_api.list_user_repos(username, per_page=5)
    Assert.status_code(r.response, 200)
    Assert.is_true(isinstance(r.json, list))
