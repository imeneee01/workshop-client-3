"""Visualisations : cartes choroplethes departementales et graphiques."""
import matplotlib.pyplot as plt


def choropleth(gdf, column, title, cmap="viridis", legend_label=None):
    """Carte choroplethe de la France par departement sur `column`."""
    fig, ax = plt.subplots(figsize=(8, 8))
    gdf.plot(
        column=column, ax=ax, cmap=cmap, legend=True,
        edgecolor="white", linewidth=0.3,
        legend_kwds={"label": legend_label or column, "shrink": 0.6},
        missing_kwds={"color": "lightgrey", "label": "n/d"},
    )
    ax.set_title(title, fontsize=13)
    ax.axis("off")
    fig.tight_layout()
    return fig


def bar_chart(labels, values, title, xlabel, ylabel, color="#2c7fb8"):
    """Diagramme en barres simple."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar([str(l) for l in labels], values, color=color)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    return fig


def grouped_bar(labels, series_dict, title, xlabel, ylabel):
    """Barres groupees : series_dict = {nom_serie: [valeurs]}."""
    import numpy as np
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(labels))
    n = len(series_dict)
    width = 0.8 / n
    for i, (name, vals) in enumerate(series_dict.items()):
        ax.bar(x + i * width, vals, width, label=name)
    ax.set_xticks(x + width * (n - 1) / 2)
    ax.set_xticklabels([str(l) for l in labels])
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    fig.tight_layout()
    return fig
