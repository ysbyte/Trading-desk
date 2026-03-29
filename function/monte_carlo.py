import numpy as np

def monte_carlo_price(S, K, T, r, sigma, option_type="call", N=100000):
    np.random.seed(42)
    Z = np.random.standard_normal(N)
    ST = S * np.exp((r - 0.5*sigma**2)*T + sigma*np.sqrt(T)*Z)
    
    if option_type=="call":
        payoff = np.maximum(ST - K, 0)
    else:
        payoff = np.maximum(K - ST, 0)
    
    price = np.exp(-r*T) * np.mean(payoff)
    return price

def monte_carlo_price_asian(S,K,T,r,sigma,option_type="call",N=100000,M=50):
    np.random.seed(42)
    Z=np.random.standard_normal((N,M))
    dt=T/M
    S_chemin=np.zeros((N,M+1))
    S_chemin[:,0]=S
    for t in range(1,M+1):
        S_chemin[:,t]=S_chemin[:,t-1]*np.exp((r-0.5*sigma**2)*dt+sigma*np.sqrt(dt)*Z[:,t-1])
    Prix_moyen_S=np.mean(S_chemin[:,1:],axis=1)
    if option_type=="call":
        Payoff=np.maximum(Prix_moyen_S-K,0)
    else:
        Payoff=np.maximum(K-Prix_moyen_S,0)
    price=np.exp(-r*T)*np.mean(Payoff)
    return price

def monte_carlo_price_lookback(S,K,T,r,sigma,option_type="call",N=100000,M=100):
    np.random.seed(42)
    Z=np.random.standard_normal((N,M))
    dt=T/M
    S_chemin=np.zeros((N,M+1))
    S_chemin[:,0]=S
    for t in range(1,M+1):
        S_chemin[:,t]=S_chemin[:,t-1]*np.exp((r-0.5*sigma**2)*dt+sigma*np.sqrt(dt)*Z[:,t-1])
    Max_S=np.max(S_chemin[:,1:],axis=1)
    Min_S=np.min(S_chemin[:,1:],axis=1)
    if option_type=="call":
        Payoff=np.maximum(Max_S-K,0)
    else:
        Payoff=np.maximum(K-Min_S,0)
    price=np.exp(-r*T)*np.mean(Payoff)
    return price

def monte_carlo_price_barrier(S,K,T,B,r,sigma,option_type="call",barrier_type="knock-out",N=100000,M=100):
    np.random.seed(42)
    dt=T/M
    Z = np.random.standard_normal((N, M))
    increments = (r-0.5*sigma**2)*dt+sigma*np.sqrt(dt)*Z
    log_paths = np.cumsum(increments, axis=1)
    log_paths = np.hstack((np.zeros((N, 1)), log_paths))  # ajoute t=0
    S_paths = S * np.exp(log_paths)

    # Vérifie si la barrière a été touchée
    if B > S:
    # barrière au-dessus → "up"
        hit_barrier = np.any(S_paths >= B, axis=1)
    else:
    # barrière en-dessous → "down"
        hit_barrier = np.any(S_paths <= B, axis=1)


# Payoff terminal
    S_T = S_paths[:, -1]
    if option_type == "call":
        payoff = np.maximum(S_T - K, 0)
    else:
        payoff = np.maximum(K - S_T, 0)

# Gestion Knock-In / Knock-Out
    if barrier_type == "knock-out":
        payoff = np.where(hit_barrier, 0, payoff)  # 0 si barrière touchée
    elif barrier_type == "knock-in":
        payoff = np.where(hit_barrier, payoff, 0)  # 0 si jamais touchée

    price = np.exp(-r * T) * np.mean(payoff)
    return price





    
    
    
    