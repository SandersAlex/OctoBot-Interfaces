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
from octobot_interfaces.util.util import run_in_bot_main_loop, get_exchange_managers
from octobot_trading.api.exchange import get_trading_pairs, get_exchange_name, force_refresh_orders_and_portfolio
from octobot_trading.api.trader import is_trader_simulated, get_trader_risk, is_trader_enabled, set_trader_risk, \
    is_trader_enabled_in_config, set_trading_enabled, \
    sell_all_everything_for_reference_market, sell_currency_for_reference_market
from octobot_trading.api.trades import get_trade_history, get_total_paid_trading_fees


def has_real_and_or_simulated_traders():
    has_real_trader = False
    has_simulated_trader = False
    exchange_managers = get_exchange_managers()
    for exchange_manager in exchange_managers:
        if is_trader_simulated(exchange_manager):
            has_simulated_trader = True
        else:
            has_real_trader = True
    return has_real_trader, has_simulated_trader


def force_real_traders_refresh():
    at_least_one = False
    for exchange_manager in get_exchange_managers():
        if is_trader_enabled(exchange_manager):
            at_least_one = True
            run_in_bot_main_loop(force_refresh_orders_and_portfolio(exchange_manager))

    if not at_least_one:
        raise RuntimeError("no real trader to update.")


def sell_all_currencies():
    orders = []
    for exchange_manager in get_exchange_managers():
        if is_trader_enabled(exchange_manager):
            orders += run_in_bot_main_loop(sell_all_everything_for_reference_market(exchange_manager))
    return orders


def sell_all(currency):
    orders = []
    for exchange_manager in get_exchange_managers():
        if is_trader_enabled(exchange_manager):
            orders += run_in_bot_main_loop(sell_currency_for_reference_market(exchange_manager, currency))
    return orders


def set_enable_trading(enable):
    for exchange_manager in get_exchange_managers():
        if is_trader_enabled_in_config(exchange_manager):
            set_trading_enabled(exchange_manager, enable)


def _merge_trader_fees(current_fees, exchange_manager):
    current_fees_dict = current_fees if current_fees else {}
    for key, val in get_total_paid_trading_fees(exchange_manager).items():
        if key in current_fees_dict:
            current_fees_dict[key] += val
        else:
            current_fees_dict[key] = val
    return current_fees_dict


def get_total_paid_fees(bot=None):
    real_trader_fees = None
    simulated_trader_fees = None

    for exchange_manager in get_exchange_managers(bot):
        if is_trader_enabled(exchange_manager):
            if is_trader_simulated(exchange_manager):
                simulated_trader_fees = _merge_trader_fees(simulated_trader_fees, exchange_manager)
            else:
                real_trader_fees = _merge_trader_fees(real_trader_fees, exchange_manager)

    return real_trader_fees, simulated_trader_fees


def get_trades_history(bot=None, symbol=None):
    simulated_trades_history = []
    real_trades_history = []

    for exchange_manager in get_exchange_managers(bot):
        if is_trader_enabled(exchange_manager):
            if is_trader_simulated(exchange_manager):
                simulated_trades_history += get_trade_history(exchange_manager, symbol)
            else:
                real_trades_history += get_trade_history(exchange_manager, symbol)

    return real_trades_history, simulated_trades_history


def set_risk(risk):
    result_risk = None
    for exchange_manager in get_exchange_managers():
        result_risk = set_trader_risk(exchange_manager, risk)
    return result_risk


def get_risk():
    return get_trader_risk(next(iter(get_exchange_managers())))


def get_currencies_with_status():
    evaluations_by_exchange_by_pair = {}
    for exchange_manager in get_exchange_managers():
        for pair in get_trading_pairs(exchange_manager):
            if pair not in evaluations_by_exchange_by_pair:
                evaluations_by_exchange_by_pair[pair] = {}
            # TODO: replace with real status explanation and details, related to matrix API
            status_explanation = "N/A"
            status_detail = "N/A"
            evaluations_by_exchange_by_pair[pair][get_exchange_name(exchange_manager)] = \
                [status_explanation, status_detail]
    return evaluations_by_exchange_by_pair


def get_matrix_list():
    # TODO: add matrix API
    return {}
    # return {
    #     symbol_evaluator.get_symbol():
    #         {
    #             exchange.get_name(): symbol_evaluator.get_matrix(exchange)
    #             for exchange in get_bot().get_exchanges_list().values()
    #             if symbol_evaluator.has_exchange(exchange)
    #         }
    #     for symbol_evaluator in get_bot().get_symbol_evaluator_list().values()}
