import unittest
from unittest import mock

import fetch


class FakeResponse:
    def __init__(self, status_code=200, body=None, json_error=False):
        self.status_code = status_code
        self._body = body if body is not None else []
        self._json_error = json_error

    def json(self):
        if self._json_error:
            raise ValueError("not json")
        return self._body


def repo(name, stars=1):
    return {"name": name, "description": "d", "stargazers_count": stars}


class FetchTests(unittest.TestCase):
    def test_single_page_and_timeout_and_headers(self):
        with mock.patch.object(
            fetch.requests, "get", return_value=FakeResponse(body=[repo("a")])
        ) as get:
            result = fetch.fetch_starred_repositories("octocat", token="dummy")
        self.assertEqual([r["name"] for r in result], ["a"])
        _, kwargs = get.call_args
        self.assertEqual(kwargs["timeout"], fetch.REQUEST_TIMEOUT)
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer dummy")

    def test_pagination_until_short_page(self):
        page1 = [repo(str(i)) for i in range(100)]
        page2 = [repo("last")]
        with mock.patch.object(
            fetch.requests,
            "get",
            side_effect=[FakeResponse(body=page1), FakeResponse(body=page2)],
        ) as get:
            result = fetch.fetch_starred_repositories("octocat")
        self.assertEqual(len(result), 101)
        self.assertEqual(get.call_count, 2)

    def test_status_failure_raises(self):
        with mock.patch.object(
            fetch.requests, "get", return_value=FakeResponse(status_code=404)
        ):
            with self.assertRaises(fetch.FetchError):
                fetch.fetch_starred_repositories("octocat")

    def test_non_json_body_raises(self):
        with mock.patch.object(
            fetch.requests, "get", return_value=FakeResponse(json_error=True)
        ):
            with self.assertRaises(fetch.FetchError):
                fetch.fetch_starred_repositories("octocat")

    def test_non_list_body_raises(self):
        with mock.patch.object(
            fetch.requests,
            "get",
            return_value=FakeResponse(body={"message": "nope"}),
        ):
            with self.assertRaises(fetch.FetchError):
                fetch.fetch_starred_repositories("octocat")

    def test_network_error_raises(self):
        with mock.patch.object(
            fetch.requests,
            "get",
            side_effect=fetch.requests.RequestException("down"),
        ):
            with self.assertRaises(fetch.FetchError):
                fetch.fetch_starred_repositories("octocat")


class MainTests(unittest.TestCase):
    def test_invalid_username_exits_2_without_a_request(self):
        with mock.patch.object(fetch.requests, "get") as get:
            self.assertEqual(fetch.main(["bad/name"]), 2)
        get.assert_not_called()

    def test_failed_fetch_exits_1(self):
        with mock.patch.object(
            fetch.requests, "get", return_value=FakeResponse(status_code=500)
        ):
            self.assertEqual(fetch.main(["octocat"]), 1)

    def test_empty_list_exits_0(self):
        with mock.patch.object(
            fetch.requests, "get", return_value=FakeResponse(body=[])
        ):
            self.assertEqual(fetch.main(["octocat"]), 0)


if __name__ == "__main__":
    unittest.main()
