import numpy as np
from scipy.stats import norm

def bs_price(S,K,T,r,sigma,option_type="call"):
    d1=(np.log(S/K)+(r+0.5*sigma**2)*T)/(sigma*np.sqrt(T))
    d2=d1-sigma*np.sqrt(T)
    
    if option_type=="call":
        price=S*norm.cdf(d1)-K*np.exp(-r*T)*norm.cdf(d2)
    elif option_type=="put":
        price=K*np.exp(-r*T)*norm.cdf(-d2)-S*norm.cdf(-d1)
    else:
        raise ValueError("option_type doit être 'call' ou 'put'")
    
    return price

def bs_greeks(S,K,T,r,sigma,option_type="call"):
    d1=(np.log(S/K)+(r+0.5*sigma**2)*T)/(sigma*np.sqrt(T))
    d2=d1-sigma*np.sqrt(T)
    
    delta=norm.cdf(d1) if option_type=="call" else norm.cdf(d1)-1
    gamma=norm.pdf(d1)/(S*sigma*np.sqrt(T))
    vega=S*norm.pdf(d1)*np.sqrt(T)
    theta=(-S*norm.pdf(d1)*sigma/(2*np.sqrt(T))-r*K*np.exp(-r*T)*norm.cdf(d2 if option_type=="call" else -d2))
    rho=K*T*np.exp(-r*T)*norm.cdf(d2 if option_type=="call" else -d2)
    
    return {"delta": f"{delta:.2f}", "gamma": f"{gamma:.2f}", "vega": f"{vega:.2f}", "theta": f"{theta:.2f}", "rho": f"{rho:.2f}"}
