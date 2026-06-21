import unittest
from unittest.mock import Mock, patch
import http

from assertpy import assert_that

import api.services.request_service as request_service
import api.core.exceptions as exceptions


class TestGetService(unittest.TestCase):
    """اختبار Factory function"""
    
    def test_lcl_returns_requests_wrapper(self):
        """✅ env='lcl' → RequestsWrapper"""
        service = request_service.get_service('lcl')
        assert_that(service).is_instance_of(request_service.RequestsWrapper)
    
    def test_non_lcl_returns_wiremock(self):
        """✅ env != 'lcl' → WiremockRequester"""
        service = request_service.get_service('test')
        assert_that(service).is_instance_of(request_service.WiremockRequester)
        
        service = request_service.get_service('prod')
        assert_that(service).is_instance_of(request_service.WiremockRequester)


class TestRequestsWrapper(unittest.TestCase):
    """اختبار RequestsWrapper"""
    
    def setUp(self):
        self.mock_requests = Mock()
    
    def test_successful_get_request(self):
        """✅ GET request success"""
        mock_response = Mock()
        mock_response.status_code = http.HTTPStatus.OK
        self.mock_requests.request = Mock(return_value=mock_response)
        
        wrapper = request_service.RequestsWrapper(self.mock_requests)
        result = wrapper.request('GET', 'https://api.example.com/users')
        
        assert_that(result.status_code).is_equal_to(200)
    
    def test_successful_post_request(self):
        """✅ POST request success"""
        mock_response = Mock()
        mock_response.status_code = http.HTTPStatus.OK
        self.mock_requests.request = Mock(return_value=mock_response)
        
        wrapper = request_service.RequestsWrapper(self.mock_requests)
        result = wrapper.request('POST', 'https://api.example.com/charges', json={'amount': 100})
        
        assert_that(result.status_code).is_equal_to(200)
    
    def test_400_error_raises_exception(self):
        """✅ 400 Bad Request"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json = Mock(return_value={'error': 'Bad request'})
        self.mock_requests.request = Mock(return_value=mock_response)
        
        wrapper = request_service.RequestsWrapper(self.mock_requests)
        
        with self.assertRaises(exceptions.ResponseError):
            wrapper.request('GET', 'https://api.example.com/invalid')
    
    def test_401_error_raises_exception(self):
        """✅ 401 Unauthorized"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json = Mock(return_value={'error': 'Unauthorized'})
        self.mock_requests.request = Mock(return_value=mock_response)
        
        wrapper = request_service.RequestsWrapper(self.mock_requests)
        
        with self.assertRaises(exceptions.ResponseError):
            wrapper.request('GET', 'https://api.example.com/protected')
    
    def test_404_error_raises_exception(self):
        """✅ 404 Not Found"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json = Mock(return_value={'error': 'Not found'})
        self.mock_requests.request = Mock(return_value=mock_response)
        
        wrapper = request_service.RequestsWrapper(self.mock_requests)
        
        with self.assertRaises(exceptions.ResponseError):
            wrapper.request('GET', 'https://api.example.com/missing')
    
    def test_500_error_raises_exception(self):
        """✅ 500 Server Error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json = Mock(return_value={'error': 'Server error'})
        self.mock_requests.request = Mock(return_value=mock_response)
        
        wrapper = request_service.RequestsWrapper(self.mock_requests)
        
        with self.assertRaises(exceptions.ResponseError):
            wrapper.request('GET', 'https://api.example.com/error')
    
    @patch('api.services.request_service.logging')
    def test_logging_info_on_success(self, mock_logging):
        """✅ Logging info on success"""
        mock_response = Mock()
        mock_response.status_code = http.HTTPStatus.OK
        self.mock_requests.request = Mock(return_value=mock_response)
        
        wrapper = request_service.RequestsWrapper(self.mock_requests)
        wrapper.request('GET', 'https://api.example.com/data')
        
        mock_logging.info.assert_called_once()
    
    @patch('api.services.request_service.logging')
    def test_logging_error_on_failure(self, mock_logging):
        """✅ Logging error on failure"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json = Mock(return_value={'error': 'Server error'})
        self.mock_requests.request = Mock(return_value=mock_response)
        
        wrapper = request_service.RequestsWrapper(self.mock_requests)
        
        try:
            wrapper.request('GET', 'https://api.example.com/error')
        except exceptions.ResponseError:
            pass
        
        mock_logging.error.assert_called_once()
    
    def test_uses_default_requests(self):
        """✅ Uses default requests library"""
        wrapper = request_service.RequestsWrapper()
        assert_that(wrapper._requests).is_not_none()


class TestWiremockRequester(unittest.TestCase):
    """اختبار WiremockRequester"""
    
    def setUp(self):
        self.mock_requests = Mock()
    
    def test_successful_get_request(self):
        """✅ Wiremock GET success"""
        mock_response = Mock()
        mock_response.status_code = http.HTTPStatus.OK
        self.mock_requests.request = Mock(return_value=mock_response)
        
        wiremock = request_service.WiremockRequester(self.mock_requests)
        result = wiremock.request('GET', 'charges')
        
        assert_that(result.status_code).is_equal_to(200)
        self.mock_requests.request.assert_called_once_with('GET', '127.0.0.1:8080/charges')
    
    def test_successful_post_request(self):
        """✅ Wiremock POST success"""
        mock_response = Mock()
        mock_response.status_code = http.HTTPStatus.OK
        self.mock_requests.request = Mock(return_value=mock_response)
        
        wiremock = request_service.WiremockRequester(self.mock_requests)
        result = wiremock.request('POST', 'charges', json={'amount': 100})
        
        assert_that(result.status_code).is_equal_to(200)
    
    def test_400_error_raises_exception(self):
        """✅ Wiremock 400 error"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json = Mock(return_value={'error': 'Bad request'})
        self.mock_requests.request = Mock(return_value=mock_response)
        
        wiremock = request_service.WiremockRequester(self.mock_requests)
        
        with self.assertRaises(exceptions.ResponseError):
            wiremock.request('GET', 'invalid')
    
    def test_500_error_raises_exception(self):
        """✅ Wiremock 500 error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json = Mock(return_value={'error': 'Server error'})
        self.mock_requests.request = Mock(return_value=mock_response)
        
        wiremock = request_service.WiremockRequester(self.mock_requests)
        
        with self.assertRaises(exceptions.ResponseError):
            wiremock.request('GET', 'error')
    
    def test_url_construction(self):
        """✅ Wiremock URL construction"""
        mock_response = Mock()
        mock_response.status_code = http.HTTPStatus.OK
        self.mock_requests.request = Mock(return_value=mock_response)
        
        wiremock = request_service.WiremockRequester(self.mock_requests)
        wiremock.request('POST', 'users/1/charges')
        
        called_url = self.mock_requests.request.call_args[0][1]
        assert_that(called_url).is_equal_to('127.0.0.1:8080/users/1/charges')
    
    @patch('api.services.request_service.logging')
    def test_logging_on_success(self, mock_logging):
        """✅ Wiremock logging on success"""
        mock_response = Mock()
        mock_response.status_code = http.HTTPStatus.OK
        self.mock_requests.request = Mock(return_value=mock_response)
        
        wiremock = request_service.WiremockRequester(self.mock_requests)
        wiremock.request('GET', 'charges')
        
        mock_logging.info.assert_called_once()
        call_args = mock_logging.info.call_args[0][0]
        assert_that(call_args).contains('wiremock')
    
    @patch('api.services.request_service.logging')
    def test_logging_on_error(self, mock_logging):
        """✅ Wiremock logging on error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json = Mock(return_value={'error': 'Server error'})
        self.mock_requests.request = Mock(return_value=mock_response)
        
        wiremock = request_service.WiremockRequester(self.mock_requests)
        
        try:
            wiremock.request('GET', 'error')
        except exceptions.ResponseError:
            pass
        
        mock_logging.error.assert_called_once()
    
    def test_uses_default_requests(self):
        """✅ Wiremock uses default requests"""
        wiremock = request_service.WiremockRequester()
        assert_that(wiremock._requests).is_not_none()


if __name__ == '__main__':
    unittest.main(verbosity=2)