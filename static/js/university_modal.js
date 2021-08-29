let edit_mode;
// форма для отправки на сервер, появляющаяся по нажатию на кнопку

customElements.define('modal-page', class ModalContent extends HTMLElement {
    connectedCallback() {
        // изменения в форме в зависимости от цели использования (добавление/редактирование)
        let inputs;
        let but_name;
        let modal_title;
        let form_class = '';
        if (edit_mode === 'add_review') {
            if (typeof admin !== 'undefined') {
                inputs = `
                        <ion-item>
                            <ion-label position="floating">Имя</ion-label>
                            <ion-input id="name" name="name" placeholder="Введите ваше имя" required></ion-input>
                        </ion-item>
                        <ion-item>
                            <ion-label position="floating">Текст</ion-label>
                            <ion-textarea id="opinion" name="opinion" placeholder="Введите ваше мнение об университете" class="textarea" required></ion-textarea>
                        </ion-item>
                        <ion-item>
                            <ion-label position="floating">Оценка</ion-label>
                            <ion-input id="rating" name="rating" placeholder="Введите вашу оценку" type="number" min="0" max="5" required></ion-input>
                        </ion-item>
                `;
            } else {
                inputs = `
                        <ion-item>
                            <ion-label position="floating">Текст</ion-label>
                            <ion-textarea id="opinion" name="opinion" placeholder="Введите ваше мнение об университете" class="textarea" required></ion-textarea>
                        </ion-item>
                        <ion-item>
                            <ion-label position="floating">Оценка</ion-label>
                            <ion-input id="rating" name="rating" placeholder="Введите вашу оценку" type="number" min="0" max="5" required></ion-input>
                        </ion-item>
                `;    
            }
            form_class = 'class="review"';
            but_name = 'add-submit';
            modal_title = 'Оставить отзыв';
        }
        else if (edit_mode === 'edit_news') {
            inputs = `
                        <ion-item>
                            <ion-label position="floating">Ссылка</ion-label>
                            <ion-input id="url" name="url" placeholder="Введите ссылку на новости" required></ion-input>
                        </ion-item>
                        <ion-item>
                            <ion-label position="floating">Блок</ion-label>
                            <ion-input id="block" name="block" placeholder="Введите блок и класс новостной ячейки" required></ion-input>
                        </ion-item>
                        <ion-item>
                            <ion-label position="floating">Название</ion-label>
                            <ion-input id="title" name="title" placeholder="Введите блок и класс названия" required></ion-input>
                        </ion-item>
                        <ion-item>
                            <ion-label position="floating">Ссылка</ion-label>
                            <ion-input id="news_url" name="news_url" placeholder="Введите блок и класс ссылки" required></ion-input>
                        </ion-item>
                        <ion-item>
                            <ion-label position="floating">Картинка</ion-label>
                            <ion-input id="image" name="image" placeholder="Введите блок и класс картинки" required></ion-input>
                        </ion-item>
                        <ion-item>
                            <ion-label position="floating">Текст</ion-label>
                            <ion-input id="text" name="text" placeholder="Введите блок и класс текста" required></ion-input>
                        </ion-item>
                        <ion-item>
                            <ion-label position="floating">Дата</ion-label>
                            <ion-input id="date" name="date" placeholder="Введите блок и класс даты" required></ion-input>
                        </ion-item>
            `;
            but_name = 'edit-news-submit';
            modal_title = 'Редактирование новостей';
        }
        else if (edit_mode === 'edit_specialties') {
            inputs = ``;
            for (let i = 0; i < specialties_ids.length; i++) {
                let checked;
                if (university_specialties_ids.indexOf(specialties_ids[i]) > -1) {
                    checked = 'checked';
                } else {
                    checked = '';
                }
                let item = `
                                
                        <ion-item>
                            <ion-label>${ specialties_codes[i] } ${ specialties_names[i] }</ion-label>
                            <ion-checkbox slot="start" name="checkbox" ${checked}></ion-checkbox>
                        </ion-item>
                `;
                inputs = inputs + item;
            }
            but_name = 'edit-specialties-submit';
            modal_title = 'Редактирование специальностей';
        }
        else if (edit_mode === 'edit-budgetary_places') {
            inputs = `
                        <ion-item>
                            <ion-label position="floating">Количество бюджетных мест</ion-label>
                            <ion-input id="budgetary_places" name="budgetary_places" placeholder="Введите количество бюджетных мест" type="number" min="0" required></ion-input>
                        </ion-item>
            `;
            but_name = 'edit-budgetary_places-submit';
            modal_title = 'Редактирование бюджетных мест';
        }
        this.innerHTML = `
            <ion-header translucent>
                <ion-toolbar>
                    <ion-title class="modal-title">${modal_title}</ion-title>
                    <ion-buttons slot="end">
                        <ion-button onclick="dismissModal()">Закрыть</ion-button>
                    </ion-buttons>
                </ion-toolbar>
            </ion-header>
            <ion-content fullscreen>
                <form action="" method="post" ${form_class} enctype="multipart/form-data">
                    <input id="spec-id" name="spec-id" hidden />
                    <ion-list class="modal-list">
                    ${inputs}    
                    </ion-list>
                    <ion-item class="box">
                        <input type="submit" id="submit" class="input-button" name="${but_name}" />
                        <label for="submit" class="submit-button ion-activatable">
                            <ion-icon name="aperture-outline" slot="start" class="submit-icon"></ion-icon>
                            <span>Подтвердить</span>
                            <ion-ripple-effect class="submit-file-button-effect" slot="start"></ion-ripple-effect>
                        </label>
                    </ion-item>
                </form>
            </ion-content>
        `;
    }
});

