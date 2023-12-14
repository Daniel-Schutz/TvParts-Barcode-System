from ._anvil_designer import HomePageTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ..EntryComponents.ChooseRole import ChooseRole
from ..CommonComponents.SendMessages import SendMessages
from ..CommonComponents.RecieveMessages import RecieveMessages
from ..CommonComponents.ProductExplorer import ProductExplorer
from ..CommonComponents.ItemLookup import ItemLookup

from ..ProductionPages.Temp_ServerTest import Temp_ServerTest

# from ..ProductionPages.ManagementMasterModule import ManagementMasterModule
# from ..ProductionPages.TeardownModule import TeardownModule
# from ..ProductionPages.IdModule import IdModule
# from ..ProductionPages.WarehousePickModule import WarehousePickModule
# from ..ProductionPages.WarehouseStockModule import WarehouseStockModule
# from ..ProductionPages.TestingModule import TestingModule
# from ..ProductionPages.ShippingModule import ShippingModule

class HomePage(HomePageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # anvil.server.events.message_update += self.message_update_handler
    self.show_links()
    if anvil.users.get_user():
      self.current_user = anvil.server.call('get_user_full_name')
      self.user_role = anvil.server.call('get_user_role')
      self.update_notifications()
      self.role_navigation()
      


########## MAIN #############################
  def show_links(self):
    print("show_links called")
    user = anvil.users.get_user()
    print(f"User logged in: {user is not None}")
    if user:
      self.sign_out_link.visible = True
      self.sign_in_link.visible = False
      #self.test_area.visible = True
      self.send_message_btn.visible = True
      self.role_home_btn.visible = True
      self.recieved_msgs_btn.visible = True
      self.product_explorer_btn.visible = True
      self.lookup_by_scan_btn.visible = True
      print(f"test_area visibility set to: {self.test_area.visible}")
        

  def role_navigation(self):
    try:
      user = self.current_user
      user_role = self.user_role
      if user_role is not None:
        self.role_router()
      else:
        self.content_panel.add_component(ChooseRole(), full_width_row=True)
    except:
      self.show_links()
    
  def role_router(self):
    try:
      current_user = self.current_user
      current_role = self.user_role
      if current_role == "Teardown":
        from ..ProductionPages.TeardownModule import TeardownModule
        self.content_panel.add_component(TeardownModule(current_user=current_user,
                                                        current_role=current_role), 
                                        full_width_row=True)
      elif current_role == 'ID':
        from ..ProductionPages.IdModule import IdModule
        self.content_panel.add_component(IdModule(current_user=current_user,
                                                        current_role=current_role),
                                        full_width_row=True)
      elif current_role == 'Warehouse':
        from ..ProductionPages.WarehousePickModule import WarehousePickModule
        from ..ProductionPages.WarehouseStockModule import WarehouseStockModule
        self.content_panel.add_component(WarehouseStockModule(current_user=current_user,
                                                        current_role=current_role),
                                        full_width_row=True)
      elif current_role == 'Testing':
        from ..ProductionPages.TestingModule import TestingModule
        self.content_panel.add_component(TestingModule(current_user=current_user,
                                                        current_role=current_role),
                                        full_width_row=True)
      elif current_role == 'Shipping':
        from ..ProductionPages.ShippingModule import ShippingModule
        self.content_panel.add_component(ShippingModule(current_user=current_user,
                                                        current_role=current_role),
                                        full_width_row=True)
      elif current_role == 'Management':
        from ..ProductionPages.ManagementMasterModule import ManagementMasterModule
        self.content_panel.add_component(ManagementMasterModule(current_user=current_user,
                                                        current_role=current_role),
                                        full_width_row=True)
    except:
      pass

######## HOME PAGE EVENTS ############################  

  # def settings_link_click(self, **event_args):
  #   """This method is called when the link is clicked"""
  #   if anvil.server.call('check_admin'):
  #     get_open_form().content_panel.clear()
  #     get_open_form().content_panel.add_component(AdminSettings())

  def sign_out_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    anvil.users.logout()
    self.content_panel.clear()
    open_form('HomePage')

  def sign_in_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    anvil.users.login_with_form()
    self.role_navigation()
    self.show_links()
    #open_form('HomePage')


  def send_message_click(self, **event_args):
    """This method is called when the link is clicked"""
    send_msg_modal = SendMessages()
    anvil.alert(
      send_msg_modal, 
      title="Send New Message",
      buttons=[],
      large=True
    )
    self.update_notifications()
    
  def test_area_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.content_panel.clear()
    self.content_panel.add_component(Temp_ServerTest(), full_width_row=True)

  def product_explorer_click(self, **event_args):
    """This method is called when the link is clicked"""
    product_explorer_modal = ProductExplorer()
    selected_value = anvil.alert(
      product_explorer_modal, 
      title="Product Explorer",
      buttons=["CLOSE"],
      large=True
    )
    #self.content_panel.clear()
    #self.content_panel.add_component(ProductExplorer(), full_width_row=True)

  def find_item_btn_click(self, **event_args):
    """This method is called when the link is clicked"""
    item_lookup_modal = ItemLookup()
    selected_value = anvil.alert(
      item_lookup_modal,
      buttons=["CLOSE"],
      large=True
    ) 

  def mail_click(self, **event_args):
    recieve_msg_modal = RecieveMessages()
    anvil.alert(
      recieve_msg_modal, 
      title="All Messages",
      buttons=["CLOSE"],
      large=True
    )
    self.update_notifications()
#########################################################

#### Notification System: Event Handlers ################
  # def message_update_handler(self, **event_args):
  #   # Update the message notifier when the server event is triggered
  #   self.update_message_notifier()
  
  # def update_message_notifier(self):
  #   # Get the number of unread messages for the logged-in user's role
  #   role_to = anvil.users.get_user()['role']
  #   unread_count = anvil.server.call('get_unread_messages_count', role_to)
      
  #     # Update the label text and visibility
  #   self.msg_notifier.text = str(unread_count)
  #   self.msg_notifier.visible = unread_count > 0

  # def clean_up_on_hide(self, **event_args):
  #   # Remove the event handler for the server event
  #   anvil.server.events.message_update -= self.message_update_handler

  def timer_tick(self, **event_args):
  # This function is called at regular intervals
    self.update_notifications()

  def update_notifications(self):
    # Get the number of new messages
    user = anvil.users.get_user()
    user_role = self.user_role
    new_count = anvil.server.call_s('get_unread_messages_count', user_role)
    # Update your notifications display based on new_count
    self.msg_notifier.text = str(new_count)
    # Show or hide the notifier based on the count
    self.msg_notifier.visible = new_count > 0
#########################################################

  def role_home_btn_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.content_panel.clear()
    self.role_navigation()