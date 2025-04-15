# chuk_leaderboard/visualizers/base.py
import os
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Tuple


class BaseVisualizer:
    """
    Base class for all visualizers.
    """
    def __init__(self, title: str = "Visualization", output_dir: str = "output"):
        self.title = title
        self.filename = title.replace(' ', '_').lower()
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def save(self, filename: Optional[str] = None):
        """Save the current figure to a file."""
        if filename:
            # Handle both absolute paths and relative paths
            if os.path.isabs(filename):
                plt.savefig(filename)
            else:
                plt.savefig(os.path.join(self.output_dir, filename))
        else:
            plt.savefig(os.path.join(self.output_dir, f"{self.filename}.png"))
        plt.close()
    
    def show(self):
        """Display the current figure."""
        plt.show()

