import streamlit as st
from src.app_factory import init_app
from src.router import Router

class App:
    """Main application class."""
    
    def __init__(self):
        self.router = Router()
        
    def initialize(self):
        """Initialize the application."""
        init_app()
        
    def run(self):
        """Run the application."""
        self.initialize()
        self.router.handle_routing()

def main():
    """Main application entry point."""
    app = App()
    app.run()

if __name__ == "__main__":
    main() 