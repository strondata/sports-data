#!/usr/bin/env bash

# sports-data CLI Tool

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}        Sports Data Framework          ${NC}"
echo -e "${BLUE}=======================================${NC}"

show_menu() {
    echo -e "\nSelect an option:"
    echo "1) Install Dependencies (poetry install)"
    echo "2) Run ETL Pipeline for Bayern Munich 2025/2026"
    echo "3) Run Tests (pytest)"
    echo "4) Run Linter (ruff)"
    echo "5) Run Type Checker (mypy)"
    echo "6) Start FastAPI Backend Server (port 8000)"
    echo "7) Start Frontend Server (port 3000)"
    echo "8) Exit"
}

while true; do
    show_menu
    read -p "Enter your choice [1-8]: " choice

    case $choice in
        1)
            echo -e "\n${GREEN}Installing dependencies...${NC}"
            poetry install
            ;;
        2)
            echo -e "\n${GREEN}Running ETL Pipeline...${NC}"
            poetry run sports-data run --url "https://fbref.com/en/squads/054efa67/2025-2026/matchlogs/all_comps/schedule/Bayern-Munich-Scores-and-Fixtures-All-Competitions"
            ;;
        3)
            echo -e "\n${GREEN}Running Tests...${NC}"
            poetry run pytest
            ;;
        4)
            echo -e "\n${GREEN}Running Linter...${NC}"
            poetry run ruff check .
            ;;
        5)
            echo -e "\n${GREEN}Running Type Checker...${NC}"
            poetry run mypy src
            ;;
        6)
            echo -e "\n${GREEN}Starting FastAPI Backend...${NC}"
            echo "Press Ctrl+C to stop."
            poetry run uvicorn src.api.main:app --host 0.0.0.0 --port 8000
            ;;
        7)
            echo -e "\n${GREEN}Starting Frontend Server...${NC}"
            echo "Press Ctrl+C to stop."
            poetry run python -m http.server 3000 --directory frontend
            ;;
        8)
            echo -e "\nExiting..."
            exit 0
            ;;
        *)
            echo -e "\nInvalid option. Please try again."
            ;;
    esac
done