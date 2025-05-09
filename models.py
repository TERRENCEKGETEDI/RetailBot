import json

WAREHOUSE_STOCK_FILE = 'data/warehouse_stock.json'
SHOP_STOCK_FILE = 'data/shop_stock.json'
LOW_STOCK_THRESHOLD = 5

def load_warehouse_stock():
    with open(WAREHOUSE_STOCK_FILE, 'r') as f:
        return json.load(f)

def save_warehouse_stock(stock):
    with open(WAREHOUSE_STOCK_FILE, 'w') as f:
        json.dump(stock, f, indent=4)

def load_shop_stock():
    with open(SHOP_STOCK_FILE, 'r') as f:
        return json.load(f)

def save_shop_stock(stock):
    with open(SHOP_STOCK_FILE, 'w') as f:
        json.dump(stock, f, indent=4)

def get_shop_stock(shop_id):
    shop_data = load_shop_stock()
    return shop_data.get(shop_id, {})

def update_shop_stock(shop_id, product, quantity):
    shop_data = load_shop_stock()
    if shop_id not in shop_data:
        shop_data[shop_id] = {}
    shop_data[shop_id][product] = quantity
    save_shop_stock(shop_data)

def get_warehouse_stock(product):
    warehouse_data = load_warehouse_stock()
    return warehouse_data.get(product, 0)

def update_warehouse_stock(product, quantity_change):
    warehouse_data = load_warehouse_stock()
    warehouse_data[product] = warehouse_data.get(product, 0) + quantity_change
    save_warehouse_stock(warehouse_data)

def add_warehouse_product(product, initial_quantity=0):
    warehouse_data = load_warehouse_stock()
    if product not in warehouse_data:
        warehouse_data[product] = initial_quantity
        save_warehouse_stock(warehouse_data)
        return True
    return False # Product already exists

def delete_warehouse_product(product):
    warehouse_data = load_warehouse_stock()
    if product in warehouse_data:
        del warehouse_data[product]
        save_warehouse_stock(warehouse_data)
        return True
    return False # Product not found