import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
from datetime import timedelta

###########  Supplier Metrics ###########
@anvil.server.callable
def revenue_by_supplier_and_date(start_date, end_date):
    import pytz

    revenue_by_supplier = {}
    
        
    all_items = app_tables.items.search()
    

    unique_suppliers = set()

    for item in all_items:
        unique_suppliers.add(item['supplier'])
    
    suppliers = list(unique_suppliers)
    print(suppliers)
   # Define the timezone
    desired_timezone = pytz.timezone('America/Chicago')
    start_date = datetime.strptime(str(start_date), "%m/%d/%Y")
    end_date = datetime.strptime(str(end_date), "%m/%d/%Y")
    start_date = desired_timezone.localize(start_date)
    end_date = desired_timezone.localize(end_date)
    for supplier in suppliers:
        sold_items = []
        kwargs = {'status': "Sold", 'supplier': supplier}
        items = app_tables.items.search(**kwargs)
        
        for row in items:
          if row['packed_on'] is None:
            print("")
            continue
          date_to_check = datetime.strptime(str(row['packed_on']), "%Y-%m-%d %H:%M:%S.%f%z")
          date_to_check = date_to_check.astimezone(desired_timezone)
          print(start_date,end_date,date_to_check)
          if start_date <= date_to_check <= end_date:
            sold_items.append(row)

        if len(sold_items) == 0:
          revenue_by_supplier[supplier] = 0
        else:
          total_revenue = sum(item['sale_price'] for item in sold_items)
          revenue_by_supplier[supplier] = total_revenue
    
    return revenue_by_supplier


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
def average_holding_time():
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
          format = "%m/%d/%Y at %I:%M:%S %p "
          date1 = datetime.strptime(timestamps[0], format)
          date2 = datetime.strptime(timestamps[1], format)
          
          time_diff = date2 - date1
          status_changes.append(time_diff)
    
    if status_changes:
        # Calculating the average
        total_timedelta = sum(status_changes, timedelta())
        average_timedelta = total_timedelta / len(status_changes)

        # Convert timedelta to a string representation
        average_timedelta_str = str(average_timedelta)

        return average_timedelta_str
    else:
        return 0  

@anvil.server.callable
def average_time_to_fulfill():
    items = app_tables.items.search()
    status_changes = []
    
    for item in items:
        history = item['history'].split('\n')
        timestamps = []
        for entry in history:
            if 'updated item status to Picked' in entry:
                new_time = entry.split('on ')[1].strip().rstrip('.')
                timestamps.append(new_time)
            elif 'updated item status to Packed' in entry:
                packed_time = entry.split('on ')[1].strip().rstrip('.')
                timestamps.append(packed_time)
        
        if len(timestamps) == 2:
          format = "%m/%d/%Y at %I:%M:%S %p "
          date1 = datetime.strptime(timestamps[0], format)
          date2 = datetime.strptime(timestamps[1], format)
          
          time_diff = date2 - date1
          status_changes.append(time_diff)
    
    if status_changes:
        # Calculating the average
        total_timedelta = sum(status_changes, timedelta())
        average_timedelta = total_timedelta / len(status_changes)

        # Convert timedelta to a string representation
        average_timedelta_str = str(average_timedelta)

        return average_timedelta_str
    else:
        return 0        
  

###########  Employee Metrics ###########

###########  Customer Metrics ###########