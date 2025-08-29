"""
Configuration settings for the Pomodoro system
"""

from pydantic import BaseSettings
from typing import Optional

class PomodoroSettings(BaseSettings):
    """Pomodoro system configuration"""
    
    # Timer settings
    DEFAULT_TIMER_MINUTES: int = 25
    DEFAULT_REST_MINUTES: int = 5
    MIN_TIMER_MINUTES: int = 1
    MAX_TIMER_MINUTES: int = 120
    
    # Update intervals
    PROGRESS_UPDATE_INTERVAL: int = 10  # seconds
    TIMER_PRECISION: float = 0.1  # seconds
    
    # Session management
    MAX_ACTIVE_SESSIONS_PER_USER: int = 5
    SESSION_CLEANUP_TIMEOUT: int = 300  # seconds
    
    # Database settings
    DB_UPDATE_BATCH_SIZE: int = 100
    DB_CONNECTION_TIMEOUT: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Health check
    HEALTH_CHECK_INTERVAL: int = 60  # seconds
    HEALTH_CHECK_TIMEOUT: int = 10  # seconds
    
    # Performance
    MAX_CONCURRENT_TIMERS: int = 100
    TIMER_MEMORY_LIMIT: int = 1000  # MB
    
    class Config:
        env_prefix = "POMODORO_"
        case_sensitive = False

# Global settings instance
pomodoro_settings = PomodoroSettings()

# Validation functions
def validate_timer_duration(minutes: int) -> bool:
    """Validate timer duration is within acceptable range"""
    return pomodoro_settings.MIN_TIMER_MINUTES <= minutes <= pomodoro_settings.MAX_TIMER_MINUTES

def validate_rest_duration(minutes: int) -> bool:
    """Validate rest duration is non-negative"""
    return minutes >= 0

def get_default_timer() -> int:
    """Get default timer duration in minutes"""
    return pomodoro_settings.DEFAULT_TIMER_MINUTES

def get_default_rest() -> int:
    """Get default rest duration in minutes"""
    return pomodoro_settings.DEFAULT_REST_MINUTES

def get_progress_update_interval() -> int:
    """Get progress update interval in seconds"""
    return pomodoro_settings.PROGRESS_UPDATE_INTERVAL

def get_timer_precision() -> float:
    """Get timer precision in seconds"""
    return pomodoro_settings.TIMER_PRECISION

def get_max_active_sessions() -> int:
    """Get maximum active sessions per user"""
    return pomodoro_settings.MAX_ACTIVE_SESSIONS_PER_USER

def get_session_cleanup_timeout() -> int:
    """Get session cleanup timeout in seconds"""
    return pomodoro_settings.SESSION_CLEANUP_TIMEOUT

def get_health_check_interval() -> int:
    """Get health check interval in seconds"""
    return pomodoro_settings.HEALTH_CHECK_INTERVAL

def get_max_concurrent_timers() -> int:
    """Get maximum concurrent timers"""
    return pomodoro_settings.MAX_CONCURRENT_TIMERS
