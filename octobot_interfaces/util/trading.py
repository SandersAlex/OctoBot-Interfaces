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
from octobot_commons.constants import PORTFOLIO_AVAILABLE, PORTFOLIO_TOTAL
from octobot_interfaces.base.abstract_interface import AbstractInterface
from octobot_trading.api.exchange import get_trading_pairs, get_exchange_name, force_refresh_orders_and_portfolio
from octobot_trading.api.portfolio import get_portfolio
from octobot_trading.api.profitability import get_profitability_stats, get_origin_portfolio_value, \
    get_current_portfolio_value, get_current_holdings_values
from octobot_trading.api.orders import cancel_all_open_orders_with_currency, get_open_orders, \
    cancel_order_from_description
from octobot_trading.api.trader import is_trader_simulated, get_trader_risk, is_trader_enabled, set_trader_risk, \
    is_trader_enabled_in_config, set_trading_enabled, \
    sell_all_everything_for_reference_market, sell_currency_for_reference_market
from octobot_trading.api.trades import get_trade_history, get_total_paid_trading_fees


def _get_exchange_managers(bot=None):
    if bot is None:
        return AbstractInterface.get_exchange_managers()
    else:
        return bot.exchange_factory.exchange_manager_list


def _run_in_bot_main_loop(coroutine):
    return AbstractInterface.bot.run_in_main_asyncio_loop(coroutine)


def _merge_portfolio_values(portfolio1, portfolio2):
    for key, value in portfolio2.items():
        if key in portfolio1:
            portfolio1[key] += portfolio2[key]
        else:
            portfolio1[key] = portfolio2[key]
    return portfolio1


def get_portfolio_holdings():
    real_currency_portfolio = {}
    simulated_currency_portfolio = {}

    for exchange_manager in _get_exchange_managers():
        if is_trader_enabled(exchange_manager):

            trader_currencies_values = _run_in_bot_main_loop(get_current_holdings_values(exchange_manager))
            if is_trader_simulated(exchange_manager):
                _merge_portfolio_values(simulated_currency_portfolio, trader_currencies_values)
            else:
                _merge_portfolio_values(real_currency_portfolio, trader_currencies_values)

    return real_currency_portfolio, simulated_currency_portfolio


def get_portfolio_current_value():
    simulated_value = 0
    real_value = 0
    has_real_trader = False
    has_simulated_trader = False

    for exchange_manager in _get_exchange_managers():
        if is_trader_enabled(exchange_manager):

            current_value = get_current_portfolio_value(exchange_manager)

            # current_value might be 0 if no trades have been made / canceled => use origin value
            if current_value == 0:
                current_value = get_origin_portfolio_value(exchange_manager)

            if is_trader_simulated(exchange_manager):
                simulated_value += current_value
                has_simulated_trader = True
            else:
                real_value += current_value
                has_real_trader = True

    return has_real_trader, has_simulated_trader, real_value, simulated_value


def has_real_and_or_simulated_traders():
    has_real_trader = False
    has_simulated_trader = False
    exchange_managers = _get_exchange_managers()
    for exchange_manager in exchange_managers:
        if is_trader_simulated(exchange_manager):
            has_simulated_trader = True
        else:
            has_real_trader = True
    return has_real_trader, has_simulated_trader


def force_real_traders_refresh():
    at_least_one = False
    for exchange_manager in _get_exchange_managers():
        if is_trader_enabled(exchange_manager):
            at_least_one = True
            _run_in_bot_main_loop(force_refresh_orders_and_portfolio(exchange_manager))

    if not at_least_one:
        raise RuntimeError("no real trader to update.")


def get_all_open_orders():
    simulated_open_orders = []
    real_open_orders = []

    for exchange_manager in _get_exchange_managers():
        if is_trader_enabled(exchange_manager):
            if is_trader_simulated(exchange_manager):
                simulated_open_orders += get_open_orders(exchange_manager)
            else:
                real_open_orders += get_open_orders(exchange_manager)

    return real_open_orders, simulated_open_orders


def cancel_orders(orders_desc):
    removed_count = 0
    if orders_desc:
        for exchange_manager in _get_exchange_managers():
            if is_trader_enabled(exchange_manager):
                removed_count += _run_in_bot_main_loop(cancel_order_from_description(exchange_manager, orders_desc))
    return removed_count


