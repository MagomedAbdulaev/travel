const list_tags = document.querySelector('.container__list'); // блок списка с тегами
const locations_content = document.querySelector('.locations__content'); // туда впишутся локации по выбранному тегу
const tag_selected = document.querySelector('.locations .tag_selected'); // туда впишется выбранный тег
const objects_all = document.querySelector('.container .objects_all');  // кнопка "все объекты"

if(list_tags){
    list_tags.addEventListener('click', (ev)=>{
    if(ev.target.classList.contains('list__item')){
        tag_selected.style.display = 'inline';
        tag_selected.innerHTML = ev.target.textContent;
        objects_all.style.display = 'block';
        let tag_obj = {
            'all': false,
            'id': ev.target.dataset.tagId,
        }
        fetch('/where_to_go_fetch/',{
                method: 'POST',
                headers: {'X-CSRFToken': csrf_token},
                mode: 'same-origin',
                body: JSON.stringify(tag_obj),
            })
        .then(response => response.json())
        .then(result => {
            let template = ``;  // шаблон для locations_content
            for(let location = 0; location < result.locations.length; location++){  // бегаем циклом по всем локациям по нажатому тегу
                let tpl = `
                    <a href="${result.locations[location]['url']}" class="locations__card" data-location-id="${result.locations[location]['tag_id']}">
                        <img src="${result.locations[location]['image']}" alt="${result.locations[location]['name']}" class="card__image">
                        <div class="card__title">${result.locations[location]['name']}</div>
                        <p class="card__description">${result.locations[location]['description']}</p>
                    </a>
                `;  // шаблон для одной локации
                template += tpl;
            }
            locations_content.innerHTML = template;
        })
        .catch(error => console.log(error))
    }
})
}

if(objects_all){
    objects_all.addEventListener('click', ()=>{
    objects_all.style.display = 'none';
    tag_selected.style.display = 'none';
    let tag_obj = {
        'id': false,
    };

    fetch('/where_to_go_fetch/',{
            method: 'POST',
            headers: {'X-CSRFToken': csrf_token},
            mode: 'same-origin',
            body: JSON.stringify(tag_obj),
        })
    .then(response => response.json())
    .then(result => {
        let template = ``;  // шаблон для locations_content
        for(let location = 0; location < result.locations.length; location++){  // бегаем циклом по всем локациям по нажатому тегу
            let tpl = `
                <a href="${result.locations[location]['url']}" class="locations__card" data-location-id="${result.locations[location]['tag_id']}">
                    <img src="${result.locations[location]['image']}" alt="${result.locations[location]['name']}" class="card__image">
                    <div class="card__title">${result.locations[location]['name']}</div>
                    <p class="card__description">${result.locations[location]['description']}</p>
                </a>
            `;  // шаблон для одной локации
            template += tpl;
        }
        locations_content.innerHTML = template;
    })
    .catch(error => console.log(error))
})
}