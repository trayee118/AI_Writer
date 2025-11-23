# config.py - Configuration Settings

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Configuration class for AI Writer application
    All settings can be overridden via environment variables
    """
    
    # ==================== Server Configuration ====================
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # ==================== Model Configuration ====================
    # Available models (from lightweight to heavy):
    # - "distilgpt2" (82M params - Fastest, smallest)
    # - "gpt2" (124M params - Good balance, recommended)
    # - "gpt2-medium" (355M params - Better quality, needs more RAM)
    # - "gpt2-large" (774M params - High quality, needs 8GB+ RAM)
    # - "EleutherAI/gpt-neo-125M" (125M params - Good alternative)
    # - "EleutherAI/gpt-neo-1.3B" (1.3B params - Very good, needs GPU)
    # - "facebook/opt-350m" (350M params - Good quality)
    
    MODEL_NAME = os.getenv('MODEL_NAME', 'gpt2')
    
    # ==================== Generation Parameters ====================
    MAX_LENGTH = int(os.getenv('MAX_LENGTH', 500))
    MIN_LENGTH = int(os.getenv('MIN_LENGTH', 50))
    TEMPERATURE = float(os.getenv('TEMPERATURE', 0.7))
    TOP_P = float(os.getenv('TOP_P', 0.9))
    TOP_K = int(os.getenv('TOP_K', 50))
    REPETITION_PENALTY = float(os.getenv('REPETITION_PENALTY', 1.2))
    
    # ==================== CORS Settings ====================
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    
    # ==================== Logging Configuration ====================
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # ==================== API Configuration ====================
    API_TITLE = os.getenv('API_TITLE', 'AI Writer API')
    API_VERSION = os.getenv('API_VERSION', '1.0.0')
    API_DESCRIPTION = os.getenv('API_DESCRIPTION', 'Generate high-quality content with AI')
    
    # ==================== Rate Limiting (Optional) ====================
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'False').lower() == 'true'
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 10))
    
    # ==================== Cache Settings (Optional) ====================
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'False').lower() == 'true'
    CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))  # Time to live in seconds
    
    # ==================== Model Loading Settings ====================
    LOW_CPU_MEM_USAGE = os.getenv('LOW_CPU_MEM_USAGE', 'True').lower() == 'true'
    USE_GPU = os.getenv('USE_GPU', 'False').lower() == 'true'
    DEVICE = 0 if USE_GPU else -1  # 0 for GPU, -1 for CPU
    
    @classmethod
    def get_config_dict(cls):
        """
        Get all configuration as dictionary
        
        Returns:
            dict: Configuration dictionary
        """
        return {
            'server': {
                'host': cls.HOST,
                'port': cls.PORT,
                'debug': cls.DEBUG
            },
            'model': {
                'name': cls.MODEL_NAME,
                'device': 'GPU' if cls.USE_GPU else 'CPU'
            },
            'generation': {
                'max_length': cls.MAX_LENGTH,
                'min_length': cls.MIN_LENGTH,
                'temperature': cls.TEMPERATURE,
                'top_p': cls.TOP_P,
                'top_k': cls.TOP_K,
                'repetition_penalty': cls.REPETITION_PENALTY
            },
            'api': {
                'title': cls.API_TITLE,
                'version': cls.API_VERSION,
                'cors_origins': cls.CORS_ORIGINS
            }
        }
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("\n" + "=" * 60)
        print("⚙️  AI Writer Configuration")
        print("=" * 60)
        print(f"🌐 Server:")
        print(f"   • Host: {cls.HOST}")
        print(f"   • Port: {cls.PORT}")
        print(f"   • Debug: {cls.DEBUG}")
        print(f"\n🤖 Model:")
        print(f"   • Name: {cls.MODEL_NAME}")
        print(f"   • Device: {'GPU' if cls.USE_GPU else 'CPU'}")
        print(f"   • Low CPU Memory: {cls.LOW_CPU_MEM_USAGE}")
        print(f"\n📝 Generation:")
        print(f"   • Max Length: {cls.MAX_LENGTH}")
        print(f"   • Min Length: {cls.MIN_LENGTH}")
        print(f"   • Temperature: {cls.TEMPERATURE}")
        print(f"   • Top P: {cls.TOP_P}")
        print(f"   • Top K: {cls.TOP_K}")
        print(f"   • Repetition Penalty: {cls.REPETITION_PENALTY}")
        print(f"\n🔐 API:")
        print(f"   • CORS Origins: {cls.CORS_ORIGINS}")
        print(f"   • Rate Limiting: {cls.RATE_LIMIT_ENABLED}")
        print("=" * 60 + "\n")
    
    @classmethod
    def validate_config(cls):
        """
        Validate configuration settings
        
        Returns:
            tuple: (is_valid, error_message)
        """
        errors = []
        
        # Validate port
        if not (1 <= cls.PORT <= 65535):
            errors.append(f"Invalid PORT: {cls.PORT}. Must be between 1 and 65535")
        
        # Validate temperature
        if not (0.0 <= cls.TEMPERATURE <= 2.0):
            errors.append(f"Invalid TEMPERATURE: {cls.TEMPERATURE}. Must be between 0.0 and 2.0")
        
        # Validate top_p
        if not (0.0 <= cls.TOP_P <= 1.0):
            errors.append(f"Invalid TOP_P: {cls.TOP_P}. Must be between 0.0 and 1.0")
        
        # Validate lengths
        if cls.MIN_LENGTH > cls.MAX_LENGTH:
            errors.append(f"MIN_LENGTH ({cls.MIN_LENGTH}) cannot be greater than MAX_LENGTH ({cls.MAX_LENGTH})")
        
        if errors:
            return False, "\n".join(errors)
        
        return True, "Configuration is valid"


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'https://yourdomain.com')


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    MODEL_NAME = 'distilgpt2'  # Use smaller model for testing
    MAX_LENGTH = 100


# Config selector based on environment
def get_config():
    """
    Get configuration based on environment
    
    Returns:
        Config: Configuration class
    """
    env = os.getenv('ENV', 'development').lower()
    
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return configs.get(env, DevelopmentConfig)