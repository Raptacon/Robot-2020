from utils.filemanager import FileManager as file
import utils.hardware.base_hardware_objects as base_hardware_objects

def generate_hardware_objects(robot, hardware_map=".hardware.map.json"):
    """
    Generate injectable dictionaries for components.

    :param robot: The robot to set dictionary attributes to.

    :param hardware_map: If desired, specify a custom hardware mapping to 
    be used.
    """

    def new_hardware_object(desc):
        """
        Generate a new hardware object.
        Look through the base_hardware_objects file and find the
        appropriate constructor object.
        """

        obj_type = desc.pop("type")
        constructor = getattr(base_hardware_objects, obj_type)
        return constructor() if not bool(desc) else constructor(desc)

    for general_type, all_objects in file.load(hardware_map):
        for subsystem_name, subsystem_items in all_objects.items():
            for item_name, item_desc in subsystem_items.items():
                obj = new_hardware_object(item_desc)
                subsystem_items[item_name] = obj
            group_subsystem = "_".join([general_type, subsystem_name])
            setattr(robot, group_subsystem)
