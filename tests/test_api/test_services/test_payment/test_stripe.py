import unittest
import os
from assertpy import assert_that

import api.services.request_service as request_service
import api.services.payment.stripe as stripe
import tests.doubles.requests as requests_doubles


class TestStripe(unittest.TestCase):    
    def setUp(self):
        os.environ['STRIPE_SECRET_KEY'] = 'fake_secret_key'
        self.request_sender = requests_doubles.RequestSenderDouble(json={'id': 'pi_fake_123'})
        self.client = stripe.StripeClient('lcl', self.request_sender)
    
    
    def test_client_uses_real_if_double_are_not_sent(self):
        client_without_double = stripe.StripeClient('lcl')
        
        assert_that(client_without_double._request_sender)\
            .is_instance_of(request_service.RequestsWrapper)
        
        print("✅ Test 1: Client uses real if double not sent")
        
    def test_create_payment_intent_calls_stripe_correctly(self):
        response = self.client.create_payment_intent(data='fake data')
        
        assert_that(response.json().get('id'))\
            .is_equal_to('pi_fake_123')
        
        self.request_sender.assert_that_request_is_called_with(
            method='POST',
            url=stripe.STRIPE_PAYMENT_INTENTS_URL,
            data='fake data',
            headers={
                "Authorization": "Bearer fake_secret_key"
            }
        )
                
    def test_auth_headers_are_set_correctly(self):
        headers = self.client._auth.headers
        
        assert_that(headers)\
            .contains("Authorization")
        
        assert_that(headers["Authorization"])\
            .is_equal_to("Bearer fake_secret_key")
        
        print("✅ Test 3: Auth headers are set correctly")
        
    def test_multiple_payment_intents(self):
        response1 = self.client.create_payment_intent(data='data1')
        response2 = self.client.create_payment_intent(data='data2')
        
        assert_that(response1.json().get('id'))\
            .is_equal_to('pi_fake_123')
        
        assert_that(response2.json().get('id'))\
            .is_equal_to('pi_fake_123')
        
        print("✅ Test 4: Multiple payment intents")
        
    def test_client_uses_custom_auth_if_provided(self):
        custom_auth = requests_doubles.CustomAuthDouble(token='custom_token_123')
        
        client_with_custom_auth = stripe.StripeClient(
            'lcl',
            test_request_sender=self.request_sender,
            test_auth=custom_auth
        )
        
        assert_that(client_with_custom_auth._auth)\
            .is_equal_to(custom_auth)
        
        headers = client_with_custom_auth._auth.headers
        assert_that(headers['Authorization'])\
            .is_equal_to('Bearer custom_token_123')
        
        print("✅ Test 5: Client uses custom auth if provided")
    
    
    def test_different_environments(self):        
        client_lcl = stripe.StripeClient('lcl', self.request_sender)
        assert_that(client_lcl._env).is_equal_to('lcl')
        
        client_test = stripe.StripeClient('test', self.request_sender)
        assert_that(client_test._env).is_equal_to('test')
    
    
    def test_create_payment_intent_with_different_amounts(self):
        data1 = {'amount': 100, 'currency': 'usd'}
        data2 = {'amount': 500, 'currency': 'eur'}
        
        response1 = self.client.create_payment_intent(data=data1)
        response2 = self.client.create_payment_intent(data=data2)
        
        assert_that(response1.json().get('id')).is_equal_to('pi_fake_123')
        assert_that(response2.json().get('id')).is_equal_to('pi_fake_123')
        
        self.request_sender.assert_that_request_is_called_with(
            method='POST',
            url=stripe.STRIPE_PAYMENT_INTENTS_URL,
            data=data2,
            headers={"Authorization": "Bearer fake_secret_key"}
        )
        


if __name__ == '__main__':
    unittest.main(verbosity=2)