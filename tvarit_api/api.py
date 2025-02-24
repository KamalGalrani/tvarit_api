import pyotp
import requests
import requests.auth


class TvaritException(Exception):
    pass


class TvaritServerError(Exception):
    """
    5xx
    """

    pass


class TvaritClientError(Exception):
    """
    Invalid input (4xx errors)
    """

    pass


class TvaritBadInputError(TvaritClientError):
    """
    400
    """

    pass


class TvaritUnauthorizedError(TvaritClientError):
    """
    401
    """

    pass


class TokenAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, request):
        request.headers.update({"Authorization": "Bearer {0}".format(self.token)})
        return request


class TOTPAuth(requests.auth.AuthBase):
    def __init__(self, org_id, token):
        self.org_id = str(org_id)
        self.totp = pyotp.TOTP(token).now

    def __call__(self, request):
        request.headers.update({"Authorization": "TOTP {0}".format(self.totp())})
        request.headers.update({"X-Grafana-Org-Id": self.org_id})
        return request


class TvaritAPI:
    def __init__(
        self,
        auth,
        host="localhost",
        port=None,
        url_path_prefix="",
        protocol="http",
        verify=True,
    ):
        self.auth = auth
        self.verify = verify
        self.url_host = host
        self.url_port = port
        self.url_path_prefix = url_path_prefix
        self.url_protocol = protocol

        def construct_api_url():
            params = {
                "protocol": self.url_protocol,
                "host": self.url_host,
                "url_path_prefix": self.url_path_prefix,
            }

            if self.url_port is None:
                url_pattern = "{protocol}://{host}/{url_path_prefix}api"
            else:
                params["port"] = self.url_port
                url_pattern = "{protocol}://{host}:{port}/{url_path_prefix}api"

            return url_pattern.format(**params)

        self.url = construct_api_url()

        self.s = requests.Session()
        if not isinstance(self.auth, tuple):
            self.auth = TokenAuth(self.auth)
        else:
            if type(self.auth[0]) == int:
                self.auth = TOTPAuth(*self.auth)
            else:
                self.auth = requests.auth.HTTPBasicAuth(*self.auth)

    def __getattr__(self, item):
        def __request_runnner(url, json=None, headers=None, params=None):
            __url = "%s%s" % (self.url, url)
            runner = getattr(self.s, item.lower())
            r = runner(
                __url, json=json, headers=headers, params=params, auth=self.auth, verify=self.verify
            )

            if 500 <= r.status_code < 600:
                raise TvaritServerError(
                    "Server Error {0}: {1}".format(
                        r.status_code, r.content.decode("ascii", "replace")
                    )
                )
            elif r.status_code == 400:
                raise TvaritBadInputError("Bad Input: `{0}`".format(r.text))
            elif r.status_code == 401:
                raise TvaritUnauthorizedError("Unauthorized")
            elif 400 <= r.status_code < 500:
                raise TvaritClientError(
                    "Client Error {0}: {1}".format(r.status_code, r.text)
                )
            return r.json()

        return __request_runnner
