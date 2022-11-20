### Purchase Order
There are instances inventory needs new stock. In my immediate scenario, I am our of stock for toner cartridges. In this case, I will have to make a purchase.
Traditionally? I will 
- Call at least three suppliers
- Compare prises and quality
- Inform accounts of the purchase and wait for their approval to proceed

With ocean, this is going in a different dimension and starts from inventory module
- From inventory, a user ( stock-keeper ) can make a purchase order
- The order details contains Supplier, Location, Remark, and Items
- The supplier will have to exist in the application. With supplier master, a user can create a new supplier
- Location is necessary since when processing the document on receiving, stock adjustment should affect purchase location
- Remark is a descriptive detail of why purchase which is required.
- Items will be the items to purchase
- Email is sent to accountant to approve purchasing
- Accountant will approve or reject purchase with description
- Purchaser will proceed

#### API
Since i already have a live application that does similar thing built with procedure php, focus is making everything through an API so other applications with access can 
make API request and responses.

Creating a purchase request has two parts. 
- Po Header : This contains header information of the document ( Location,Supplier,Date Created,Document Status `approved`,`pending`,`rejected`,  )
- Po Transactions : This contains list of items and each item has line entry number (Foreign Key of a po header),line number (to arrange items sequentially),product (Foreign of a product to products master ), packing (this will affect total quantity calculations),quantity (quantity purchasing), total (total purchasing)

When saving a purchase document, for each transaction, packing is checked and multiplied by quantity to give total.
For instance, when the item is 12 in a container, packing will be 12, and quantity will be container purchased.

So if 2 containers are purchased? Total will be packing * quantity
