const control_product_btns = document.querySelectorAll('.include__buttons');  // блоки с кнопками + - и количество
let web_socket_url = `ws://${window.location.host}/ws/socket-server/`;
const count_tour = new WebSocket(web_socket_url);
const stays = document.querySelectorAll('.stay .stay__count');
count_tour.onopen = function (event) {
    // Отправляем данные после успешной установки соединения
    for(let stay of stays) {
        count_tour.send(JSON.stringify({
            'count': stay.innerHTML,
            'id': stay.dataset.setId,
        }));
    }
};
count_tour.onmessage = function (ev){
    let data = JSON.parse(ev.data)
    for(let stay of stays) {
        if(data.type === 'count_tour' && data.id === stay.dataset.setId){
            stay.innerHTML = data.count;
        }
    }
}

for(let block = 0; block < control_product_btns.length; block++){
    control_product_btns[block].addEventListener('click', (ev)=>{
        let cart = {
            'plus_minus': true,  // обозначаем в views.py что за фетч прилетает
        };
        if(ev.target.classList.contains('add_to_cart')){  // если нажал на плюс, то проверяем атрибут и вставляем его в cart
            if(ev.target.dataset.setId === 'Full'){
                cart['full'] = true;
            }
            else if(ev.target.dataset.setId === 'Light'){
                cart['light'] = true;
            }
            else if(ev.target.classList.contains('add_tour')){
                cart['tour_id'] = ev.target.dataset.setId;
            }
            else{
                cart['product_id'] = ev.target.dataset.setId;
            }
            cart['add'] = true;
        }
        else if(ev.target.classList.contains('remove_from_cart')){  // если нажал на минус, то проверяем атрибут и вставляем его в cart
            if(ev.target.dataset.setId === 'Full'){
                cart['full'] = true;
            }
            else if(ev.target.dataset.setId === 'Light'){
                cart['light'] = true;
            }
            else if(ev.target.classList.contains('remove_tour')){
                cart['tour_id'] = ev.target.dataset.setId;
            }
            else{
                cart['product_id'] = ev.target.dataset.setId;
            }
            cart['remove'] = true;
        }
        fetch('/cart_fetch/',{
            method: 'POST',
            headers: {'X-CSRFToken': csrf_token},
            mode: 'same-origin',
            body: JSON.stringify(cart),
            
        })
        .then(response => response.json())
        .then(result => {

            if(result['available'] && result['tours_count_max']){
                let web_socket_url = `ws://${window.location.host}/ws/socket-server/`;
                const count_tour = new WebSocket(web_socket_url);
                count_tour.onopen = function (event) {
                    // Отправляем данные после успешной установки соединения
                    count_tour.send(JSON.stringify({
                        'count': result['available']['count'],
                        'id': result['available']['id'],
                    }));
                };
                count_tour.onmessage = function (ev){
                    let data = JSON.parse(ev.data)
                    if(data.type === 'count_tour'){
                        const stay = document.querySelectorAll('.stay .stay__count')[block];  // див, где написано сколько осталось свободных мест
                        if(stay && data.id === stay.dataset.setId){
                            stay.innerHTML = data.count;
                        }
                    }
                }
            }
            let count_product = control_product_btns[block].querySelector('.count'); // див, где пишется количество чего-то
            if(result['item']['count'] !== undefined && result['item']['count'] !== 0){
                if(count_product){
                    count_product.innerHTML = result['item']['count'];  // вписываем в див количество продукта
                }
                let price_item = document.querySelectorAll('.cart .card .card_item .price_item')[block];  // цена товара
                let sum_value = document.querySelectorAll('.cart .card .card_item .sum_value')[block];  // общая сумма товара
                if(price_item && sum_value){  // может быть так, что их не будет на странице и код дальше работать не будет
                    const sum_tovar = parseInt(price_item.textContent) * result['item']['count'];  // умножаем количество на сумму одного
                    sum_value.innerHTML = sum_tovar + ' руб.';  // вписываем общую сумму за товар
                }
                if(result['available'] && result['tours_count_max']){
                    let tour_added = document.querySelector('.tour_added_cart');  // окно, когда добавил в корзину тур
                    if(tour_added){
                        tour_added.innerHTML = `<div class="text">Тур добавлен в корзину</div>
                        <a href="/cart/" class="link">Перейти в корзину</a>`
                        tour_added.style.display = 'flex';
                        const timer = setTimeout(() => {
                            tour_added.style.display = 'none'
                        }, 8000)
                    }
                }

            }
            else{
                count_product.innerHTML = '0';
                if(count_product.dataset.setName === 'product'){
                    const products = document.querySelectorAll('.cart__products .card_product');
                    for(let prod = 0; prod < products.length; prod++){
                        if(products[prod].dataset.setId === count_product.dataset.setId){
                            products[prod].style.opacity = 0;
                            const timer = setTimeout(() => {
                                products[prod].remove();
                                SumCart();
                            }, 150)

                        }
                    }
                }
                else if(count_product.dataset.setName === 'tour'){
                    const tours = document.querySelectorAll('.cart__tours .card_tour');
                    for(let prod = 0; prod < tours.length; prod++){
                        if(tours[prod].dataset.setId === count_product.dataset.setId){
                            tours[prod].style.opacity = 0;
                            const timer = setTimeout(() => {
                                tours[prod].remove();
                                SumCart();
                            }, 150)
                        }
                    }
                }
                else if(count_product.classList.contains('count_full')){
                    const full = document.querySelector('.cart .card_full');
                    full.style.opacity = 0;
                    const timer = setTimeout(() => {
                       full.remove();
                       SumCart();
                    }, 150)
                }
                else if(count_product.classList.contains('count_light')){
                    const light = document.querySelector('.cart .card_light');
                    light.style.opacity = 0;
                    const timer = setTimeout(() => {
                       light.remove();
                       SumCart();
                    }, 150)
                }
            }
            SumCart();
            CountCart();
        })
    })
}