def cancel_all_open_orders(currency=None):
    for exchange_manager in _get_exchange_managers():
        if is_trader_enabled(exchange_manager):
            if currency is None:
                _run_in_bot_main_loop(cancel_all_open_orders(exchange_manager))
            else:
                _run_in_bot_main_loop(cancel_all_open_orders_with_currency(exchange_manager, currency))


def sell_all_currencies():
    orders = []
    for exchange_manager in _get_exchange_managers():
        if is_trader_enabled(exchange_manager):
            orders += _run_in_bot_main_loop(sell_all_everything_for_reference_market(exchange_manager))
    return orders


def sell_all(currency):
    orders = []
    for exchange_manager in _get_exchange_managers():
        if is_trader_enabled(exchange_manager):
            orders += _run_in_bot_main_loop(sell_currency_for_reference_market(exchange_manager, currency))
    return orders


def set_enable_trading(enable):
    for exchange_manager in _get_exchange_managers():
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

    for exchange_manager in _get_exchange_managers(bot):
        if is_trader_enabled(exchange_manager):
            if is_trader_simulated(exchange_manager):
                simulated_trader_fees = _merge_trader_fees(simulated_trader_fees, exchange_manager)
            else:
                real_trader_fees = _merge_trader_fees(real_trader_fees, exchange_manager)

    return real_trader_fees, simulated_trader_fees


def get_trades_history(bot=None, symbol=None):
    simulated_trades_history = []
    real_trades_history = []

    for exchange_manager in _get_exchange_managers(bot):
        if is_trader_enabled(exchange_manager):
            if is_trader_simulated(exchange_manager):
                simulated_trades_history += get_trade_history(exchange_manager, symbol)
            else:
                real_trades_history += get_trade_history(exchange_manager, symbol)

    return real_trades_history, simulated_trades_history


def set_risk(risk):
    result_risk = None
    for exchange_manager in _get_exchange_managers():
        result_risk = set_trader_risk(exchange_manager, risk)
    return result_risk


def get_risk():
    return get_trader_risk(next(iter(_get_exchange_managers())))


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

    for exchange_manager in _get_exchange_managers():
        if is_trader_enabled(exchange_manager):

            current_value, _, _, market_average_profitability, initial_portfolio_current_profitability = \
                _run_in_bot_main_loop(get_profitability_stats(exchange_manager))

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


def get_currencies_with_status():
    evaluations_by_exchange_by_pair = {}
    for exchange_manager in _get_exchange_managers():
        for pair in get_trading_pairs(exchange_manager):
            if pair not in evaluations_by_exchange_by_pair:
                evaluations_by_exchange_by_pair[pair] = {}
            # TODO: replace with real status explanation and details, related to matrix API
            status_explanation = "N/A"
            status_detail = "N/A"
            evaluations_by_exchange_by_pair[pair][get_exchange_name(exchange_manager)] = \
                [status_explanation, status_detail]
    return evaluations_by_exchange_by_pair


def _get_portfolios():
    simulated_portfolios = []
    real_portfolios = []

    for exchange_manager in _get_exchange_managers():
        if is_trader_enabled(exchange_manager):
            if is_trader_simulated(exchange_manager):
                simulated_portfolios.append(get_portfolio(exchange_manager))
            else:
                real_portfolios.append(get_portfolio(exchange_manager))

    return real_portfolios, simulated_portfolios


def _merge_portfolios(base_portfolio, to_merge_portfolio):
    for currency, amounts in to_merge_portfolio.items():
        if currency not in base_portfolio:
            base_portfolio[currency] = {
                PORTFOLIO_AVAILABLE: 0,
                PORTFOLIO_TOTAL: 0
            }

        base_portfolio[currency][PORTFOLIO_TOTAL] += amounts[PORTFOLIO_TOTAL]
        base_portfolio[currency][PORTFOLIO_TOTAL] = amounts[PORTFOLIO_TOTAL]


def get_global_portfolio_currencies_amounts():
    real_portfolios, simulated_portfolios = _get_portfolios()
    real_global_portfolio = {}
    simulated_global_portfolio = {}

    for portfolio in simulated_portfolios:
        _merge_portfolios(simulated_global_portfolio, portfolio)

    for portfolio in real_portfolios:
        _merge_portfolios(real_global_portfolio, portfolio)

    return real_global_portfolio, simulated_global_portfolio


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
