import io

import matplotlib

matplotlib.use("Agg")  # Run Matplotlib in "headless" mode
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

from economy.models import PriceHistory


async def generate_price_graph(price_records: list[PriceHistory]) -> io.BytesIO:
    timestamps = np.array([record.timestamp for record in price_records])
    prices = [float(record.price) for record in price_records]

    initial_price = prices[0]
    fig, ax = plt.subplots()
    ax.plot(
        timestamps,
        prices,
        marker="o",
        linestyle="-",
        label="Price",
    )

    # Starting reference line
    ax.axhline(
        y=initial_price,
        color="#E06C75",
        linestyle="--",
        alpha=0.8,
        label=f"Start ({initial_price})",
    )
    ax.legend(loc="upper left")

    ax.set_title(f"Price History for {price_records[0].item.name}")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Price (Gold.silver)")
    ax.grid(True, linestyle="--", alpha=0.6)

    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%m-%d %H:%M")
    )  # (Month-Day Hour:Minute)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    plt.close(fig)

    return buffer
