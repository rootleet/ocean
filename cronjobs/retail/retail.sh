#!/bin/bash
echo "RETAILER"

printf "SYNCING SUPPLIERS.... \n"
./sync_retail_suppliers.sh

printf "SYNCING GROUPS.... \n"
./sync_retail_groups.sh

printf "SYNCING SUB GROUPS.... \n"
./sync_retail_sub_groups.sh

printf "SYNCING PRODUCTS.... \n"
./sync_retail_products.sh

printf "UPDATING STOCK.... \n"
./update_stock.sh