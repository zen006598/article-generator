# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based article generator project using `uv` for dependency management. The project is in early development with a basic structure consisting of a main entry point and minimal dependencies.

## Development Commands

- **Run the application**: `uv run main.py`
- **Install dependencies**: `uv install` (uses uv.lock for consistent installs)
- **Add new dependencies**: `uv add <package-name>`
- **Python version**: Requires Python >= 3.13.5

## Project Structure

- `main.py` - Entry point with basic "Hello World" functionality
- `pyproject.toml` - Project configuration and dependencies
- `uv.lock` - Locked dependency versions for reproducible builds

## Dependencies

- `python-dotenv` - For environment variable management

## Development Notes

- This project uses `uv` as the package manager instead of pip
- The codebase is minimal and appears to be a starting template for an article generation tool
- No testing framework is currently configured