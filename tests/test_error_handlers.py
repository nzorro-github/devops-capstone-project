"""
Unit Test for error_handlers
"""
from unittest import TestCase
from service.common import error_handlers as eh


class TestErrorHandlers(TestCase):
    """Test Error Handlers"""

    def setUp(self):
        self._Debug = False

    def test_not_found(self):
        """Test handling of HTTP_404"""
        status_code = eh.status.HTTP_404_NOT_FOUND
        
        res, status = eh.not_found(status_code)
        self.assertEqual(status, status_code)
        self.assertEqual(res.get_json()['status'], status_code)
        self.assertGreater(len(res.get_json()['error']), 0)
        self.assertGreater(len(res.get_json()['message']), 0)
   
    def test_method_not_supported(self):
        """Tests handling of method not supported"""
        status_code = eh.status.HTTP_405_METHOD_NOT_ALLOWED
        res, status = eh.method_not_supported(status_code)
        self.assertEqual(status, status_code)
        self.assertEqual(res.get_json()['status'], status_code)
        self.assertGreater(len(res.get_json()['error']), 0)
        self.assertGreater(len(res.get_json()['message']), 0)

    def test_internal_server_error(self):
        """Tests handling of internal server error"""
        status_code = eh.status.HTTP_500_INTERNAL_SERVER_ERROR
        res,status = eh.internal_server_error(status_code)
        self.assertEqual(status, status_code)
        self.assertEqual(res.get_json()['status'], status_code)
        self.assertGreater(len(res.get_json()['error']),0)
        self.assertGreater(len(res.get_json()['message']),0)
