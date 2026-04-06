"""
Generate PNG chart cards optimized for social media sharing.
Creates Twitter/X-sized (1200x675) and Instagram-sized (1080x1080) images.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("media/chart_cards")

# Consistent styling
DARK_BG = '#0a0a0f'
CARD_BG = '#1a1a2e'
TEXT_PRIMARY = '#e8e8f0'
TEXT_SECONDARY = '#8888aa'
RED = '#ff4757'
ORANGE = '#ff8c42'
BLUE = '#4ea8de'


def setup_style():
    plt.rcParams.update({
        'figure.facecolor': DARK_BG,
        'axes.facecolor': CARD_BG,
        'text.color': TEXT_PRIMARY,
        'axes.labelcolor': TEXT_SECONDARY,
        'xtick.color': TEXT_SECONDARY,
        'ytick.color': TEXT_SECONDARY,
        'font.family': 'sans-serif',
        'font.size': 12,
    })


def generate_oil_price_card():
    """Generate oil price chart card for social media."""
    dates = ['Feb 27', 'Mar 4', 'Mar 8', 'Mar 12', 'Mar 19', 'Mar 23', 'Mar 30', 'Apr 5']
    brent = [73, 91, 103, 115, 126, 104, 116, 113]

    fig, ax = plt.subplots(figsize=(12, 6.75))
    ax.fill_between(range(len(dates)), brent, alpha=0.3, color=RED)
    ax.plot(brent, color=RED, linewidth=3, marker='o', markersize=8)
    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels(dates, fontsize=11)
    ax.set_ylabel('USD / barrel', fontsize=13)
    ax.set_title('Brent Crude Oil Price — 2026 Iran Conflict', fontsize=18, fontweight='bold', pad=20)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('$%d'))

    # Add annotation
    ax.annotate(f'Peak: $126', xy=(4, 126), xytext=(5, 130),
                fontsize=12, color=RED, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=RED))

    # Branding
    fig.text(0.02, 0.02, 'War Impact Observatory | warimpactobservatory.org | CC BY 4.0',
             fontsize=9, color=TEXT_SECONDARY)
    fig.text(0.98, 0.02, datetime.utcnow().strftime('%Y-%m-%d'),
             fontsize=9, color=TEXT_SECONDARY, ha='right')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'oil_price_twitter.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Generated: oil_price_twitter.png")


def generate_household_cost_card():
    """Generate household cost comparison card."""
    countries = ['Germany', 'US', 'Italy', 'UK', 'Japan', 'Australia', 'S. Korea', 'India', 'Turkey', 'Brazil']
    costs = [2800, 2400, 2300, 2200, 2100, 1900, 1600, 480, 380, 350]

    fig, ax = plt.subplots(figsize=(12, 6.75))
    colors = [RED if c > 2000 else ORANGE if c > 1000 else BLUE for c in costs]
    bars = ax.barh(countries[::-1], costs[::-1], color=colors[::-1], height=0.6)

    for bar, cost in zip(bars, costs[::-1]):
        ax.text(bar.get_width() + 30, bar.get_y() + bar.get_height()/2,
                f'${cost:,}/yr', va='center', fontsize=11, fontweight='bold', color=TEXT_PRIMARY)

    ax.set_xlabel('Additional Annual Cost per Household (USD)', fontsize=13)
    ax.set_title('How Much Is the Iran War Costing Your Household?', fontsize=18, fontweight='bold', pad=20)
    ax.set_xlim(0, max(costs) * 1.25)

    fig.text(0.02, 0.02, 'War Impact Observatory | warimpactobservatory.org | CC BY 4.0',
             fontsize=9, color=TEXT_SECONDARY)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'household_cost_twitter.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Generated: household_cost_twitter.png")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    setup_style()

    print("Generating social media chart cards...")
    generate_oil_price_card()
    generate_household_cost_card()
    print("Done!")


if __name__ == "__main__":
    main()