let count_products_obj = {
    'count_products': true,  // обозначаем, что за фетч прилетает
};
function CountCart(){  // подсчитываем количество каждого товара
    fetch('/cart_fetch/', {
        method: 'POST',
        headers: {'X-CSRFToken': csrf_token},
        mode: 'same-origin',
        body: JSON.stringify(count_products_obj),
        
    })
        .then(response => response.json())
        .then(result => {
            if(result['quantity_products']['products'].length === 0 && result['quantity_products']['tours'].length === 0 && result['quantity_products']['full'] === 0 && result['quantity_products']['light'] === 0){  // если корзина пустая
                const cart = document.querySelector('.cart .cart_container');
                if(cart){
                    cart.innerHTML = '<h1 class="cart__title">В корзине ничего нет!</h1>'
                }

            }
            else{
                const count_full = document.querySelector('.count_full');  // количество наборов фул
                if (count_full) {
                    count_full.innerHTML = result['quantity_products']['full'];  // вписываем
                }
                const count_light = document.querySelector('.count_light');  // количество наборов лайт
                if (count_light) {
                    count_light.innerHTML = result['quantity_products']['light'];  // вписываем
                }
                const products_gear = document.querySelectorAll('.count');  // количество всех продуктов и товаров
                if (products_gear) {
                    for (let prod = 0; prod < result['quantity_products']['products'].length; prod++) {
                        for (let count = 0; count < products_gear.length; count++) {
                            if (products_gear[count].dataset.setId === result['quantity_products']['products'][prod]['id'] && products_gear[count].dataset.setName === 'product') {  // проверяем на айди и дополнительно проверяем на имя
                                if (result['quantity_products']['products'][prod]['count'] !== 0) {
                                    products_gear[count].innerHTML = result['quantity_products']['products'][prod]['count'];
                                }
                            }
                        }
                    }

                    for (let tour = 0; tour < result['quantity_products']['tours'].length; tour++) {
                        for (let count = 0; count < products_gear.length; count++) {
                            if (products_gear[count].dataset.setId === result['quantity_products']['tours'][tour]['id'] && products_gear[count].dataset.setName === 'tour') {// проверяем на айди и дополнительно проверяем на имя
                                products_gear[count].innerHTML = result['quantity_products']['tours'][tour]['count'];
                            }
                        }
                    }
                }
                const products = document.querySelectorAll('.cart .card');  // карточки с товарами
                for (let block = 0; block < products.length; block++) {
                    let price_item = products[block].querySelector('.card_item .price_item');  // цена товара
                    let sum_value = products[block].querySelector('.card_item .sum_value');  // общая сумма товара
                    let count_product = products[block].querySelector('.include__buttons .count');  // количество товара
                    const sum_tovar = parseInt(price_item.textContent) * Number(count_product.textContent);
                    sum_value.innerHTML = sum_tovar + ' руб.';  // вписываем общую сумму за товар
                }
                SumCart();
            }

        })
        .catch(error => console.log(error))
}
CountCart();

