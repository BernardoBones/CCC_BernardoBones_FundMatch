from typing import List
from statistics import mean, pstdev

def calculate_returns(prices: List[float]) -> List[float]:
    """Retornos simples: (P_t / P_{t-1}) - 1."""
    if not prices or len(prices) < 2:
        return []
    returns = []
    for prev, cur in zip(prices[:-1], prices[1:]):
        # proteger divisão por zero
        if prev == 0:
            returns.append(0.0)
        else:
            returns.append((cur / prev) - 1.0)
    return returns

def calculate_volatility(returns: List[float]) -> float:
    """Volatilidade (desvio padrão amostral dos retornos)."""
    if not returns or len(returns) < 2:
        return 0.0
    return pstdev(returns)

def calculate_sharpe(returns: List[float], risk_free: float = 0.0) -> float:
    """Sharpe ratio: (avg return - risk_free) / volatility."""
    if not returns:
        return 0.0
    avg = mean(returns)
    vol = calculate_volatility(returns)
    if vol == 0:
        return 0.0
    return (avg - risk_free) / vol

def total_return(prices: List[float]) -> float:
    """Retorno total entre primeiro e último preço."""
    if not prices or len(prices) < 2:
        return 0.0
    first = prices[0]
    last = prices[-1]
    if first == 0:
        return 0.0
    return (last / first) - 1.0
