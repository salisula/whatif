# simulator.py

def calculate_profit(price, cost, sales, fixed):
    return (price - cost) * sales - fixed

def find_strategies(price, cost, sales, fixed, goal, max_price_inc, max_cost_cut, max_sales_inc):
    current_profit = calculate_profit(price, cost, sales, fixed)
    strategies = []
    steps = 5
    
    for p_inc in range(0, max_price_inc + 1, steps):
        for c_cut in range(0, max_cost_cut + 1, steps):
            for s_inc in range(0, max_sales_inc + 1, steps):
                
                if p_inc == 0 and c_cut == 0 and s_inc == 0:
                    continue
                
                new_price = price * (1 + p_inc / 100)
                new_cost = cost * (1 - c_cut / 100)
                new_sales = sales * (1 + s_inc / 100)
                
                new_profit = calculate_profit(new_price, new_cost, new_sales, fixed)
                
                if new_profit >= goal:
                    # Calculate Risk Score (lower is safer)
                    # Price increases are riskiest (1.5x), sales increases medium (1.2x), cost cuts safest (1.0x)
                    risk_score = (p_inc * 1.5) + (s_inc * 1.2) + (c_cut * 1.0)
                    
                    strategies.append({
                        "Price Increase": f"+{p_inc}%",
                        "Cost Cut": f"-{c_cut}%",
                        "Sales Increase": f"+{s_inc}%",
                        "New Price": f"${new_price:.2f}",
                        "New Cost": f"${new_cost:.2f}",
                        "Projected Profit": round(new_profit, 2),
                        "Risk Score": round(risk_score, 1)
                    })
    
    # Sort by lowest risk score first, then highest profit
    strategies.sort(key=lambda x: (x["Risk Score"], -x["Projected Profit"]))
    
    # Return the top 5 safest/most profitable strategies
    return strategies[:5]