const cart_cards = document.querySelectorAll('.cart .card');

for(let card = 0; card < cart_cards.length; card++){ // удаление товара из корзины
    const card_delete_btn = cart_cards[card].querySelector('.cart_delete');
    card_delete_btn.addEventListener('click', ()=>{
        let card_delete_product_obj = {
            'delete_product': true,
            'id': card_delete_btn.dataset.setId,
            'name': card_delete_btn.dataset.setName,
        };

        fetch('/cart_fetch/',{
            method: 'POST',
            headers: {'X-CSRFToken': csrf_token},
            mode: 'same-origin',
            body: JSON.stringify(card_delete_product_obj),
            
        })
            .then(response => response.json())
            .then(result => {
                let web_socket_url = `ws://${window.location.host}/ws/socket-server/`;
                const count_tour = new WebSocket(web_socket_url);
                if(result['available']) {
                    count_tour.onopen = function (event) {
                    // Отправляем данные после успешной установки соединения
                    count_tour.send(JSON.stringify({
                        'count': result['available']['count'],
                        'id': result['available']['id'],
                    }));
                };
                count_tour.onmessage = function (ev){
                    let data = JSON.parse(ev.data)
                    for(let stay of stays) {
                        if(data.type === 'count_tour' && data.id === stay.dataset.setId){
                            stay.innerHTML = data.count;
                        }
                    }
                }
            }
                CountCart();
                cart_cards[card].style.opacity = 0;
                const timer = setTimeout(() => {
                    cart_cards[card].remove();
                    SumCart();
                }, 150)
            })
            .catch(error => console.log(error))

    })
}

function SumCart(){
    const common_sum_value = document.querySelector('.cart .common_sum_value'); // стоимость корзины
    const sum_values = document.querySelectorAll('.cart .card .sum_value'); // общая сумма каждого товара
    let sum = 0; // запишем сюда сумму из sum_values
    for(let val = 0; val < sum_values.length; val++){
        sum += parseInt(sum_values[val].textContent);
    }
    if(common_sum_value){
        common_sum_value.innerHTML = sum + ' руб.';
    }
    let sum_cart = {
        'summa': sum,
    }
    fetch('/cart_fetch/',{
            method: 'POST',
            headers: {'X-CSRFToken': csrf_token},
            mode: 'same-origin',
            body: JSON.stringify(sum_cart),
            
        })
        .then(response => response.json())
        .then(result => {

        })
        .catch(error => console.log(error))
}


const inputs_disabled = document.querySelectorAll('.total_info_form .inputs_disabled .form-input');

for(let inp of inputs_disabled){
    inp.setAttribute('readonly', 'true')
}

const edit_btn = document.querySelector('.data_user .edit_btn');

if(edit_btn){
    edit_btn.addEventListener('click', ()=>{
        for(let inp of inputs_disabled){
            inp.removeAttribute('readonly')
        }
        const button_submit = document.querySelector('.data_user .total_info_form .submit_button');
        button_submit.style.display = 'block';
    })
}