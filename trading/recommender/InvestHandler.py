"""
Trading Strategy using Fundamental Data
Adjusted Graham Fundamentals trading algorithm (based on https://www.quantopian.com/help#fundamental-data)
1. Filter the top 50 companies by market cap
2. Exclude companies based on ESC criteria
3. Find the top two sectors that have the highest average PE ratio
4. Every week exit all the positions before entering new ones
5. Log the positions that we need
"""
from zipline.api import (
    attach_pipeline,
    pipeline_output,
    order_target_percent,
    record,
    schedule_function,
    date_rules,
    time_rules,
    )
from zipline.pipeline import Pipeline
from contract.ContractHandler import ContractHandler


def initialize(context):
    # Ethereum contract
    context.contract = ContractHandler()
    # Dictionary of stocks and their respective weights
    context.stock_weights = {}
    # Count of days before rebalancing
    context.days = 0
    # Number of sectors to go long in
    context.sect_numb = 2

    # TODO: Get section mappings from pipeline and exclude unwanted industries/companies
    # Sector mappings
    context.sector_mappings = {
       101.0: "Basic Materials",
       102.0: "Consumer Cyclical",
       103.0: "Financial Services",
       104.0: "Real Estate",
       205.0: "Consumer Defensive",
       206.0: "Healthcare",
       207.0: "Utilites",
       308.0: "Communication Services",
       309.0: "Energy",
       310.0: "Industrials",
       311.0: "Technology"
    }

    # Rebalance weekly on the first day of the week at market open
    schedule_function(rebalance,
                      date_rule=date_rules.week_start(),
                      time_rule=time_rules.market_open())

    schedule_function(record_positions,
                      date_rule=date_rules.week_start(),
                      time_rule=time_rules.market_close())

    # Register pipeline
    fundamental_df = make_pipeline()
    attach_pipeline(fundamental_df, 'fundamentals')


#  Create a fundamentals data pipeline
def make_pipeline():
     #fundamental_df = get_fundamentals(
    #    query(
    #        # put your query in here by typing "fundamentals."
    #        fundamentals.valuation_ratios.pe_ratio,
    #        fundamentals.asset_classification.morningstar_sector_code
    #    )
    #    .filter(fundamentals.valuation.market_cap != None)
    #    .filter(fundamentals.valuation.shares_outstanding != None)
    #    .order_by(fundamentals.valuation.market_cap.desc())
    #    .limit(num_stocks)
    #)

    # Find sectors with the highest average PE
    #sector_pe_dict = {}
    #for stock in fundamental_df:
    #    sector = fundamental_df[stock]['morningstar_sector_code']
    #    pe = fundamental_df[stock]['pe_ratio']

    #    # If it exists add our pe to the existing list.
    #    # Otherwise don't add it.
    #    if sector not in sector_pe_dict:
    #      sector_pe_dict[sector] = []

    #    sector_pe_dict[sector].append(pe)

    # Find average PE per sector
    #sector_pe_dict = dict([
    #    (sectors, np.average(sector_pe_dict[sectors]))
    #    for sectors in sector_pe_dict
    #    if len(sector_pe_dict[sectors]) > 0
    #])

    # Sort in ascending order
    #sectors = sorted(
    #              sector_pe_dict,
    #              key=lambda x: sector_pe_dict[x],
    #              reverse=True
    #          )[:context.sect_numb]

    # Filter out only stocks with that particular sector
    # context.stocks = [
    #    stock for stock in fundamental_df
    #    if fundamental_df[stock]['morningstar_sector_code'] in sectors
    # ]

    # Initialize a context.sectors variable
    # context.sectors = [context.sector_mappings[sect] for sect in sectors]

    # Update context.fundamental_df with the securities (and pe_ratio)
    # that we need
    # context.fundamental_df = fundamental_df[context.stocks]

    # pe_ratio = close price / earnings per share
    pe_ratio = 3
    # mapping of companies to industry sectors
    sector_code = 3
    # market_cap = price * total shares outstanding (at e.g. closing)
    market_cap = 3
    # total shares outstanding reported by the company
    shares_outstanding = 3

    fundamentals = Pipeline(
        columns={
            'sector_code': sector_code,
            'pe_ratio': pe_ratio,
            'market_cap': market_cap,
            'shares_outstanding': shares_outstanding,
        },
        screen={
            market_cap is not None,
            shares_outstanding is not None,
        }
    )
    return fundamentals


"""
Called before the start of each trading day.  Runs the
fundamentals query and saves the matching securities into
context.fundamentals_df.
"""


def before_trading_start(context, data):
    # May need to increase the number of stocks
    num_stocks = 50
    context.fundamental_df = pipeline_output('fundamentals')
    # get current balance to determine capital_base
    context.capital_base = context.contract.getBalance()


def create_weights(stocks):
    # Takes in a list of securities and weights them all equally
    if len(stocks) == 0:
        return 0
    else:
        weight = 1.0 / len(stocks)
        return weight


# TODO: This needs to go to TradeHandler in the future
def rebalance(context, data):
    # Exit all positions before starting new ones
    for stock in context.portfolio.positions:
        if stock not in context.fundamental_df and data.can_trade(stock):
            order_target_percent(stock, 0)

    # Create weights for each stock
    weight = create_weights(context.stocks)

    # Rebalance all stocks to target weights
    for stock in context.fundamental_df:
        if data.can_trade(stock):
            if weight != 0:
                code = context.sector_mappings[
                     context.fundamental_df[stock]['sector_code']
                ]

            order_target_percent(stock, weight)


def record_positions(context, data):
    # track how many positions we're holding
    record(num_positions=len(context.portfolio.positions))

