import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
    vus: 10,
    duration: '2s',
};

export default function () {
    http.get('http://127.0.0.1/catalog');
    http.get('http://127.0.0.1/catalog/1');
    http.get('http://127.0.0.1/catalog/2');
    http.get('http://127.0.0.1/customer');
    http.get('http://127.0.0.1/customer/1');
    http.get('http://127.0.0.1/customer/2');
    http.get('http://127.0.0.1/order');
    http.get('http://127.0.0.1/order/1');
    http.get('http://127.0.0.1/order/2');
    sleep(1);
}
