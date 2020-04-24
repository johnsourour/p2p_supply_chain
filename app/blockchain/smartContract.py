import hashlib

class SmartContract:
    def __init__(self, data):
        self.seller = data["from_account"]
        self.product_key_hash = data["content"]
        self.price = float(data.get("amount", 0.0))
        self.sold = False ### set to True after purchase
        self.verify = False ### set to True after verification by buyer
        self.valid = True
        self.address = data["to_account"]
        self.buyer = []
        
    # to decide whether the price being asked for is fair or not, I decided to use the last price and add inflation
    # but also decrease the price by 10% for every year it was in the current owners possession. 
    # for the purposes of this demo, I will consider the inflation rate in Spain
    # I also assume that the product depreciates in value
    
    def cancel(self):
        if self.sold: ### contract should only be cancellable as long as product hasn't been sold
            return False
        self.valid = False
        return True
    
    def purchase(self, price, address, buyer):
        if self.sold or not self.valid or self.price!=price or address!=self.address:
            return False
        self.sold = True ### product has been sold
        self.buyer = buyer
        return True
    
    def verify(self, product_key_hash, buyer):
        if self.verify or product_key_hash!=self.product_key_hash or buyer!=self.buye:
            return False
        self.verify = True
        return True

    def get_seller(self):
        return self.seller

    def get_price(self):
        return self.price

    def get_address(self):
        return self.address

    def get_buyer(self):
        return self.buyer

    def is_sold(self):
        return self.sold

    def is_valid(self):
        return self.valid

