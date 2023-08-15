class BitMapManager:
  def __init__(self, permissions_map, modules_map):
    self.permissions_map = permissions_map
    self.modules_map = modules_map

  def check_bit_map(self, bit_map, module, permission):
    bit_map_ = list(bit_map)
    index = self.modules_map[module]
    permission_index = self.permissions_map.index(permission)
    combined_index = index + permission_index

    return bool(int(bit_map_[combined_index]))


  # "gcc:get-qemu:get:kill"
  def convert_str_to_dict(self, str_permissions):
    parts = str_permissions.split("-")
    result = {}

    for part in parts:
      split_parts = part.split(":")
      key = split_parts[0]
      values = split_parts[1:] if len(split_parts) > 1 else []
      result[key] = values
    
    return result

  def add_permission(self, bit_map, permits):

    bit_map_ = list(bit_map)
    permits = self.convert_str_to_dict(permits)

    for module, permissions in permits.items():
      module_index = self.modules_map[module]
      for permission in permissions:
        permission_index = self.permissions_map.index(permission)
        combined_index = module_index + permission_index
        bit_map_[combined_index] = "1"

    return "".join(bit_map_)

  def remove_permission(self, bit_map, module, permissions):
    module_index = self.modules_map[module]

    for permission in permissions:
      perission_index = self.permissions_map.index(permission)
      combined_index = module_index + perission_index
      bit_map[:combined_index] = "0"

    return str(bit_map)

  def get_bit_map(self):
    return "0" * (len(self.modules_map) * len(self.permissions_map))
