class OrderManager:
    """
    OrderManager Class Has Responsibility for:
        - Retrieve Buy/Sell Orders From StrategyManager
        - Execute Buy/Sell Orders 
    """
    def __init__(self):
        self.orders = None
        self.interface = None
        pass
    
    def retrieve_orders(self, orders):
        self.orders = orders
        pass

    def execute_orders(self):
        pass

        

