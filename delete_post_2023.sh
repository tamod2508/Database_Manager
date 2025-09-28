#!/bin/bash

# Script to delete stock data after 2023 from the database
# This will test incremental update functionality

# Configuration (relative paths)
DB_PATH="data/db/historical_data.db"
BACKUP_PATH="data/db/historical_data_backup_$(date +%Y%m%d_%H%M%S).db"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Delete Post-2023 Stock Data ===${NC}"
echo

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo -e "${RED}Error: Database not found at $DB_PATH${NC}"
    echo "Please make sure you're running this from the project root directory."
    exit 1
fi

# Show current database stats
echo -e "${BLUE}Current database statistics:${NC}"
sqlite3 "$DB_PATH" "
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT ticker) as unique_tickers,
    MIN(date) as earliest_date,
    MAX(date) as latest_date
FROM stock_data;
"
echo

# Show records by year
echo -e "${BLUE}Records by year:${NC}"
sqlite3 "$DB_PATH" "
SELECT 
    substr(date, 1, 4) as year,
    COUNT(*) as record_count
FROM stock_data 
GROUP BY substr(date, 1, 4)
ORDER BY year;
"
echo

# Count records that will be deleted
records_to_delete=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM stock_data WHERE date > '2023-12-31';")
echo -e "${YELLOW}Records to be deleted (after 2023): $records_to_delete${NC}"
echo

# Confirmation prompt
echo -e "${YELLOW}This will:${NC}"
echo "1. Create a backup of your current database"
echo "2. Delete all records with dates after 2023-12-31"
echo "3. Allow you to test incremental updates for 2024 data"
echo

read -p "Do you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Operation cancelled.${NC}"
    exit 0
fi

# Create backup
echo -e "${BLUE}Creating backup...${NC}"
cp "$DB_PATH" "$BACKUP_PATH"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Backup created: $BACKUP_PATH${NC}"
else
    echo -e "${RED}Failed to create backup. Aborting.${NC}"
    exit 1
fi

# Delete post-2023 data
echo -e "${BLUE}Deleting records after 2023...${NC}"
deleted_count=$(sqlite3 "$DB_PATH" "
BEGIN TRANSACTION;
DELETE FROM stock_data WHERE date > '2023-12-31';
SELECT changes();
COMMIT;
")

echo -e "${GREEN}Deleted $deleted_count records${NC}"

# Run VACUUM to reclaim space
echo -e "${BLUE}Optimizing database...${NC}"
sqlite3 "$DB_PATH" "VACUUM;"
echo -e "${GREEN}Database optimized${NC}"

# Show updated statistics
echo
echo -e "${BLUE}Updated database statistics:${NC}"
sqlite3 "$DB_PATH" "
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT ticker) as unique_tickers,
    MIN(date) as earliest_date,
    MAX(date) as latest_date
FROM stock_data;
"

echo
echo -e "${BLUE}Updated records by year:${NC}"
sqlite3 "$DB_PATH" "
SELECT 
    substr(date, 1, 4) as year,
    COUNT(*) as record_count
FROM stock_data 
GROUP BY substr(date, 1, 4)
ORDER BY year;
"

echo
echo -e "${GREEN}=== Operation Complete ===${NC}"
echo -e "${GREEN}✓ Backup created: $BACKUP_PATH${NC}"
echo -e "${GREEN}✓ Deleted $deleted_count records after 2023${NC}"
echo -e "${GREEN}✓ Database optimized${NC}"
echo
echo -e "${YELLOW}Now you can test incremental updates:${NC}"
echo "1. Run your GUI application"
echo "2. Click 'Check Update Plan' - should show many symbols need updates"
echo "3. Click 'Update Data' - should fetch 2024 data incrementally"
echo
echo -e "${BLUE}To restore original data: cp \"$BACKUP_PATH\" \"$DB_PATH\"${NC}"
