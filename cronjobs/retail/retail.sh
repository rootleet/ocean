#!/bin/bash
echo "RETAILER"

printf "CHECKING STOCK MONITOR"
/home/repositories/ocean/cronjobs/retail/update_stock.sh

printf "SYNCING SUPPLIERS.... \n"
/home/repositories/ocean/cronjobs/retail/sync_retail_suppliers.sh

printf "SYNCING GROUPS.... \n"
/home/repositories/ocean/cronjobs/retail/sync_retail_groups.sh

printf "SYNCING SUB GROUPS.... \n"
/home/repositories/ocean/cronjobs/retail/sync_retail_sub_groups.sh

printf "SYNCING PRODUCTS.... \n"
/home/repositories/ocean/cronjobs/retail/sync_retail_products.sh

printf "UPDATING STOCK.... \n"
/home/repositories/ocean/cronjobs/retail/update_stock.sh
