import paypalrestsdk
from flask import current_app
import time
import requests


class PayPalService:
    @staticmethod
    def configure():
        """Configure PayPal SDK with credentials from Flask config"""
        client_id = current_app.config.get('PAYPAL_CLIENT_ID')
        client_secret = current_app.config.get('PAYPAL_CLIENT_SECRET')
        mode = current_app.config.get('PAYPAL_MODE', 'sandbox')
        
        if not client_id or not client_secret:
            raise ValueError("PayPal credentials are missing. Please check your .env file.")
        
        paypalrestsdk.configure({
            "mode": mode,
            "client_id": client_id,
            "client_secret": client_secret
        })
        
        # Configure requests timeout globally
        if hasattr(requests, 'Session'):
            session = requests.Session()
            session.timeout = 30
    
    @staticmethod
    def _retry_with_backoff(func, max_retries=3, initial_delay=1):
        """Retry function with exponential backoff"""
        last_exception = None
        for attempt in range(max_retries):
            try:
                return func()
            except (requests.exceptions.Timeout, 
                    requests.exceptions.ConnectionError,
                    requests.exceptions.ConnectTimeout,
                    requests.exceptions.ReadTimeout,
                    requests.exceptions.RequestException) as e:
                last_exception = e
                if attempt == max_retries - 1:
                    break
                delay = initial_delay * (2 ** attempt)
                time.sleep(delay)
            except Exception as e:
                error_str = str(e).lower()
                if 'timeout' in error_str or 'connection' in error_str or 'connect' in error_str:
                    last_exception = e
                    if attempt == max_retries - 1:
                        break
                    delay = initial_delay * (2 ** attempt)
                    time.sleep(delay)
                else:
                    raise
        if last_exception:
            raise last_exception
        return None
    
    @staticmethod
    def create_payment(amount, booking_code, booking_id=None, currency='USD'):
        """Create a PayPal payment with retry logic"""
        try:
            PayPalService.configure()
            
            return_url = current_app.config.get('PAYPAL_RETURN_URL')
            cancel_url = current_app.config.get('PAYPAL_CANCEL_URL')
            
            if not return_url or not cancel_url:
                return {
                    'success': False, 
                    'error': 'PayPal return/cancel URLs are not configured'
                }
            
            if booking_id:
                from urllib.parse import urlencode
                separator = '&' if '?' in return_url else '?'
                return_url = f"{return_url}{separator}booking_id={booking_id}"
                separator = '&' if '?' in cancel_url else '?'
                cancel_url = f"{cancel_url}{separator}booking_id={booking_id}"
            
            payment_data = {
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "redirect_urls": {
                    "return_url": return_url,
                    "cancel_url": cancel_url
                },
                "transactions": [{
                    "amount": {
                        "total": str(round(amount, 2)),
                        "currency": currency
                    },
                    "description": f"Booking {booking_code}"
                }]
            }
            
            def _create_payment():
                payment = paypalrestsdk.Payment(payment_data)
                if payment.create():
                    approval_url = next((link.href for link in payment.links if link.rel == 'approval_url'), None)
                    return {
                        'success': True, 
                        'payment_id': payment.id, 
                        'approval_url': approval_url,
                        'payment': payment
                    }
                
                error_msg = "Unknown error"
                if hasattr(payment, 'error') and payment.error:
                    if isinstance(payment.error, dict):
                        error_msg = payment.error.get('message', str(payment.error))
                    else:
                        error_msg = str(payment.error)
                
                return {'success': False, 'error': error_msg, 'payment': payment}
            
            result = PayPalService._retry_with_backoff(_create_payment, max_retries=3, initial_delay=1)
            
            if result and result.get('success'):
                return {
                    'success': True,
                    'payment_id': result.get('payment_id'),
                    'approval_url': result.get('approval_url')
                }
            
            error_msg = result.get('error', 'Unknown error') if result else 'Connection timeout'
            return {'success': False, 'error': error_msg}
            
        except ValueError as e:
            return {'success': False, 'error': str(e)}
        except (requests.exceptions.Timeout, 
                requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout,
                requests.exceptions.RequestException) as e:
            return {'success': False, 'error': 'Không thể kết nối đến PayPal. Vui lòng kiểm tra kết nối mạng và thử lại sau.'}
        except Exception as e:
            error_msg = str(e)
            error_lower = error_msg.lower()
            if any(keyword in error_lower for keyword in ['timeout', 'connection', 'connect', 'max retries', 'connection pool']):
                return {'success': False, 'error': 'Kết nối PayPal bị timeout. Vui lòng thử lại sau.'}
            return {'success': False, 'error': f'PayPal error: {error_msg}'}
    
    @staticmethod
    def execute_payment(payment_id, payer_id):
        """Execute a PayPal payment after user approval with retry logic"""
        try:
            PayPalService.configure()
            
            def _find_and_execute():
                payment = paypalrestsdk.Payment.find(payment_id)
                
                if not payment:
                    return {'success': False, 'error': 'Payment not found'}
                
                if payment.execute({"payer_id": payer_id}):
                    return {'success': True, 'payment': payment}
                
                error_msg = "Unknown error"
                if hasattr(payment, 'error') and payment.error:
                    if isinstance(payment.error, dict):
                        error_msg = payment.error.get('message', str(payment.error))
                    else:
                        error_msg = str(payment.error)
                
                return {'success': False, 'error': error_msg, 'payment': payment}
            
            result = PayPalService._retry_with_backoff(_find_and_execute, max_retries=3, initial_delay=1)
            
            if result and result.get('success'):
                return {'success': True, 'payment': result.get('payment')}
            
            error_msg = result.get('error', 'Unknown error') if result else 'Connection timeout'
            return {'success': False, 'error': error_msg}
            
        except ValueError as e:
            return {'success': False, 'error': str(e)}
        except (requests.exceptions.Timeout, 
                requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout) as e:
            return {'success': False, 'error': f'Không thể kết nối đến PayPal. Vui lòng thử lại sau. ({str(e)})'}
        except Exception as e:
            error_msg = str(e)
            if 'timeout' in error_msg.lower() or 'connection' in error_msg.lower():
                return {'success': False, 'error': 'Kết nối PayPal bị timeout. Vui lòng thử lại sau.'}
            return {'success': False, 'error': f'PayPal execution error: {error_msg}'}

