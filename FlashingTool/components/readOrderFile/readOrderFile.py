# components/readOrderFile.py

def parse_order_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    orders = []
    for line in lines:
        order_data = {}
        pairs = line.split(', ')
        for pair in pairs:
            key, value = pair.split(': ', 1)
            order_data[key] = value
        orders.append(order_data)
    
    return orders
