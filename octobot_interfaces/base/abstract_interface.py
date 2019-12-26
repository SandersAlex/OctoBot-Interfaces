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

from octobot_commons.logging.logging_util import get_logger
from octobot_services.api.services import get_available_services
from octobot_services.services.service_factory import ServiceFactory


class AbstractInterface:

    # the service required to run this interface
    REQUIRED_SERVICE = None

    # references that will be shared by interfaces
    bot = None
    project_name = None
    project_version = None
    enabled = True

    def __init__(self, config):
        self.config = config
        self.paused = False

    async def initialize(self, backtesting_enabled):
        # init associated service if not already init
        service_list = get_available_services()
        if self.REQUIRED_SERVICE:
            if self.REQUIRED_SERVICE in service_list:
                service_factory = ServiceFactory(self.config)
                if await service_factory.create_or_get_service(self.REQUIRED_SERVICE, backtesting_enabled):
                    await self._post_initialize()
                else:
                    self.get_logger().error(f"Impossible to start {self.__class__.__name__}: required service "
                                            f"is not available.")
            else:
                self.get_logger().error(f"Required service {self.REQUIRED_SERVICE} is not an available service")
        elif self.REQUIRED_SERVICE is None:
            self.get_logger().error(f"Required service is not set, set it at False if no service is required")

    # implement _post_initialize if anything specific has to be done after initialize and before start
    async def _post_initialize(self):
        pass

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

    @classmethod
    def get_logger(cls):
        return get_logger(cls.__name__)

    @abstractmethod
    def start(self):
        raise NotImplementedError("start is not implemented")

    @abstractmethod
    def stop(self):
        raise NotImplementedError("stop is not implemented")
