import unittest
import os
from assertpy import assert_that

import api.services.request_service as request_service
import api.services.payment.stripe as stripe
import tests.doubles.requests as requests_doubles


class TestStripe(unittest.TestCase):
    """اختبارات Stripe Client"""
    
    def setUp(self):
        """التحضير قبل كل اختبار"""
        os.environ['STRIPE_SECRET_KEY'] = 'fake_secret_key'
        self.request_sender = requests_doubles.RequestSenderDouble(json={'id': 'pi_fake_123'})
        self.client = stripe.StripeClient('lcl', self.request_sender)
    
    # ===== TEST 1: Dependency Injection =====
    
    def test_client_uses_real_if_double_are_not_sent(self):
        """✅ لو ما مرّيت double، بيستخدم الحقيقي"""
        client_without_double = stripe.StripeClient('lcl')
        
        # تحقق: استخدم RequestsWrapper (الحقيقي)
        assert_that(client_without_double._request_sender)\
            .is_instance_of(request_service.RequestsWrapper)
        
        print("✅ Test 1: Client uses real if double not sent")
    
    # ===== TEST 2: Create Payment Intent =====
    
    def test_create_payment_intent_calls_stripe_correctly(self):
        """✅ create_payment_intent بينادي الـ API صح"""
        response = self.client.create_payment_intent(data='fake data')
        
        # تحقق: الـ response صحيح
        assert_that(response.json().get('id'))\
            .is_equal_to('pi_fake_123')
        
        # تحقق: اتنادت مع الـ arguments الصحيح
        self.request_sender.assert_that_request_is_called_with(
            method='POST',
            url=stripe.STRIPE_PAYMENT_INTENTS_URL,
            data='fake data',
            headers={
                "Authorization": "Bearer fake_secret_key"
            }
        )
        
        print("✅ Test 2: Create payment intent calls Stripe correctly")
    
    # ===== TEST 3: Auth Headers =====
    
    def test_auth_headers_are_set_correctly(self):
        """✅ Auth headers صحيحة"""
        headers = self.client._auth.headers
        
        # تحقق: فيها Authorization header
        assert_that(headers)\
            .contains("Authorization")
        
        # تحقق: القيمة صحيحة
        assert_that(headers["Authorization"])\
            .is_equal_to("Bearer fake_secret_key")
        
        print("✅ Test 3: Auth headers are set correctly")
    
    # ===== TEST 4: Multiple Calls =====
    
    def test_multiple_payment_intents(self):
        """✅ استدعاء متعدد للـ create_payment_intent"""
        response1 = self.client.create_payment_intent(data='data1')
        response2 = self.client.create_payment_intent(data='data2')
        
        # تحقق: كل مرة ترجع نفس الـ response
        assert_that(response1.json().get('id'))\
            .is_equal_to('pi_fake_123')
        
        assert_that(response2.json().get('id'))\
            .is_equal_to('pi_fake_123')
        
        print("✅ Test 4: Multiple payment intents")
    
    # ===== TEST 5: Custom Auth =====
    
    def test_client_uses_custom_auth_if_provided(self):
        """✅ لو مرّيت custom auth double، يستخدمها"""
        custom_auth = requests_doubles.CustomAuthDouble(token='custom_token_123')
        
        client_with_custom_auth = stripe.StripeClient(
            'lcl',
            test_request_sender=self.request_sender,
            test_auth=custom_auth
        )
        
        # تحقق: استخدم الـ custom auth
        assert_that(client_with_custom_auth._auth)\
            .is_equal_to(custom_auth)
        
        # تحقق: الـ headers صحيح
        headers = client_with_custom_auth._auth.headers
        assert_that(headers['Authorization'])\
            .is_equal_to('Bearer custom_token_123')
        
        print("✅ Test 5: Client uses custom auth if provided")
    
    # ===== TEST 6: Different Environments =====
    
    def test_different_environments(self):
        """✅ بيئات مختلفة"""
        
        # في development
        client_lcl = stripe.StripeClient('lcl', self.request_sender)
        assert_that(client_lcl._env).is_equal_to('lcl')
        
        # في testing
        client_test = stripe.StripeClient('test', self.request_sender)
        assert_that(client_test._env).is_equal_to('test')
        
        print("✅ Test 6: Different environments")
    
    # ===== TEST 7: Payment Intent with Different Data =====
    
    def test_create_payment_intent_with_different_amounts(self):
        data1 = {'amount': 100, 'currency': 'usd'}
        data2 = {'amount': 500, 'currency': 'eur'}
        
        response1 = self.client.create_payment_intent(data=data1)
        response2 = self.client.create_payment_intent(data=data2)
        
        assert_that(response1.json().get('id')).is_equal_to('pi_fake_123')
        assert_that(response2.json().get('id')).is_equal_to('pi_fake_123')
        
        # تحقق: اتنادت مع البيانات الصحيحة
        self.request_sender.assert_that_request_is_called_with(
            method='POST',
            url=stripe.STRIPE_PAYMENT_INTENTS_URL,
            data=data2,
            headers={"Authorization": "Bearer fake_secret_key"}
        )
        
        print("✅ Test 7: Payment intent with different amounts")


if __name__ == '__main__':
    unittest.main(verbosity=2)