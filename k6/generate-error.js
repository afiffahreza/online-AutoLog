import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
    vus: 10,
    duration: '60s',
};

function getRandomInt(max) {
    const min = 1;
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min)) + min;
}

function readAll(url, path) {
    return http.get(url + path);
}

function readOne(url, path, id) {
    return http.get(url + path + '/' + id);
}

function createOne(url, path, data) {
    return http.post(url + path, data);
}

function updateOne(url, path, id, data) {
    return http.put(url + path + '/' + id, data);
}

function deleteOne(url, path, id) {
    return http.del(url + path + '/' + id);
}

export default function () {
    const url = 'http://127.0.0.1';


    //  ===== Catalog =====

    readAll(url, '/catalog');
    readOne(url, '/catalog', getRandomInt(3));
    readOne(url, '/catalog', getRandomInt(3));
    readOne(url, '/catalog', getRandomInt(3));

    const catalogPayload = JSON.stringify({
        "name": "Test Product",
        "price": 100.00,
    });

    let catalogRes = createOne(url, '/catalog', catalogPayload);
    let catalogId = catalogRes.json().data.catalog.id;

    readOne(url, '/catalog', catalogId);

    const catalogUpdatePayload = JSON.stringify({
        "name": "Test Product Updated",
        "price": 200.00,
    });

    updateOne(url, '/catalog', catalogId, catalogUpdatePayload);


    //  ===== Customer =====

    readAll(url, '/customer');
    readOne(url, '/customer', getRandomInt(3));
    readOne(url, '/customer', getRandomInt(3));
    readOne(url, '/customer', getRandomInt(3));

    const customerPayload = JSON.stringify({
        "name": "Test Customer",
        "email": "test123@gmail.com",
        "address": "Test Address",
    });

    let customerRes = createOne(url, '/customer', customerPayload);
    let customerId = customerRes.json().data.customer.id;

    readOne(url, '/customer', customerId);

    const customerUpdatePayload = JSON.stringify({
        "name": "Test Customer Updated",
        "email": "updatedtest123@gmail.com",
        "address": "Test Address",
    });

    updateOne(url, '/customer', customerId, customerUpdatePayload);


    //  ===== Order =====

    readAll(url, '/order');
    readOne(url, '/order', getRandomInt(3));
    readOne(url, '/order', getRandomInt(3));
    readOne(url, '/order', getRandomInt(3));

    const orderPayload = JSON.stringify({
        "customer_id": customerId,
        "catalog_id": catalogId,
        "quantity": 1,
    });

    let orderRes = createOne(url, '/order', orderPayload);
    let orderId = orderRes.json().data.order.id;

    readOne(url, '/order', orderId);

    const orderUpdatePayload = JSON.stringify({
        "customer_id": customerId,
        "catalog_id": catalogId,
        "quantity": 2,
    });

    updateOne(url, '/order', orderId, orderUpdatePayload);


    // ===== Delete =====

    deleteOne(url, '/order', orderId);
    deleteOne(url, '/customer', customerId);
    deleteOne(url, '/catalog', catalogId);

    sleep(1);
}
