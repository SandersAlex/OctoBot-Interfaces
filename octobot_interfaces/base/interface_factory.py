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

from octobot_commons.logging.logging_util import get_logger
from octobot_commons.tentacles_management import get_all_classes_from_parent
from octobot_interfaces.base.abstract_interface import AbstractInterface


class InterfaceFactory:
    def __init__(self, config):
        self.logger = get_logger(self.__class__.__name__)
        self.config = config

    @staticmethod
    def get_available_interfaces():
        return get_all_classes_from_parent(AbstractInterface)

    async def create_interface(self, interface_class):
        return interface_class(self.config)
