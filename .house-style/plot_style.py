import matplotlib.pyplot as plt

COLORS = {
    'primary': '#000000',
    'secondary': '#E85D4C',  # Coral (extended)
    'tertiary': '#4DA375',   # Sage Green (parent)
    'quaternary': '#9B6B9E', # Muted Purple (grandparent)
}

def setup():
    """Configure matplotlib with house style settings."""
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['EB Garamond', 'Garamond', 'Georgia', 'Times New Roman'],
        # Use STIX fonts for math to blend better with Garamond than default CM
        'mathtext.fontset': 'stix',
        'axes.spines.top': False,
        'axes.spines.right': False,
        'legend.frameon': False,
        'figure.dpi': 200,
        'savefig.bbox': 'tight',
    })

def save_figure(fig, path_base):
    """Save figure as PDF and PNG."""
    fig.savefig(f'{path_base}.pdf')
    fig.savefig(f'{path_base}.png', dpi=200)

def add_grid(ax, axis='y', **kwargs):
    """Add standardized grid lines."""
    default_kwargs = {'linestyle': ':', 'linewidth': 0.5, 'color': '#E8E8E8'}
    default_kwargs.update(kwargs)
    ax.grid(True, axis=axis, **default_kwargs)
