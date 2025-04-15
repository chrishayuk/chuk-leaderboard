# chuk_leaderboard/visualizers/season_projection_visualizer.py
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from tabulate import tabulate
import matplotlib.patches as mpatches

# imports
from chuk_leaderboard.visualizers.rating_visualizer import RatingVisualizer


class SeasonProjectionVisualizer(RatingVisualizer):
    """
    Visualizer for season projections in points-based leagues.
    """
    def __init__(self, title: str = "Season Projections", output_dir: str = "output",
                weeks_in_season: int = 16, current_week: int = 0):
        """
        Initialize the season projection visualizer.
        
        Args:
            title: Title for visualizations
            output_dir: Directory to save output files
            weeks_in_season: Total number of weeks in the season
            current_week: Current week number (0-based)
        """
        super().__init__(title, output_dir)
        self.projections = {}
        self.weeks_in_season = weeks_in_season
        self.current_week = current_week
        self.history = {}
        self.league_name = "League"
    
    def set_league_info(self, league_name: str, weeks_in_season: int, current_week: int):
        """
        Set league information.
        
        Args:
            league_name: Name of the league
            weeks_in_season: Total number of weeks in the season
            current_week: Current week number (0-based)
        """
        self.league_name = league_name
        self.weeks_in_season = weeks_in_season
        self.current_week = current_week
    
    def add_participant(self, name: str, current_points: float, 
                       points_history: List[float], projection: Dict[str, float]):
        """
        Add a participant with their season projection data.
        
        Args:
            name: Participant name
            current_points: Current total points
            points_history: List of weekly point values
            projection: Dictionary with projection data (from PointsBasedRankingSystem.project_season_finish)
        """
        self.projections[name] = projection
        self.history[name] = {
            "current_points": current_points,
            "points_history": points_history
        }
    
    def plot_projections(self, figsize: Tuple[int, int] = (12, 8), confidence_level: float = 0.95):
        """
        Plot projected end-of-season standings with confidence intervals.
        
        Args:
            figsize: Figure size (width, height)
            confidence_level: Confidence level for intervals (used for labeling)
        """
        plt.figure(figsize=figsize)
        
        # Sort participants by projected points
        sorted_participants = sorted(
            [(name, data["projected_points"]) for name, data in self.projections.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        names = [item[0] for item in sorted_participants]
        projected = [self.projections[name]["projected_points"] for name in names]
        lower = [self.projections[name]["lower_bound"] for name in names]
        upper = [self.projections[name]["upper_bound"] for name in names]
        current = [self.history[name]["current_points"] for name in names]
        
        # Calculate error bars
        yerr_lower = [p - l for p, l in zip(projected, lower)]
        yerr_upper = [u - p for p, u in zip(projected, upper)]
        
        # Create positions for bars
        pos = np.arange(len(names))
        
        # Plot current points
        current_bars = plt.bar(pos, current, width=0.4, align='center', alpha=0.6, 
                              color='lightblue', label='Current Points')
        
        # Plot projected points with error bars
        plt.errorbar(pos, projected, yerr=[yerr_lower, yerr_upper], fmt='o', color='darkblue', 
                    capsize=5, capthick=2, label=f'Projected (Confidence: {confidence_level*100:.0f}%)')
        
        # Customize the plot
        plt.xlabel('Participant')
        plt.ylabel('Points')
        plt.title(f'{self.league_name} End-of-Season Projections (Week {self.current_week}/{self.weeks_in_season})')
        plt.xticks(pos, names, rotation=45, ha='right')
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
    
    def plot_weekly_trends(self, figsize: Tuple[int, int] = (14, 8), highlight_recent: int = 3):
        """
        Plot weekly point trends for all participants.
        
        Args:
            figsize: Figure size (width, height)
            highlight_recent: Number of recent weeks to highlight
        """
        plt.figure(figsize=figsize)
        
        # Prepare data
        max_history_len = max([len(data["points_history"]) for data in self.history.values()], default=0)
        week_labels = [f"Week {i+1}" for i in range(max_history_len)]
        
        # Sort participants by current points
        sorted_participants = sorted(
            [(name, data["current_points"]) for name, data in self.history.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        names = [item[0] for item in sorted_participants]
        
        # Plot each participant's weekly performance
        for name in names:
            points = self.history[name]["points_history"]
            weeks = list(range(1, len(points) + 1))
            
            # Split into normal and highlighted sections
            if highlight_recent > 0 and len(points) > highlight_recent:
                normal_weeks = weeks[:-highlight_recent]
                normal_points = points[:-highlight_recent]
                
                recent_weeks = weeks[-highlight_recent:]
                recent_points = points[-highlight_recent:]
                
                # Plot regular history
                plt.plot(normal_weeks, normal_points, 'o-', alpha=0.6, label=name if normal_weeks else None)
                
                # Plot highlighted recent performance with thicker line
                plt.plot(recent_weeks, recent_points, 'o-', linewidth=3, 
                        label=None if normal_weeks else name)
            else:
                plt.plot(weeks, points, 'o-', label=name)
        
        # Add league average if we have enough data
        if max_history_len > 0:
            all_points = []
            for week in range(max_history_len):
                week_points = []
                for name in self.history:
                    if week < len(self.history[name]["points_history"]):
                        week_points.append(self.history[name]["points_history"][week])
                
                if week_points:
                    all_points.append(sum(week_points) / len(week_points))
                else:
                    all_points.append(0)
            
            plt.plot(range(1, len(all_points) + 1), all_points, 'k--', linewidth=2, label='League Average')
        
        # Customize the plot
        plt.xlabel('Week')
        plt.ylabel('Points')
        plt.title(f'{self.league_name} Weekly Performance (Through Week {self.current_week})')
        plt.grid(True, alpha=0.3)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
        plt.tight_layout()
    
    def plot_projection_ranges(self, figsize: Tuple[int, int] = (12, 8)):
        """
        Plot min/max projection ranges for each participant.
        
        Args:
            figsize: Figure size (width, height)
        """
        plt.figure(figsize=figsize)
        
        # Sort participants by projected points
        sorted_participants = sorted(
            [(name, data["projected_points"]) for name, data in self.projections.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        names = [item[0] for item in sorted_participants]
        current = [self.history[name]["current_points"] for name in names]
        projected = [self.projections[name]["projected_points"] for name in names]
        min_points = [self.projections[name]["min_points"] for name in names]
        max_points = [self.projections[name]["max_points"] for name in names]
        
        # Create positions for bars
        pos = np.arange(len(names))
        width = 0.3
        
        # Plot current points
        plt.bar(pos - width/2, current, width=width, color='lightblue', label='Current')
        
        # Plot projected points
        plt.bar(pos + width/2, projected, width=width, color='darkblue', label='Projected')
        
        # Add min/max range lines
        for i, name in enumerate(names):
            plt.plot([pos[i] + width/2, pos[i] + width/2], 
                    [min_points[i], max_points[i]], 
                    'r-', linewidth=2)
            
            plt.plot([pos[i] + width/2 - 0.1, pos[i] + width/2 + 0.1], 
                    [min_points[i], min_points[i]], 
                    'r-', linewidth=2)
                    
            plt.plot([pos[i] + width/2 - 0.1, pos[i] + width/2 + 0.1], 
                    [max_points[i], max_points[i]], 
                    'r-', linewidth=2)
        
        # Add a legend element for the min/max range
        red_patch = mpatches.Patch(color='red', label='Min/Max Range')
        plt.legend(handles=[plt.Rectangle((0,0),1,1,color='lightblue', ec="k"), 
                          plt.Rectangle((0,0),1,1,color='darkblue', ec="k"),
                          red_patch])
        
        # Customize the plot
        plt.xlabel('Participant')
        plt.ylabel('Points')
        plt.title(f'{self.league_name} Projection Ranges (Week {self.current_week}/{self.weeks_in_season})')
        plt.xticks(pos, names, rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
    
    def print_projection_table(self):
        """Print a table of projections sorted by projected finish."""
        sorted_participants = sorted(
            [(name, self.projections[name]["projected_points"]) for name in self.projections],
            key=lambda x: x[1],
            reverse=True
        )
        
        table_data = []
        for rank, (name, _) in enumerate(sorted_participants, 1):
            proj = self.projections[name]
            current = self.history[name]["current_points"]
            
            # Calculate projected points to be gained
            to_gain = proj["projected_points"] - current
            
            # Determine trend based on recent performance
            points_history = self.history[name]["points_history"]
            if len(points_history) >= 6:  # Need at least 6 weeks to determine trend
                recent_avg = sum(points_history[-3:]) / 3
                previous_avg = sum(points_history[-6:-3]) / 3
                
                if recent_avg > previous_avg * 1.1:
                    trend = "▲"  # Up
                elif recent_avg < previous_avg * 0.9:
                    trend = "▼"  # Down
                else:
                    trend = "◆"  # Stable
            else:
                trend = "◆"  # Default to stable if not enough data
            
            # Format confidence interval
            confidence = f"{proj['lower_bound']:.1f} - {proj['upper_bound']:.1f}"
            
            table_data.append([
                f"{rank}",
                name,
                f"{current:.1f}",
                f"{proj['projected_points']:.1f}",
                f"{to_gain:.1f}",
                confidence,
                trend
            ])
        
        headers = ["Rank", "Name", "Current", "Projected", "To Gain", "Confidence Interval", "Trend"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))