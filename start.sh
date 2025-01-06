#!/bin/bash
gunicorn expenses:app --bind 0.0.0.0:$PORT
