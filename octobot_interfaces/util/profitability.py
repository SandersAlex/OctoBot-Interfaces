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
from octobot_interfaces.util.util import get_exchange_managers, run_in_bot_main_loop
from octobot_trading.api.profitability import get_profitability_stats, get_origin_portfolio_value
from octobot_trading.api.trader import is_trader_enabled, is_trader_simulated


def get_global_profitability():
    simulated_global_profitability = 0
    real_global_profitability = 0
    simulated_no_trade_profitability = 0
    real_no_trade_profitability = 0
    simulated_full_origin_value = 0
    real_full_origin_value = 0
    market_average_profitability = None
    has_real_trader = False
    has_simulated_trader = False

    for exchange_manager in get_exchange_managers():
        if is_trader_enabled(exchange_manager):

            current_value, _, _, market_average_profitability, initial_portfolio_current_profitability = \
                get_profitability_stats(exchange_manager)

            if is_trader_simulated(exchange_manager):
                simulated_full_origin_value += get_origin_portfolio_value(exchange_manager)
                simulated_global_profitability += current_value
                simulated_no_trade_profitability += initial_portfolio_current_profitability
                has_simulated_trader = True
            else:
                real_full_origin_value += get_origin_portfolio_value(exchange_manager)
                real_global_profitability += current_value
                real_no_trade_profitability += initial_portfolio_current_profitability
                has_real_trader = True

    simulated_percent_profitability = simulated_global_profitability * 100 / simulated_full_origin_value \
        if simulated_full_origin_value > 0 else 0
    real_percent_profitability = real_global_profitability * 100 / real_full_origin_value \
        if real_full_origin_value > 0 else 0

    return has_real_trader, has_simulated_trader, \
        real_global_profitability, simulated_global_profitability, \
        real_percent_profitability, simulated_percent_profitability, \
        real_no_trade_profitability, simulated_no_trade_profitability, \
        market_average_profitability