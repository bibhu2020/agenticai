import math
from typing import List, Dict, Any

def calculate_strategy_metrics(legs: List[Dict[str, Any]], spot_price: float) -> Dict[str, Any]:
    """
    Calculates Max Profit, Max Loss, and Breakeven for a given set of option legs.
    Leg format: {'action': 'BUY'/'SELL', 'type': 'CALL'/'PUT', 'strike': float, 'price': float, 'expiry': str}
    """
    if not legs:
        return {"max_profit": 0, "max_loss": 0, "breakeven": 0, "net_cost": 0}

    # 1. Calculate Net Debit/Credit
    net_premium = 0
    for leg in legs:
        multiplier = 1 if leg['action'].upper() == 'BUY' else -1
        net_premium += leg['price'] * multiplier
    
    # Positive net_premium = Debit (Paying)
    # Negative net_premium = Credit (Receiving)
    is_debit = net_premium > 0
    net_cost = abs(net_premium) * 100 # Multiplied by contract size
    
    # 2. Identify Strategy Type and Calculate Risk
    leg_count = len(legs)
    expiries = set(leg['expiry'] for leg in legs)
    is_multi_expiry = len(expiries) > 1
    
    # Sort legs by strike for easier analysis
    sorted_legs = sorted(legs, key=lambda x: x['strike'])
    
    max_profit = 0
    max_loss = 0
    
    if is_multi_expiry:
        # Complex calculation for Calendars/Diagonals
        # For simplicity in this version, we provide an ESTIMATE based on premium paid
        # Usually Max Loss = Net Debit Paid
        if is_debit:
            max_loss = net_cost
            # Max profit is capped by the back-month value at front-month expiration
            # This is hard to calculate without a model, so we flag it as an estimate
            max_profit = "Estimated (Limited)" 
        else:
            # Net Credit Calendar (Rare/Risky)
            max_loss = "Unlimited"
            max_profit = net_cost
            
    elif leg_count == 1:
        # Long/Short Call/Put
        if legs[0]['action'].upper() == 'BUY':
            max_loss = net_cost
            max_profit = "Unlimited"
        else:
            max_profit = net_cost
            max_loss = "Unlimited"
            
    elif leg_count == 2:
        # Spreads (Vertical)
        s1, s2 = sorted_legs[0]['strike'], sorted_legs[1]['strike']
        spread_width = (s2 - s1) * 100
        
        if is_debit:
            max_loss = net_cost
            max_profit = spread_width - net_cost
        else:
            max_profit = net_cost
            max_loss = spread_width - net_cost
            
    elif leg_count == 4:
        # Iron Condor / Iron Butterfly
        # Max Profit = Net Credit
        # Max Loss = Width of widest wing - Net Credit
        if not is_debit:
            put_spread_width = (sorted_legs[1]['strike'] - sorted_legs[0]['strike']) * 100
            call_spread_width = (sorted_legs[3]['strike'] - sorted_legs[2]['strike']) * 100
            widest_wing = max(put_spread_width, call_spread_width)
            max_profit = net_cost
            max_loss = widest_wing - net_cost
        else:
            # Reverse Iron Condor (Debit)
            max_loss = net_cost
            max_profit = max(sorted_legs[1]['strike'] - sorted_legs[0]['strike'], sorted_legs[3]['strike'] - sorted_legs[2]['strike']) * 100 - net_cost

    elif leg_count == 3:
        # Butterfly / Christmas Tree
        # S1 (Buy 1), S2 (Sell 2), S3 (Buy 1)
        if is_debit:
            wing_width = (sorted_legs[1]['strike'] - sorted_legs[0]['strike']) * 100
            max_loss = net_cost
            max_profit = wing_width - net_cost

    return {
        "max_profit": max_profit,
        "max_loss": max_loss,
        "net_premium": round(net_premium, 2),
        "is_debit": is_debit,
        "leg_details": [f"{l['action']} {l['type']} {l['strike']} @ {l['price']} (Exp: {l['expiry']})" for l in legs]
    }
