const question_btn_all = document.querySelector('.questions .all');  // кнопка развернуть все
const question_buttons_block = document.querySelector('.questions__list');  // блок с вопросами
const question_buttons = document.querySelectorAll('.questions__list .list__item_question');  // кнопки-вопросы
const question_answer = document.querySelector('.questions .answer');  // ответ на вопрос блок
const couple_image = document.querySelector('.questions .couple__image');


if(question_btn_all){
    question_btn_all.addEventListener('click',()=>{
        for(let btn = 0; btn < question_buttons.length; btn++){
            question_btn_all.style.display = 'none';
            question_buttons[btn].style.display = 'block';
        }
    })
}

if(question_buttons_block){

    question_buttons_block.addEventListener('click', (ev)=>{
        if(ev.target.classList.contains('list__item_question')){
            let question_close = ev.target.querySelector('.question_close');
            question_close.style.display = 'block';
            for(let btn = 0; btn < question_buttons.length; btn++){
                question_buttons[btn].style.display = 'none';
            }
            ev.target.style.display = 'block';
            ev.target.classList.add('question_active');
            question_answer.style.display = 'block';
            question_btn_all.style.display = 'none';
            if(body.offsetWidth + 25 < 1800){
                couple_image.style.display = 'none';
            }
            let question_answer_text = question_answer.querySelector('.answer__text');
            let question_answer_obj = {
                'id': ev.target.dataset.questionId,
            }
            fetch('/question_description_fetch/',{
                    method: 'POST',
                    headers: {'X-CSRFToken': csrf_token},
                    mode: 'same-origin',
                    body: JSON.stringify(question_answer_obj),
                })
            .then(response => response.json())
            .then(result => {
                question_answer_text.innerHTML = result.description
            })
            .catch(error => console.log(error))
            question_close.addEventListener('click', ()=>{
                question_close.style.display = 'none';
                ev.target.classList.remove('question_active');
                question_answer.style.display = 'none';
                couple_image.style.display = 'block';
                for(let btn = 0; btn < question_buttons.length; btn++){
                    question_buttons[btn].style.display = 'block';
                }
            })
        }
    })

}

