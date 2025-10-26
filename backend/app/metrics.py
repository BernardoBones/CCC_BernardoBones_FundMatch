from typing import List
from statistics import mean, pstdev

def calculate_returns(prices: List[float]) -> List[float]:
    """
    Calcula os retornos simples de uma série de preços.

    Fórmula: (P_t / P_{t-1}) - 1

    Args:
        prices (List[float]): Lista de preços históricos.

    Returns:
        List[float]: Lista de retornos entre cada par de dias consecutivos.
    """
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
    """
    Calcula a volatilidade dos retornos como o desvio padrão populacional.

    Args:
        returns (List[float]): Lista de retornos diários.

    Returns:
        float: Volatilidade dos retornos. Retorna 0.0 se não houver dados suficientes.
    """
    if not returns or len(returns) < 2:
        return 0.0
    return pstdev(returns)

def calculate_sharpe(returns: List[float], risk_free: float = 0.0) -> float:
    """
    Calcula o índice de Sharpe da série de retornos.

    Fórmula: (média dos retornos - taxa livre de risco) / volatilidade

    Args:
        returns (List[float]): Lista de retornos diários.
        risk_free (float): Taxa livre de risco (default: 0.0).

    Returns:
        float: Índice de Sharpe. Retorna 0.0 se a volatilidade for zero ou não houver dados.
    """
    if not returns:
        return 0.0
    avg = mean(returns)
    vol = calculate_volatility(returns)
    if vol == 0:
        return 0.0
    return (avg - risk_free) / vol

def total_return(prices: List[float]) -> float:
    """
    Calcula o retorno total entre o primeiro e o último preço da série.

    Fórmula: (P_final / P_inicial) - 1

    Args:
        prices (List[float]): Lista de preços históricos.

    Returns:
        float: Retorno total da série. Retorna 0.0 se não houver dados suficientes ou se o preço inicial for zero.
    """
    if not prices or len(prices) < 2:
        return 0.0
    first = prices[0]
    last = prices[-1]
    if first == 0:
        return 0.0
    return (last / first) - 1.0
