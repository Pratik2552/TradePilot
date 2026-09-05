"""
TradePilot — Analytics Service

Computes the full AnalyticsSnapshot from raw repository data.
All heavy computation (Sharpe, Sortino, drawdowns, distributions) lives here.
Results are NOT stored — computed fresh each request.
Add an in-memory TTL cache here when needed.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, List, Optional

from app.core.exceptions import EngineNotReadyError, StrategyNotFoundError
from app.core.logging import get_logger
from app.domain.strategy_registry import get_strategy_registry
from app.infrastructure.repositories.base import BaseRepository
from app.schemas.analytics import (
    AnalyticsSnapshot,
    DrawdownPeriod,
    EquityPoint,
    HoldingDistributionBucket,
    MonthlyReturn,
    ReturnDistributionBucket,
    RollingMetricPoint,
)

logger = get_logger(__name__)


class AnalyticsService:
    def __init__(self, repository: BaseRepository) -> None:
        self._repo = repository
        self._registry = get_strategy_registry()

    def get_analytics(
        self, strategy_id: str, user_id: str = "default"
    ) -> AnalyticsSnapshot:
        if not self._registry.exists(strategy_id):
            raise StrategyNotFoundError(strategy_id)

        equity_raw = self._repo.load_equity_curve(strategy_id, user_id)
        trades_raw = self._repo.load_backtest_trades(strategy_id, user_id)

        if not equity_raw and not trades_raw:
            raise EngineNotReadyError(
                "No backtest data available. Run a backtest first."
            )

        try:
            import numpy as np
            import pandas as pd

            now = datetime.now(timezone.utc).isoformat()

            # ----------------------------------------------------------------
            # Prepare DataFrames
            # ----------------------------------------------------------------
            ec = pd.DataFrame(equity_raw) if equity_raw else pd.DataFrame()
            trades = pd.DataFrame(trades_raw) if trades_raw else pd.DataFrame()

            if not ec.empty:
                ec["Date"] = pd.to_datetime(ec["Date"])
                ec = ec.sort_values("Date").reset_index(drop=True)
                ec["Portfolio"] = ec["Portfolio"].astype(float)

            if not trades.empty:
                trades["Return %"] = pd.to_numeric(
                    trades.get("Return %", 0), errors="coerce"
                ).fillna(0)
                trades["Holding Days"] = pd.to_numeric(
                    trades.get("Holding Days", 0), errors="coerce"
                ).fillna(0)

            # ----------------------------------------------------------------
            # Core Metrics from Equity Curve
            # ----------------------------------------------------------------
            total_return = cagr = sharpe = sortino = max_dd = 0.0
            max_dd_duration = 0
            calmar = recovery_factor = volatility = 0.0

            if not ec.empty and len(ec) > 1:
                port = ec["Portfolio"]
                start_val = float(port.iloc[0])
                end_val = float(port.iloc[-1])
                start_date = ec["Date"].iloc[0]
                end_date = ec["Date"].iloc[-1]
                years = (end_date - start_date).days / 365.25

                total_return = ((end_val - start_val) / start_val * 100) if start_val > 0 else 0

                if years > 0 and start_val > 0:
                    cagr = ((end_val / start_val) ** (1 / years) - 1) * 100

                daily_r = port.pct_change().dropna()
                if len(daily_r) > 0:
                    mean_r = float(daily_r.mean())
                    std_r = float(daily_r.std())
                    volatility = std_r * math.sqrt(252) * 100

                    if std_r > 0:
                        sharpe = (mean_r / std_r) * math.sqrt(252)

                    downside = daily_r[daily_r < 0]
                    down_std = float(downside.std()) if len(downside) > 0 else 0
                    if down_std > 0:
                        sortino = (mean_r / down_std) * math.sqrt(252)

                running_max = port.cummax()
                dd_series = (port - running_max) / running_max * 100
                max_dd = float(dd_series.min())

                if cagr != 0 and max_dd != 0:
                    calmar = cagr / abs(max_dd)

                # Max drawdown duration (in trading days)
                in_dd = dd_series < 0
                max_dur = 0
                cur_dur = 0
                for v in in_dd:
                    if v:
                        cur_dur += 1
                        max_dur = max(max_dur, cur_dur)
                    else:
                        cur_dur = 0
                max_dd_duration = max_dur

                recovery_factor = total_return / abs(max_dd) if max_dd != 0 else 0

            # ----------------------------------------------------------------
            # Trade Metrics
            # ----------------------------------------------------------------
            total_trades = win_rate = avg_win = avg_loss = 0.0
            profit_factor = expectancy = avg_holding = 0.0

            if not trades.empty:
                returns = trades["Return %"].values
                wins = returns[returns > 0]
                losses = returns[returns <= 0]
                total_trades = len(trades)
                win_rate = len(wins) / total_trades * 100 if total_trades > 0 else 0
                avg_win = float(wins.mean()) if len(wins) > 0 else 0
                avg_loss = float(losses.mean()) if len(losses) > 0 else 0
                gross_profit = float(wins.sum())
                gross_loss = abs(float(losses.sum()))
                profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
                wr = win_rate / 100
                expectancy = (wr * avg_win) + ((1 - wr) * avg_loss)
                avg_holding = float(trades["Holding Days"].mean())

            # ----------------------------------------------------------------
            # Equity Curve Points
            # ----------------------------------------------------------------
            equity_points: List[EquityPoint] = []
            if not ec.empty:
                port = ec["Portfolio"]
                running_max = port.cummax()
                dd = (port - running_max) / running_max * 100

                for _, row in ec.iterrows():
                    equity_points.append(
                        EquityPoint(
                            date=str(row["Date"])[:10],
                            equity=round(float(row["Portfolio"]), 2),
                            drawdownPercent=round(
                                float(dd[row.name]), 2
                            ),
                        )
                    )

            # ----------------------------------------------------------------
            # Drawdown Periods
            # ----------------------------------------------------------------
            dd_periods: List[DrawdownPeriod] = []
            if not ec.empty and len(ec) > 1:
                port_vals = ec["Portfolio"].values
                dates_vals = ec["Date"].values
                running_max_vals = ec["Portfolio"].cummax().values
                in_dd_flag = False
                dd_start_idx = 0
                dd_peak_val = 0.0

                for i in range(len(port_vals)):
                    val = float(port_vals[i])
                    max_val = float(running_max_vals[i])
                    if val < max_val and not in_dd_flag:
                        in_dd_flag = True
                        dd_start_idx = max(0, i - 1)
                        dd_peak_val = max_val
                    elif val >= max_val and in_dd_flag:
                        in_dd_flag = False
                        trough = float(min(port_vals[dd_start_idx:i + 1]))
                        dd_pct = (trough - dd_peak_val) / dd_peak_val * 100 if dd_peak_val else 0
                        dd_periods.append(
                            DrawdownPeriod(
                                startDate=str(dates_vals[dd_start_idx])[:10],
                                endDate=str(dates_vals[i])[:10],
                                peakValue=round(dd_peak_val, 2),
                                troughValue=round(trough, 2),
                                drawdownPercent=round(dd_pct, 2),
                            )
                        )

            # ----------------------------------------------------------------
            # Monthly Returns
            # ----------------------------------------------------------------
            monthly_returns: List[MonthlyReturn] = []
            if not ec.empty and len(ec) > 1:
                monthly = (
                    ec.set_index("Date")["Portfolio"]
                    .resample("ME")
                    .last()
                    .pct_change()
                    .dropna()
                )
                for date, ret in monthly.items():
                    if not math.isnan(ret):
                        monthly_returns.append(
                            MonthlyReturn(
                                year=date.year,
                                month=date.month,
                                returnPercent=round(float(ret) * 100, 2),
                            )
                        )

            # ----------------------------------------------------------------
            # Rolling Metrics (252-day window)
            # ----------------------------------------------------------------
            rolling_metrics: List[RollingMetricPoint] = []
            if not ec.empty and len(ec) > 252:
                daily_r = ec.set_index("Date")["Portfolio"].pct_change().dropna()
                window = 252

                for i in range(window, len(daily_r), 21):  # Monthly sampling
                    window_r = daily_r.iloc[i - window : i]
                    date = str(daily_r.index[i])[:10]
                    mean_w = float(window_r.mean())
                    std_w = float(window_r.std())
                    rs = (mean_w / std_w) * math.sqrt(252) if std_w > 0 else 0

                    down_w = window_r[window_r < 0]
                    down_std_w = float(down_w.std()) if len(down_w) > 0 else 0
                    so = (mean_w / down_std_w) * math.sqrt(252) if down_std_w > 0 else 0

                    rolling_metrics.append(
                        RollingMetricPoint(
                            date=date,
                            rollingSharpe=round(rs, 2),
                            rollingSortino=round(so, 2),
                        )
                    )

            # ----------------------------------------------------------------
            # Return Distribution
            # ----------------------------------------------------------------
            return_distribution: List[ReturnDistributionBucket] = []
            if not trades.empty:
                bins = [
                    (-float("inf"), -20, "<-20%"),
                    (-20, -10, "-20% to -10%"),
                    (-10, -5, "-10% to -5%"),
                    (-5, 0, "-5% to 0%"),
                    (0, 5, "0% to 5%"),
                    (5, 10, "5% to 10%"),
                    (10, 20, "10% to 20%"),
                    (20, float("inf"), ">20%"),
                ]
                returns_arr = trades["Return %"].values
                total_t = len(returns_arr)
                for rmin, rmax, label in bins:
                    count = int(
                        ((returns_arr > rmin) & (returns_arr <= rmax)).sum()
                    )
                    return_distribution.append(
                        ReturnDistributionBucket(
                            rangeLabel=label,
                            rangeMin=rmin if rmin != -float("inf") else -999,
                            rangeMax=rmax if rmax != float("inf") else 999,
                            count=count,
                            percent=round(count / total_t * 100, 1) if total_t > 0 else 0,
                        )
                    )

            # ----------------------------------------------------------------
            # Holding Distribution
            # ----------------------------------------------------------------
            holding_distribution: List[HoldingDistributionBucket] = []
            if not trades.empty:
                holding_bins = [
                    (0, 5, "0-5 days"),
                    (5, 15, "6-15 days"),
                    (15, 30, "16-30 days"),
                    (30, 60, "31-60 days"),
                    (60, 90, "61-90 days"),
                    (90, float("inf"), ">90 days"),
                ]
                hd = trades["Holding Days"].values
                ret = trades["Return %"].values
                for hmin, hmax, label in holding_bins:
                    mask = (hd > hmin) & (hd <= hmax)
                    count = int(mask.sum())
                    avg_ret = (
                        float(ret[mask].mean()) if count > 0 else 0
                    )
                    holding_distribution.append(
                        HoldingDistributionBucket(
                            rangeLabel=label,
                            rangeMin=hmin,
                            rangeMax=hmax if hmax != float("inf") else 9999,
                            count=count,
                            avgReturn=round(avg_ret, 2),
                        )
                    )

            return AnalyticsSnapshot(
                strategyId=strategy_id,
                computedAt=now,
                totalReturn=round(total_return, 2),
                cagr=round(cagr, 2),
                sharpeRatio=round(sharpe, 2),
                sortinoRatio=round(sortino, 2),
                calmarRatio=round(calmar, 2),
                maxDrawdown=round(max_dd, 2),
                maxDrawdownDuration=max_dd_duration,
                recoveryFactor=round(recovery_factor, 2),
                totalTrades=int(total_trades),
                winRate=round(win_rate, 2),
                avgWinPercent=round(avg_win, 2),
                avgLossPercent=round(avg_loss, 2),
                profitFactor=round(profit_factor, 2),
                expectancy=round(expectancy, 2),
                avgHoldingDays=round(avg_holding, 1),
                volatilityAnnual=round(volatility, 2),
                beta=0.0,
                alpha=0.0,
                informationRatio=0.0,
                equityCurve=equity_points,
                drawdownPeriods=dd_periods[:20],  # Top 20
                monthlyReturns=monthly_returns,
                rollingMetrics=rolling_metrics,
                returnDistribution=return_distribution,
                holdingDistribution=holding_distribution,
            )

        except Exception as exc:
            logger.error(f"AnalyticsService.get_analytics: {exc}", exc_info=True)
            raise EngineNotReadyError(f"Analytics computation failed: {exc}")
