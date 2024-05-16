"""Module  Contains code for making request to fahamu Api"""
# pylint: disable=C0301
import json
import time

import requests
from requests import Session
from requests.adapters import HTTPAdapter

from urllib3.util import Retry
from gn3.llms.errors import LLMError


class TimeoutHTTPAdapter(HTTPAdapter):
    """HTTP TimeoutAdapter """
    # todo rework on this
    def __init__(self, timeout, *args, **kwargs):
        """TimeoutHTTPAdapter constructor.
        Args:
            timeout (int): How many seconds to wait for the server to
        send data before
                giving up.
        """
        self.timeout = timeout
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        """Override :obj:`HTTPAdapter` send method to add a default timeout."""
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout

        return super().send(request, **kwargs)


class GeneNetworkQAClient(Session):
    """GeneNetworkQA Client

    This class provides a client object interface to the GeneNetworkQA API.
    It extends the `requests.Session` class and includes authorization,
    base URL,
    request timeouts, and request retries.

    Args:
        account (str): Base address subdomain.
        api_key (str): API key.
        version (str, optional): API version, defaults to "v3".
        timeout (int, optional): Timeout value, defaults to 5.
        total_retries (int, optional): Total retries value, defaults to 5.
        backoff_factor (int, optional): Retry backoff factor value,
    defaults to 30.

    Usage:
        from genenetworkqa import GeneNetworkQAClient
        gnqa = GeneNetworkQAClient(account="account-name",
    api_key="XXXXXXXXXXXXXXXXXXX...")
    """

    def __init__(self, account, api_key, version="v3", timeout=30,
                 total_retries=5, backoff_factor=30):
        super().__init__()
        self.headers.update(
            {"Authorization": "Bearer " + api_key})
        self.base_url = "https://genenetwork.fahamuai.com/api/tasks"
        self.answer_url = f"{self.base_url}/answers"
        self.feedback_url = f"{self.base_url}/feedback"

        adapter = TimeoutHTTPAdapter(
            timeout=timeout,
            max_retries=Retry(
                total=total_retries,
                status_forcelist=[429, 500, 502, 503, 504],
                backoff_factor=backoff_factor,
            ),
        )

        self.mount("https://", adapter)
        self.mount("http://", adapter)

    def ask_the_documents(self, extend_url, my_auth):
        try:
            response = requests.post(
                self.base_url + extend_url, data={}, headers=my_auth)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            raise RuntimeError(f"Error making the request: {error}") from error
        if response.status_code != 200:
            return GeneNetworkQAClient.negative_status_msg(response), 0
        task_id = GeneNetworkQAClient.get_task_id_from_result(response)
        response = GeneNetworkQAClient.get_answer_using_task_id(task_id,
                                                                my_auth)
        if response.status_code != 200:
            return GeneNetworkQAClient.negative_status_msg(response), 0
        return response, 1

    @staticmethod
    def negative_status_msg(response):
        """ handler for non 200 response from fahamu api"""
        return f"Error: Status code -{response.status_code}- Reason::{response.reason}"

    def ask(self, ex_url, *args, **kwargs):
        """fahamu ask api interface"""
        res = self.custom_request('POST', f"{self.base_url}{ex_url}", *args, **kwargs)
        if res.status_code != 200:
            return self.negative_status_msg(res), 0
        return res, json.loads(res.text)

    def get_answer(self, taskid, *args, **kwargs):
        """Fahamu get answer interface"""
        query = f"{self.answer_url}?task_id={taskid['task_id']}"
        res = self.custom_request('GET', query, *args, **kwargs)
        if res.status_code != 200:
            return self.negative_status_msg(res), 0
        return res, 1

    @staticmethod
    def get_task_id_from_result(response):
        """method to get task_id from response"""
        task_id = json.loads(response.text)
        return f"?task_id={task_id.get('task_id', '')}"

    def get_answer_using_task_id(self, extend_url, my_auth):
        """call this method with task id to fetch response"""
        try:
            response = requests.get(
               self.answer_url + extend_url, data={}, headers=my_auth)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as error:
            raise error

    def custom_request(self, method, url, *args, **kwargs):
        """ make custom request to fahamu api ask and get response"""
        max_retries = 50
        retry_delay = 3
        for _i in range(max_retries):
            try:
                response = super().request(method, url, *args, **kwargs)
                response.raise_for_status()
            except requests.exceptions.HTTPError as error:
                if error.response.status_code == 500:
                    raise LLMError(error.request, error.response, f"Response Error with:status_code:{error.response.status_code},Reason for error: Use of Invalid Fahamu Token") from error
                elif error.response.status_code == 404:
                    raise LLMError(error.request, error.response, f"404 Client Error: Not Found for url: {self.base_url}") from error
                raise error
            except requests.exceptions.RequestException as error:
                raise error
            if response.ok:
                if method.lower() == "get" and response.json().get("data") is None:
                    time.sleep(retry_delay)
                    continue
                else:
                    return response
            else:
                time.sleep(retry_delay)
            return response
