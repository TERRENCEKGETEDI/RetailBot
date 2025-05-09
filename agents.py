LOW_STOCK_THRESHOLD = 5
MAX_STOCK_LIMIT = 20

def check_low_stock(shop_inventory):
    return {item: qty for item, qty in shop_inventory.items() if qty < LOW_STOCK_THRESHOLD}

def generate_restock_request(low_stock_items, warehouse_inventory):
    return {
        item: min(warehouse_inventory.get(item, 0), MAX_STOCK_LIMIT - qty)
        for item, qty in low_stock_items.items()
    }

def handle_overstock(shop_inventory):
    return {
        item: qty - MAX_STOCK_LIMIT
        for item, qty in shop_inventory.items() if qty > MAX_STOCK_LIMIT
    }
