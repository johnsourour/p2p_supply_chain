class Smart_Contract(tx_input):
    import time
        
    def __init__(self, tx_input):
        self.seller = last_buyer 
        self.product_key = product_key
        self.price = asked_price
        self.sold = False ### set to True after purchase
        self.verify = False ### set to True after verification by buyer
        
    # to decide whether the price being asked for is fair or not, I decided to use the last price and add inflation
    # but also decrease the price by 10% for every year it was in the current owners possession. 
    # for the purposes of this demo, I will consider the inflation rate in Spain
    # I also assume that the product depreciates in value
    
    def cancel(self):
        assert not self.sold ### contract should only be cancellable as long as product hasn't been sold
        exit()
    
    def purchase(self, price):
        assert not self.sold ### to ensure contract is still open
        assert self.value == price ### ensure price paid is price asked for
        time_of_new_purchase = time.time()
        self.sold = True ### product has been sold
        print ("Please verify your product now.")
        self.verification()
    
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
        
        '''
        ### this is code for after integration
        tx_output = {}
        tx_output['Product Key'] = product_key_verification
        tx_output['Seller Address'] = self.seller
        tx_output['Price'] = self.price
        tx_output['Time of Purchase'] = time_of_new_purchase
        return tx_output
        '''