var pause = false;

let currentModal = null;

// отображение формы по нажатию на кнопку "редактировать" в разделе новостей
const button = document.getElementById('news-edit-button');
if (button) {
    button.addEventListener('click', () => {
        edit_mode = 'edit_news';
        presentModal();
    });

    // отображение формы по нажатию на кнопку "редактировать" в разделе специальностей вуза
    const button2 = document.getElementById('specialties-edit-button');
    button2.addEventListener('click', () => {
        edit_mode = 'edit_specialties';
        presentModal();
    });
}

// отображение формы по нажатию на кнопку "добавить" в разделе отзывов
const button3 = document.getElementById('add-review');
button3.addEventListener('click', () => {
    edit_mode = 'add_review';
    presentModal();
});

// отображение формы по нажатию на одну из кнопок редактирования количества бюджетных мест
let budgetary_place
let specialty_id
const button4 = document.getElementsByClassName('edit-budgetary_places');
for (let i = 0; i < button4.length; i++) {
    button4[i].onclick = function() {
        budgetary_place = this.getAttribute("name").split('; ')[0];
        specialty_id = this.getAttribute("name").split('; ')[1];
        edit_mode = 'edit-budgetary_places';
        presentModal();
    }
}

// функция отображения формы
function presentModal() {
    const modalElement = document.createElement('ion-modal');
    modalElement.component = 'modal-page';
    modalElement.cssClass = 'my-custom-class';

    currentModal = modalElement

    document.body.appendChild(modalElement);
    return modalElement.present();
}

// функция закрытия формы
function dismissModal() {
    if (currentModal) {
        currentModal.dismiss().then(() => { currentModal = null; });
        setTimeout(() => { pause = false; }, 500);
    }
}

document.documentElement.style.setProperty('--effect-width', '210px');
let i = setInterval(function() {

    // авто заполнение полей данными из переменных
    if (document.getElementById("title")){
        if (!pause) {
            document.getElementById("url").value = url;
            document.getElementById("block").value = block;
            document.getElementById("title").value = title;
            document.getElementById("news_url").value = news_url;
            document.getElementById("image").value = image;
            document.getElementById("text").value = text;
            document.getElementById("date").value = date;
            pause = true;
        }
    }
    
    if (document.getElementById("budgetary_places")){
        if (!pause) {
            document.getElementById("spec-id").value = specialty_id;
            document.getElementById("budgetary_places").value = budgetary_place;
            pause = true;
        }
        
    }

}, 100);