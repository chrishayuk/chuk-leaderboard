# chuk_leaderboard/rating_systems/registry.py

# imports
from typing import List, Optional
from chuk_leaderboard.rating_systems.rating_system import RatingSystem

class RatingSystemRegistry:
    """
    Registry for available rating systems.
    """
    _registry = {}
    
    @classmethod
    def register(cls, name: str, system_cls):
        """
        Register a rating system.
        
        Args:
            name: Name of the rating system
            system_cls: Rating system class
        """
        cls._registry[name.lower()] = system_cls
    
    @classmethod
    def get(cls, name: str, **kwargs) -> Optional[RatingSystem]:
        """
        Get a rating system by name.
        
        Args:
            name: Name of the rating system
            **kwargs: Additional parameters to pass to the rating system constructor
        
        Returns:
            Initialized rating system or None if not found
        """
        system_cls = cls._registry.get(name.lower())
        if system_cls:
            return system_cls(**kwargs)
        return None
    
    @classmethod
    def list_available(cls) -> List[str]:
        """
        List all available rating systems.
        
        Returns:
            List of registered rating system names
        """
        return list(cls._registry.keys())


def get_rating_system(system_name: str, **kwargs) -> RatingSystem:
    """
    Factory function to get a rating system by name.
    
    Args:
        system_name: Name of the rating system
        **kwargs: Additional parameters to pass to the rating system constructor
    
    Returns:
        Initialized rating system
    
    Raises:
        ValueError: If the requested rating system is not supported
    """
    system = RatingSystemRegistry.get(system_name, **kwargs)
    if system is None:
        available = RatingSystemRegistry.list_available()
        raise ValueError(f"Unsupported rating system: {system_name}. "
                         f"Available systems: {', '.join(available)}")
    return system