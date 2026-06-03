import os

class Config:
    """Production configuration for Gradio app"""
    
    # Server settings
    GRADIO_SERVER_NAME = os.environ.get("GRADIO_SERVER_NAME", "0.0.0.0")
    GRADIO_SERVER_PORT = int(os.environ.get("GRADIO_SERVER_PORT", "7860"))
    GRADIO_SHARE = False  # Never share in production
    
    # Security
    GRADIO_AUTH_MESSAGE = "Welcome to my Alter Ego"
    
    # CORS for iframe embedding
    GRADIO_ALLOWED_PATHS = ["/"]
    GRADIO_ANALYTICS_ENABLED = False
