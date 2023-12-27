import anvil.secrets
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

from ..DataTables import Common

@anvil.server.callable
def add_new_supplier(**kwargs):
  Common.add_row_to_table('suppliers', **kwargs)

@anvil.server.callable
def get_supplier_dropdown():
  results = app_tables.suppliers.search()
  return [(row['supplier_name'], row['supplier_name']) for row in results]

@anvil.server.callable
def get_unique_trucks():
  results = results_tables.mocktrucks.search()
  return list(set([row['truck_ID'] for row in results]))

@anvil.server.callable
def create_truck(truck_id, truck_created):
  app_tables.mocktrucks.add_row(truck_id = truck_id, truck_created=truck_created)

@anvil.server.callable
def update_item_count(trucks_table, items_table):
  truck_ids = app_tables.trucks_table.get_column('truck_id')
  print(truck_ids)
  for truck_id in truck_ids:
    result_rows = app_tables.items_table.search(truck=truck_id)
    item_system_count = len(result_rows)
    item_sold_count = len([item for item in result_rows if item['status'] == 'Sold'])
    item_return_count = len([item for item in result_rows if item['status'] == 'Returned'])
    item_defect_count = len([item for item in items_for_truck if 'Needs Fixed' in item['history']])

    truck_row = app_tables.trucks_table.get(truck_id=truck_id)

    if truck_row is not None:
        truck_row['item_system_count'] = num_rows
        truck_row.save()
        print(f"Campo 'item_system_count' atualizado para {num_rows} para o caminhão {truck_id}")
    else:
        print(f"Caminhão com ID {truck_id} não encontrado na tabela 'trucks'")
    
    # Obtendo o número de linhas correspondentes
    num_rows = len(count)
    print(f"O número de linhas na tabela 'items' para o caminhão {truck_id} é: {num_rows}")