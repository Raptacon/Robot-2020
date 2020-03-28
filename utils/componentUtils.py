"""
File to hold misc component helper commands
"""

import components
import typing

def testComponentCompatibility(robot, component_type):
    """
    takes a robot and a component_type to check
    If the component is not compatibile with the robot type, it will attempt to create basic bindings and
    disable the on_enable and execute() methods of the compeont.
    """
    # Iterate over variables with type annotations
    if not hasattr(component_type, "compatString"):
        robot.logger.warn("%s has no compatString set. Assuming compatible", component_type)
        return

    if robot.mapper.checkCompatibility(component_type.compatString):
        return

    robot.logger.warn("%s is not compatible. Disabling", component_type)

    for n, inject_type in typing.get_type_hints(component_type).items():
        # If the variable is private ignore it
        if n.startswith("_"):
            continue
        # If the variable has been set, skip it
        if hasattr(component_type, n):
            continue

        # Check for generic types from the typing module
        origin = getattr(inject_type, "__origin__", None)
        if origin is not None:
            inject_type = origin

        # If the type is not actually a type, give a meaningful error
        if not isinstance(inject_type, type):
            raise TypeError(
                "Component %s has a non-type annotation on %s (%r); lone non-injection variable annotations are disallowed, did you want to assign a static variable?"
                % (inject_type, n, inject_type)
            )
        
        if not hasattr(robot, n):
            #Create any injectables we need
            robot.logger.info("Creating variable %s for robot", n)
            setattr(robot, n, inject_type())

    #First pass this will not always work can expand to make better
    #This will let the component not use the real ones.
    component_type.execute = components.dummyFunc
    component_type.on_enable = components.dummyFunc
    component_type.setup = components.dummyFunc
