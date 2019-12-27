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
from abc import abstractmethod

from octobot_services.abstract_service_user import AbstractServiceUser


class AbstractInterface(AbstractServiceUser):
    # The service required to run this interface
    REQUIRED_SERVICE = None

    # References that will be shared by interfaces
    bot = None
    project_name = None
    project_version = None
    enabled = True

    @staticmethod
    def initialize_global_project_data(bot, project_name, project_version):
        AbstractInterface.bot = bot
        AbstractInterface.project_name = project_name
        AbstractInterface.project_version = project_version

    @staticmethod
    def get_exchange_managers():
        return AbstractInterface.bot.exchange_factory.exchange_manager_list

    @staticmethod
    def is_bot_ready():
        return AbstractInterface.bot.initialized

    @abstractmethod
    def start(self):
        raise NotImplementedError(f"start is not implemented for {self.get_name()}")

    @abstractmethod
    def stop(self):
        raise NotImplementedError(f"stop is not implemented for {self.get_name()}")
