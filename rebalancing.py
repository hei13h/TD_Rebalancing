#import numpy as np
#import pandas as pd
from numpy import random
import json

class Positions :

    def __init__ (self , positions: dict[str, float]): 
        self.pos = positions
    def get_universe(self) -> list[str]: 
        return list(self. pos.keys())


## class object similar to positions for consistency
class Weights :

    def __init__ (self , weights: dict[str, float]): 
        self.wgts = weights
    def get_universe(self) -> list[str]: 
        return list(self.wgts.keys())

class Broker :
    def __init__(self, initial_positions: Positions, initial_aum: float): 
        self.positions : Positions = initial_positions
        self.aum: float = initial_aum
    def get_live_price(self) -> dict[str, float]:
        prices = {asset: random.uniform(10, 30) for asset in 
                  self.positions.get_universe()}
        return prices
    def get_positions ( self ) -> Positions :
        return self.positions
    def execute_trades(self , execution_positions: Positions) -> None:
        pass 


class RebalancingSystem: 
    def __init__(self): 
        pass

    def rebalance(self, broker: Broker, weights: Weights):
        
        assert broker is not None #no broker - no positions etc
        
        current_pos=broker.get_positions()
        #either new portfolio, either liquidating old portfolio
        assert (current_pos is not None or weights.wgts is not None) 
        
        #form a combined position book with current and prospective positions
        if current_pos and not(all(k==0 for k in current_pos.pos.items())): 
            new_portfolio = False
        else:
            new_portfolio = True

        reb_universe=weights.get_universe()
        combined_positions= {}

        if not new_portfolio: 
            combined_positions = current_pos.pos
        for r in reb_universe: 
            combined_positions.setdefault(r,0)

        #if new portfo = use AUM supplied, otherwise recalculate
        if new_portfolio:
            current_aum = broker.aum
        
        broker.positions = Positions(combined_positions)
        pos_prices = broker.get_live_price()

        if not new_portfolio: 
            current_aum = sum([pos_prices[i] * combined_positions[i] for \
                                i in combined_positions.keys()])
        
        print(f'initial pos: {combined_positions}')
        print(f'Price: {pos_prices}')
        print(f'AUM: {current_aum}')

        #calculated intended exposure = wgt intended * aum, hence derive intended positions
        intended_positions = {}
        wgts = weights.wgts
        for w in wgts.keys():
            intended_positions[w] = wgts[w] * current_aum / pos_prices[w]
        if current_pos: 
            for c in current_pos.pos.keys(): 
                intended_positions.setdefault(c,0)
        
        print(f'intended pos:{intended_positions}')

        #if new portfolio - need buy all positions. otherwise reduce current holding
        if current_pos:
            trades = {}
            for p in intended_positions:
                trades[p] = intended_positions[p] - combined_positions[p]
        else: 
            trades = intended_positions
        
        for t in list(trades):
            if trades[t]==0: trades.pop(t)
        print(f'trades: {trades}')
        return trades
    
if __name__ == "__main__":
    with open('targetWeights.json', encoding='utf-8') as f:
        w_dict = json.load(f)
    # 3 test cases - No initial positions, blank position object, some positions (with untraded items)
    #positions = Positions({'AAPL':100,'IBM':0,'MSFT':100})
    #positions = Positions({})
    positions = None
    broker = Broker(positions, 10000)
    wgts = Weights(w_dict)
    rebal = RebalancingSystem()
    trades = rebal.rebalance(broker,wgts)
    with open('executedTrades.json','w', encoding='utf-8') as f:
        json.dump(trades,f)
    broker.execute_trades(trades)