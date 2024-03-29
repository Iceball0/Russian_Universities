// форма для отправки на сервер, появляющаяся по нажатию на кнопку

customElements.define('modal-page', class ModalContent extends HTMLElement {
    connectedCallback() {
        // изменения в форме в зависимости от цели использования (добавление/редактирование)
        let mod_title;
        let but_name;
        let required;
        if (edit_mode === 'add') {
            mod_title = 'Добавление вуза';
            but_name = 'add-submit';
            required = 'required';
        }
        else {
            mod_title = 'Редактирование вуза';
            but_name = 'edit-submit';
            required = '';
        }
        this.innerHTML = `
            <ion-header translucent>
                <ion-toolbar>
                    <ion-title class="modal-title">${mod_title}</ion-title>
                    <ion-buttons slot="end">
                        <ion-button onclick="dismissModal()">Закрыть</ion-button>
                    </ion-buttons>
                </ion-toolbar>
            </ion-header>
            <ion-content fullscreen>
                <form action="" method="post" enctype="multipart/form-data">
                    <input id="univ-id" name="univ-id" hidden />
                    <ion-list class="modal-list">
                        <ion-item>
                            <ion-label position="floating">Название</ion-label>
                            <ion-input id="title" name="title" placeholder="Введите название" required></ion-input>
                        </ion-item>
                        <ion-item>
                            <ion-label position="floating">Город</ion-label>
                            <ion-input id="city" name="city" placeholder="Введите город" required></ion-input>
                        </ion-item>
                        <ion-item>
                            <ion-label position="floating">Топ в России</ion-label>
                            <ion-input id="TopInRussia" name="TopInRussia" placeholder="Введите место по России" type="number" min="0" required></ion-input>
                        </ion-item>
                        <ion-item>
                            <ion-label position="floating">Описание</ion-label>
                            <ion-textarea id="description" name="description" placeholder="Введите описание" class="textarea" required></ion-textarea>
                        </ion-item>
                    </ion-list>
                    <ion-item class="box">
                        <input type="file" id="file-load" class="input-button" name="photo" ${required} />
                        <label for="file-load" class="file-label ion-activatable">
                            <ion-icon name="cloud-upload-outline" slot="start"></ion-icon>
                            <span id="file-load-text">Загрузить файл&hellip;</span>
                            <ion-ripple-effect class="upload-file-button-effect" slot="start"></ion-ripple-effect>
                        </label>
                    </ion-item>
                    <ion-item class="box">
                        <input type="submit" id="submit" class="input-button" name="${but_name}"/>
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

var edit_mode = 'edit';
var pause = false;

let currentModal = null;

// отображение формы по нажатию на кнопку "добавить"
const button = document.getElementsByClassName('add-button')[0]
button.addEventListener('click', () => {
    edit_mode = 'add';
    presentModal();
});

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

// значения для авто заполнения полей по умолчанию

let id = '';
let title = '';
let city = '';
let TopInRussia = '';
let description = '';

// отображение формы по нажатию на одну из кнопок "редактировать" и определение нажатой кнопки

const edit_buttons = document.getElementsByClassName('edit-button');
for (let j = 0; j < edit_buttons.length; j++) {

    edit_buttons[j].onclick = function() {

        // значения для авто заполнения в зависимости от нажатой кнопки
        id = ids[this.getAttribute("name") - 1];
        title = titles[this.getAttribute("name") - 1];
        city = cities[this.getAttribute("name") - 1];
        TopInRussia = TopsInRussia[this.getAttribute("name") - 1];
        description = descriptions[this.getAttribute("name") - 1];
        edit_mode = 'edit';
        presentModal();

    }

}

document.documentElement.style.setProperty('--effect-width', '210px');
let i = setInterval(function() {

    // гибкое изменение ширины кнопки "загрузка фото" в зависимости от названия выбранного файла 
    if (document.getElementById("file-load")){
        document.getElementById("file-load").onchange = function () {
            document.getElementById("file-load-text").textContent = this.files[0].name;
            document.documentElement.style.setProperty('--effect-width', String(document.getElementsByClassName('file-label')[0].offsetWidth) + 'px');
        };
    }

     // авто заполнение полей и обнуление данных в переменных
    if (document.getElementById("title")){
        if (!pause) {
            document.getElementById("univ-id").value = id;
            document.getElementById("title").value = title;
            document.getElementById("city").value = city;
            document.getElementById("TopInRussia").value = TopInRussia;
            document.getElementById("description").value = description;
            id = '';
            title = '';
            city = '';
            TopInRussia = '';
            description = '';
            pause = true;
        }
    }

}, 100);