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


def get_exchange_managers(bot=None):
    if bot is None:
        return AbstractInterface.get_exchange_managers()
    else:
        return bot.exchange_factory.exchange_manager_list


def run_in_bot_main_loop(coroutine):
    return AbstractInterface.bot.run_in_main_asyncio_loop(coroutine)
