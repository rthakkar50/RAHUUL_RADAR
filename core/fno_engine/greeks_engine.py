"""
RAHUUL RADAR — F&O Engine: Greeks Engine (Task 8)
=================================================
Calculates Black-Scholes analytical option Greeks:
Delta, Gamma, Theta, Vega, and Rho.
"""

import math
from typing import Dict, Any
from core.fno_engine.fno_models import Greeks


def _norm_cdf(x: float) -> float:
    """Standard normal cumulative distribution function (CDF)."""
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0


def _norm_pdf(x: float) -> float:
    """Standard normal probability density function (PDF)."""
    return (1.0 / math.sqrt(2.0 * math.pi)) * math.exp(-0.5 * x * x)


class GreeksEngine:
    """
    Black-Scholes Option Greeks Calculation Engine.
    """

    def calculate_greeks(
        self,
        spot: float,
        strike: float,
        time_to_expiry_years: float,
        volatility: float,
        option_type: str = "CE",
        risk_free_rate: float = 0.07
    ) -> Greeks:
        """
        Calculates Delta, Gamma, Theta, Vega, and Rho for Call or Put options.
        """
        S = float(spot)
        K = float(strike)
        T = max(float(time_to_expiry_years), 0.0001)  # Prevent divide by zero
        v = max(float(volatility), 0.01)
        r = float(risk_free_rate)
        opt = option_type.upper()

        d1 = (math.log(S / K) + (r + 0.5 * v * v) * T) / (v * math.sqrt(T))
        d2 = d1 - v * math.sqrt(T)

        # Gamma (Same for Call & Put)
        gamma = round(_norm_pdf(d1) / (S * v * math.sqrt(T)), 6)
        # Vega (Same for Call & Put)
        vega = round(S * _norm_pdf(d1) * math.sqrt(T) / 100.0, 4)

        if opt in ("CE", "CALL"):
            delta = round(_norm_cdf(d1), 4)
            theta_annual = -(S * _norm_pdf(d1) * v) / (2.0 * math.sqrt(T)) - r * K * math.exp(-r * T) * _norm_cdf(d2)
            theta = round(theta_annual / 365.0, 4)
            rho = round(K * T * math.exp(-r * T) * _norm_cdf(d2) / 100.0, 4)
        else: # PE / PUT
            delta = round(_norm_cdf(d1) - 1.0, 4)
            theta_annual = -(S * _norm_pdf(d1) * v) / (2.0 * math.sqrt(T)) + r * K * math.exp(-r * T) * _norm_cdf(-d2)
            theta = round(theta_annual / 365.0, 4)
            rho = round(-K * T * math.exp(-r * T) * _norm_cdf(-d2) / 100.0, 4)

        return Greeks(
            delta=delta,
            gamma=gamma,
            theta=theta,
            vega=vega,
            rho=rho
        )
