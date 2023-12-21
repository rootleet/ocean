curl --location --request PATCH 'http://127.0.0.1/servicing/api/' \
--header 'Content-Type: text/plain' \
--header 'Cookie: csrftoken=etMJ2XQLTdShoVg4UxIfhE67JjVuYtNP' \
--data '{
    "module":"close_sent",
    "data":{}
}'