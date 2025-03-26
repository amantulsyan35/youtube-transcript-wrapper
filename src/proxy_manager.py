from free_proxy import FreeProxy
import random
import logging

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.refresh_proxies()
    
    def refresh_proxies(self):
        """Fetch new proxies when needed"""
        try:
            # Get HTTPS proxies with a 1 second timeout
            proxy_list = FreeProxy(https=True, timeout=1).get_proxy_list()
            if proxy_list:
                self.proxies = proxy_list
                logging.info(f"Refreshed proxy list. Got {len(self.proxies)} proxies.")
            else:
                logging.warning("Failed to get any proxies.")
        except Exception as e:
            logging.error(f"Error refreshing proxies: {str(e)}")
    
    def get_proxy(self):
        """Get a random proxy from the list"""
        if not self.proxies:
            self.refresh_proxies()
            
        if not self.proxies:
            return None
            
        proxy = random.choice(self.proxies)
        return {
            'http': proxy,
            'https': proxy
        }