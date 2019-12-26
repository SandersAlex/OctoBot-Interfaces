#  Drakkar-Software OctoBot-Interfaces
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
from octobot_interfaces.base.abstract_interface import AbstractInterface
from octobot_interfaces.base.interface_factory import InterfaceFactory
from octobot_interfaces.managers.interface_manager import InterfaceManager


def initialize_global_project_data(bot, project_name, project_version) -> None:
    AbstractInterface.initialize_global_project_data(bot, project_name, project_version)


def create_interface_factory(config) -> InterfaceFactory:
    return InterfaceFactory(config)


def is_enabled(interface_class) -> bool:
    return interface_class.enabled


def disable_interfaces(interface_identifier) -> int:
    disabled_interfaces = 0
    normalized_identifier = interface_identifier.lower()
    for interface_class in InterfaceFactory.get_available_interfaces():
        if normalized_identifier in interface_class.__name__.lower():
            interface_class.enabled = False
            disabled_interfaces += 1
    return disabled_interfaces


def start_interfaces(interfaces) -> None:
    InterfaceManager.start_interfaces(interfaces)


def stop_interfaces(interfaces) -> None:
    InterfaceManager.stop_interfaces(interfaces)
