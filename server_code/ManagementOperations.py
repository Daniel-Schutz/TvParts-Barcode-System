import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime

###########  Supplier Metrics ###########
@anvil.server.callable
def tossed_rate_per_truck():
    trucks = app_tables.trucks.search()
    tossed_rate = {}
    
    for truck in trucks:
        tossed_count = truck['item_tossed_count']
        total_count = truck['item_system_count']
        truck_name = truck['truck_id']
        if tossed_count is not None and total_count is not None:
          if total_count == 0:
            tossed_rate[truck_name] = 0
          else:
            tossed_rate[truck_name] = (tossed_count/total_count)*100
          
    return tossed_rate
  
@anvil.server.callable
def count_items_per_year():
    items = app_tables.items.search()
    year_count = {}
    
    # Iterate through each item and tally the counts for each year
    for item in items:
        year = item['year']
        if year is not None:
            year_str = str(year)  # Convert the year to string
            if year_str in year_count:
                year_count[year_str] += 1
            else:
                year_count[year_str] = 1
    
    return year_count

@anvil.server.callable
def count_items_per_brand():
    items = app_tables.items.search()
    brand_count = {}
    
    # Iterate through each item and tally the counts for each year
    for item in items:
        brand = item['make']
        if brand is not None:
            if brand in brand_count:
                brand_count[brand] += 1
            else:
                brand_count[brand] = 1
    
    return brand_count

@anvil.server.callable
def count_items_per_model():
    items = app_tables.items.search()
    model_count = {}
    
    # Iterate through each item and tally the counts for each year
    for item in items:
        model = item['model']
        if model is not None:
            if model in model_count:
                model_count[model] += 1
            else:
                model_count[model] = 1
    
    return model_count


###########  Product Metrics ###########


@anvil.server.callable
def average_time_new_to_packed():
    items = app_tables.items.search()
    status_changes = []
    
    for item in items:
        history = item['history'].split('\n')
        timestamps = []
        for entry in history:
            if 'updated item status to New' in entry:
                new_time = entry.split('on ')[1].strip().rstrip('.')
  
                timestamps.append(new_time)
            elif 'updated item status to Packed' in entry:
                packed_time = entry.split('on ')[1].strip().rstrip('.')
                timestamps.append(packed_time)
        
        if len(timestamps) == 2:
          print(timestamps)
          time_diff = 1
          status_changes.append(time_diff)
    
    if status_changes:
        avg_time = sum(status_changes) / len(status_changes)
        return avg_time / 3600  # Convertendo para horas (opcional)
    else:
        return 0  # Retorna 0 se não houver itens que tenham passado por esses status
  

###########  Employee Metrics ###########

###########  Customer Metrics ###########