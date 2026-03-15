"""Генерация красивых графиков цен через Matplotlib."""
import io
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


def _setup_dark_style():
    plt.rcParams.update({
        "figure.facecolor": "#12121a",
        "axes.facecolor": "#12121a",
        "axes.edgecolor": "#22223a",
        "text.color": "#e2e8f0",
        "axes.labelcolor": "#e2e8f0",
        "xtick.color": "#64748b",
        "ytick.color": "#64748b",
        "grid.color": "#22223a",
        "grid.alpha": 0.5,
    })


def generate_price_chart(prices: list, coin: str, days: int) -> io.BytesIO:
    _setup_dark_style()

    timestamps = [datetime.fromtimestamp(p[0] / 1000) for p in prices]
    values = [p[1] for p in prices]

    fig, ax = plt.subplots(figsize=(10, 5))

    is_up = values[-1] >= values[0]
    color = "#00ff88" if is_up else "#ff4757"

    # Fill gradient
    ax.fill_between(timestamps, values, alpha=0.15, color=color)
    ax.plot(timestamps, values, color=color, linewidth=2, zorder=5)

    # Moving average
    if len(values) > 14:
        window = max(5, len(values) // 20)
        ma = np.convolve(values, np.ones(window) / window, mode="valid")
        ax.plot(timestamps[window - 1:], ma, color="#8b5cf6", linewidth=1.2, linestyle="--", alpha=0.7, label="MA")

    # Min/max markers
    min_idx = np.argmin(values)
    max_idx = np.argmax(values)
    ax.scatter([timestamps[min_idx]], [values[min_idx]], color="#ff4757", s=60, zorder=10)
    ax.scatter([timestamps[max_idx]], [values[max_idx]], color="#00ff88", s=60, zorder=10)

    ax.set_title(
        f"{coin} / USD  ·  {days}d  {'▲' if is_up else '▼'} {((values[-1]/values[0]-1)*100):+.1f}%",
        fontsize=14, fontweight="bold",
        color=color, pad=12,
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}" if x >= 1 else f"${x:.4f}"))
    ax.grid(True, linestyle="--", linewidth=0.5)
    ax.tick_params(labelsize=9)

    if len(values) > 14:
        ax.legend(facecolor="#1a1a26", edgecolor="#22223a", labelcolor="#8b5cf6", fontsize=8)

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf
