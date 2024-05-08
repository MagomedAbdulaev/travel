const header = document.querySelector('.header');  // шапка сайта
if(window.location.pathname !== '/'){
    header.style.background = '#000000BF';
}
const body = document.querySelector('body');
const plan_link = header.querySelector('.list__item_plan');  // планирование поездки
const sublist = plan_link.querySelector('.sublist');  // подсписок, который появляется при наведении на plan_link
let body_width = body.offsetWidth;
let plan_link_key = true;
window.addEventListener('resize', ()=>{
    body_width = body.offsetWidth;
})
if(body_width > 1024){
    plan_link.addEventListener('mouseover', () => {
        header.style.paddingBottom = '50px';
        sublist.style.visibility = 'visible';
    });

    // Изменение события mouseout на mouseleave
    plan_link.addEventListener('mouseleave', () => {
        header.style.paddingBottom = '0';
        sublist.style.visibility = 'hidden';
    });
}
else{
    const plan_link_plus = plan_link.querySelector('.plus');
    plan_link.addEventListener('click', () => {
        if(plan_link_key){
            header.style.paddingBottom = '50px';
            sublist.style.visibility = 'visible';
            plan_link_plus.style.transform = 'rotate(45deg)';
            plan_link.style.paddingBottom = '80px';
            plan_link_key = false;
        }
        else{
            plan_link_key = true;
            header.style.paddingBottom = '18px';
            plan_link_plus.style.transform = 'rotate(0deg)';
            sublist.style.visibility = 'hidden';
            plan_link.style.paddingBottom = '0';
        }

    });

}

const menu = header.querySelector('.menu');  // гамбургер
const close = header.querySelector('.close');  // закрыть гамбургер
const navigation = header.querySelector('.navigation__list');


menu.addEventListener('click', ()=>{
    body.style.overflow = 'hidden';
    window.scrollTo({
        top: 0,
    });
    menu.style.display = 'none';
    close.style.display = 'block';
    navigation.style.display = 'flex';
})

close.addEventListener('click', ()=>{
    body.style.overflow = 'auto';
    menu.style.display = 'block';
    close.style.display = 'none';
    navigation.style.display = 'none';
    header.style.paddingBottom = '18px';
})

const scroll_to_top_btn = document.querySelector('#scrollToTop');

if(scroll_to_top_btn){
    scroll_to_top_btn.addEventListener('click', ()=>{
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        })
    })
}

function ScrollToBlock(link_id, block_id){
    const link = document.querySelector(link_id);
    const block = document.querySelector(block_id);
    if (link){
        if(block){
            link.addEventListener('click', ()=>{
                window.scroll({
                    top: block.offsetTop,
                    behavior: 'smooth'
                })
            })
        }
        else{
            link.addEventListener('click', ()=>{
                link.href = `/${block_id}`;
            })
        }
    }
}
ScrollToBlock('#to_faq', '#faq');
ScrollToBlock('#to_contacts', '#contacts');
ScrollToBlock('#to_feedbacks', '#feedbacks');
ScrollToBlock('#footer_to_faq', '#faq');
ScrollToBlock('#footer_to_contacts', '#contacts');
ScrollToBlock('#footer_to_feedbacks', '#feedbacks');
ScrollToBlock('#to_contacts_group', '#contacts');


const user_icon = document.querySelector('.header .box .user');  // картинка пользователя
const register_modal = document.querySelector('.header .navigation .modal'); // окно, которое будет появляться
let user_key = true;

user_icon.addEventListener('click', ()=>{
    if(user_key){
        user_icon.style.backgroundColor = '#545454';
        register_modal.style.display = 'flex';
        user_key = false;
    }
    else{
        user_icon.style.backgroundColor = 'var(--green-color)';
        register_modal.style.display = 'none';
        user_key = true;
    }

})



const login_btn = document.querySelector('.header .navigation .modal .enter_btn');  // кнопка "войти"
const form_login = document.querySelector('.form_login');   // форма авторизации
const register_btn = document.querySelector('.header .navigation .modal .register_btn'); // кнопка "регистрация"
const form_register = document.querySelector('.form_register');   // форма регистрации
const form_close = document.querySelectorAll('.form-user__close');   // закрыть форму кнопка
const form_reset_password = document.querySelector('.form_forget_password');

if(login_btn){
    login_btn.addEventListener('click', ()=>{
    form_login.style.display = 'block';
    form_register.style.display = 'none';
    form_reset_password.style.display = 'none';
    user_icon.click();
    user_icon.style.backgroundColor = '#545454';
    body.style.overflow = 'hidden';
})
}
if(register_btn){
    register_btn.addEventListener('click', ()=>{
        form_register.style.display = 'block';
        form_login.style.display = 'none';
        form_reset_password.style.display = 'none';
        user_icon.click();
        user_icon.style.backgroundColor = '#545454';
        body.style.overflow = 'hidden';
    })
}
for(let close = 0; close < form_close.length; close++){
    form_close[close].addEventListener('click', ()=>{
        form_register.style.display = 'none';
        form_login.style.display = 'none';
        form_reset_password.style.display = 'none';
        body.style.overflow = 'auto';
        user_icon.click();
    })
}

const phone_input_register = document.querySelectorAll('.phone-input-register');

if(phone_input_register){
    for(let i = 0; i < phone_input_register.length; i++){
        phone_input_register[i].addEventListener('input', ()=>{
            let value_current = phone_input_register[i].value.slice(2);
            phone_input_register[i].value = '+7' + value_current;
        })
    }
}

const reset_password_btn = document.querySelector('.forget_password_btn');

reset_password_btn.addEventListener('click', ()=>{
    form_reset_password.style.display = 'block';
    form_register.style.display = 'none';
    form_login.style.display = 'none';
})



window.addEventListener('load', () => {
    const formErrorRegister = document.querySelector('.form_register .form-error .errorlist li');
    const formErrorLogin = document.querySelector('.form_login .form-error .errorlist li');
    const formErrorReset = document.querySelector('.form_forget_password .form-error .errorlist li');
    if (formErrorRegister && formErrorRegister.innerHTML !== 'Обязательное поле.') {
        user_icon.click();
        register_btn.click();
    }

    else if (formErrorLogin && formErrorLogin.innerHTML !== 'Обязательное поле.') {
        user_icon.click();
        login_btn.click();
    }

    else if (formErrorReset && formErrorReset.innerHTML !== 'Обязательное поле.') {
        reset_password_btn.click();
    }

});

const register_form = document.querySelector('.form_register .form-user__container .form');
const messages_register_form = document.querySelector('.form_register .form-user__container .messages');

if(messages_register_form){
    user_icon.click();
    register_btn.click();
    register_form.style.display = 'none';
    const email_message_active = document.querySelector('.form_register .email_message_active');
    email_message_active.style.display = 'block';
}


const reset_form = document.querySelector('.form_forget_password .form-user__container .form');
const messages_reset_form = document.querySelector('.form_forget_password .form-user__container .messages');

if(messages_reset_form){
    user_icon.click();
    reset_password_btn.click();
    reset_form.style.display = 'none';
    const form_forget_password__title = document.querySelector('.form_forget_password .form-user__title');
    form_forget_password__title.innerHTML = 'Успех!';
    const message = document.querySelector('.form_forget_password .email_message_active');
    message.style.display = 'block';
    const email_message_active_container = document.querySelector('.form_forget_password .email_message_active_container');
    email_message_active_container.style.border = 'none';
    const form_forget_password__data = document.querySelector('.form_forget_password .form_forget_password__data');
    form_forget_password__data.style.display = 'none';
}

const close_message_email = document.querySelectorAll('.form-user .close_message_email');

for(let close = 0; close < close_message_email.length; close++){
    close_message_email[close].addEventListener('click', ()=>{
        form_register.style.display = 'none';
        form_login.style.display = 'none';
        form_reset_password.style.display = 'none';
        body.style.overflow = 'auto';
        user_icon.click();
    })
}