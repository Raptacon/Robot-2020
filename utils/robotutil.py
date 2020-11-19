import wpilib  # only for annotations
import typing


def cleanup_components(robot_cls: wpilib.RobotBase, *, key: str):
    """Remove incompatable components.

    If multiple robots are being used and the components
    for these robots are defined in one robot class, this
    fucntion eill remove any incompatable components from
    the robot class. All components MUST have a `robot`
    attribute to determine what robot they belong to.

    :param robot_cls: Base robot class to check components
    for (i.e. `MyRobot`).

    :param key: Key used to determine what components to use.
    If a component doesn't have this key in it's `robot`
    attribute, it is removed and not used in the robot.
    This is typically (and should be) the name of the config
    file selected.
    """

    # this allows us to access __annotations__ from
    # the instance rather than the class itself
    cls = type(robot_cls)

    #
    # HACK: to allow `get_type_hints` to work
    #       with pybind11_bultins.
    #
    class FakeModule:
        pass

    import sys

    sys.modules["pybind11_builtins"] = FakeModule()

    annotations = typing.get_type_hints(cls)
    bad_components = []

    for cname, c in annotations.items():
        compat_robots = getattr(c, "robot", None)
        if not compat_robots:

            #
            # XXX: Should this be a warning and enable the
            #      component by default?
            #
            #      Or, we could seperate robot components into their
            #      own directories (i.e. components\doof\component.py)
            #      and use inspect.getsourcefile(c) to check if the
            #      component belongs to a specific robot (then no need
            #      for a `self.robot_name` attribute at all).
            #

            raise AttributeError(
                f"Component {cname} ({c}) is missing a 'robot'"
                " attribute; component cannot be created."
            )
        if key in compat_robots or "all" in compat_robots:
            continue
        else:
            bad_components.append(cname)

    for bad_comp in bad_components:
        robot_cls.logger.info(f"Removing component {bad_comp!r}")
        del annotations[bad_comp]
