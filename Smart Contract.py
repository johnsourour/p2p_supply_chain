#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from public import public


# In[ ]:


### init function to initialize class variables 
class Smart_Contract():
    
    buyer = None
    value = None
    product_key = None
    
    @public
    def __init__(self, value, seller, product_key):
        self.product_key = product_key
        self.value = value
        self.seller = seller
        self.sold = False ### set to True after purchase
        self.verify = False ### set to True after verification by buyer

    @public
    def cancel(self):
        assert not self.sold ### contract should only be cancellable as long as product hasn't been sold
        exit()

    @public
    def verification(self):
        assert self.sold ### item should have been purchased for this function to be called
        assert not self.verify ### can't verify the same product 2 times
        
        product_key_verification = int(input('Please enter product key '))
        if product_key_verification == self.product_key:        
            self.verify = True
            print ('Product has been verified!')
        else:
            print ('Product key is not right.')
            self.verification()
    
    @public
    def purchase(self, price):
        assert not self.sold ### to ensure contract is still open
        assert self.value == price ### ensure price paid is price asked for
        self.sold = True ### product has been sold
        print ("Please verify your product now.")
        self.verification()

