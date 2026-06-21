import base64
import os


import api.services.request_service as request_service

STRIPE_PAYMENT_INTENTS_URL = "https://api.stripe.com/v1/payment_intents"
STRIPE_CUSTOMERS_URL = "https://api.stripe.com/v1/customers"



class  StripeClient:
    def __init__(self,env,test_request_sender=None,test_auth=None):
        
        self._env = env
        self._request_sender = test_request_sender or request_service.get_service(self._env)
        self._auth = test_auth or _StripeAuth(os.environ['STRIPE_SECRET_KEY'])

    def create_payment_intent(self,data):  
        response=self._request_sender.request( # type: ignore
            method="POST",
            url=STRIPE_PAYMENT_INTENTS_URL,
            data=data,
            headers=self._auth.headers # type: ignore
        )  
        return response
    
class _StripeAuth:    
    def __init__(self, secret_key):
        self.secret_key = secret_key

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.secret_key}"
        }    

    
