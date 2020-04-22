import hashlib

class SmartContract:
    def __init__(self, data, address):
        self.seller = data["from_account"]
        self.product_key_hash = data["content"]
        self.price = data["amount"]
        self.sold = False ### set to True after purchase
        self.verify = False ### set to True after verification by buyer
        self.valid = True
        self.address = address
        
    # to decide whether the price being asked for is fair or not, I decided to use the last price and add inflation
    # but also decrease the price by 10% for every year it was in the current owners possession. 
    # for the purposes of this demo, I will consider the inflation rate in Spain
    # I also assume that the product depreciates in value
    
    def cancel(self):
        if self.sold: ### contract should only be cancellable as long as product hasn't been sold
            return False
        self.valid = False
        return True
    
    def purchase(self, price, product_key_hash):
        if self.sold or not self.valid or self.value!=price:
            return False
        self.sold = True ### product has been sold
        return self.verification(product_key_hash)
    
    def verification(self, product_key_hash):
        if self.verify or product_key_hash!=self.product_key_hash:
            return False
        self.verify = True
        return True

    def get_address(self):
        return self.address
        
        '''
        ### this is code for after integration
        tx_output = {}
        tx_output['Product Key'] = product_key_verification
        tx_output['Seller Address'] = self.seller
        tx_output['Price'] = self.price
        tx_output['Time of Purchase'] = time_of_new_purchase
        return tx_output
        '''
