# Microsevices Demo
https://github.com/ewolff/microservice-kubernetes/tree/master

## Routes
- / : Home
- /customer/list.html : List of customers
- /customer/{id}.html : Customer details & edit form
- /customer/form.html : New customer form
- /catalog/list.html : List of items
- /catalog/{id}.html : Item details & edit form
- /catalog/form.html : New item form
- /catalog/searchForm.html : Search item form
- /catalog/searchByName.html?query={itemName}&submit= : Search item by name
- /order/ : List of orders
- /order/form.html : New order form

## POST/PUT Data
- customer
    - String name
    - String firstname
    - String email
    - String street
    - String city
- catalog
    - String name
    - String description
    - Double price
- order
