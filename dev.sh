#!/bin/bash

# ShopEAT Development Script with UV
# This script provides common development tasks using UV

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "backend/pyproject.toml" ]; then
    print_error "Please run this script from the ShopEAT root directory"
    exit 1
fi

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    print_error "UV is not installed. Please run ./setup.sh first"
    exit 1
fi

# Function to setup backend environment
setup_backend() {
    print_status "Setting up backend development environment..."
    cd backend
    
    if [ ! -d ".venv" ]; then
        print_status "Creating virtual environment with UV..."
        uv venv
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    print_status "Installing dependencies with UV..."
    uv pip install -e '.[dev]'
    print_success "Dependencies installed"
    
    cd ..
}

# Function to format code
format_code() {
    print_status "Formatting code with Black..."
    cd backend
    uv run black .
    print_success "Code formatted with Black"
    
    print_status "Sorting imports with isort..."
    uv run isort .
    print_success "Imports sorted with isort"
    cd ..
}

# Function to lint code
lint_code() {
    print_status "Linting code with flake8..."
    cd backend
    uv run flake8 .
    print_success "Code linted with flake8"
    cd ..
}

# Function to type check
type_check() {
    print_status "Running type checking with mypy..."
    cd backend
    uv run mypy .
    print_success "Type checking completed"
    cd ..
}

# Function to run tests
run_tests() {
    print_status "Running tests with pytest..."
    cd backend
    uv run pytest
    print_success "Tests completed"
    cd ..
}

# Function to start backend
start_backend() {
    print_status "Starting backend server..."
    cd backend
    source .venv/bin/activate
    python main.py
}

# Function to show help
show_help() {
    echo "ShopEAT Development Script with UV"
    echo "=================================="
    echo ""
    echo "Usage: ./dev.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup      - Setup backend development environment"
    echo "  format     - Format code with Black and isort"
    echo "  lint       - Lint code with flake8"
    echo "  typecheck  - Run type checking with mypy"
    echo "  test       - Run tests with pytest"
    echo "  start      - Start backend server"
    echo "  all        - Run format, lint, typecheck, and test"
    echo "  help       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./dev.sh setup      # Setup development environment"
    echo "  ./dev.sh format     # Format code"
    echo "  ./dev.sh all        # Run all checks"
    echo "  ./dev.sh start      # Start backend server"
}

# Main script logic
case "${1:-help}" in
    "setup")
        setup_backend
        ;;
    "format")
        format_code
        ;;
    "lint")
        lint_code
        ;;
    "typecheck")
        type_check
        ;;
    "test")
        run_tests
        ;;
    "start")
        start_backend
        ;;
    "all")
        print_status "Running all development checks..."
        format_code
        lint_code
        type_check
        run_tests
        print_success "All development checks completed!"
        ;;
    "help"|*)
        show_help
        ;;
esac
