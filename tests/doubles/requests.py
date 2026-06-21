# في tests/doubles/requests.py

class MockResponse:
    """محاكاة Response object"""
    def __init__(self, json_data=None, status_code=200):
        self._json_data = json_data or {}
        self.status_code = status_code
    
    def json(self):
        return self._json_data


class RequestSenderDouble:
    """محاكاة request sender"""
    def __init__(self, json=None, status_code=200):
        self.last_call = None
        self.response = MockResponse(json, status_code)
    
    def request(self, method, url, **kwargs):
        self.last_call = {
            'method': method,
            'url': url,
            'kwargs': kwargs
        }
        return self.response
    
    def assert_that_request_is_called_with(self, method, url, **kwargs):
        from assertpy import assert_that
        
        assert_that(self.last_call).is_not_none()
        assert_that(self.last_call['method']).is_equal_to(method) # type: ignore
        assert_that(self.last_call['url']).is_equal_to(url) # type: ignore
        
        for key, value in kwargs.items():
            assert_that(self.last_call['kwargs'].get(key))\ 
             .is_equal_to(value)


class CustomAuthDouble:
    """✅ محاكاة Auth Double"""
    def __init__(self, token):
        self.token = token
        self.called = False
    
    @property
    def headers(self):
        """أرجع الـ headers"""
        self.called = True
        return {
            "Authorization": f"Bearer {self.token}"
        }
    
    def assert_that_headers_were_called(self):
        """تحقق: اتنادت headers"""
        from assertpy import assert_that
        assert_that(self.called).is_true()