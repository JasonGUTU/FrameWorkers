#!/usr/bin/env python3
# Entry point for the Plan Stack + Assistant Flask backend

from src.app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5002, debug=True)
