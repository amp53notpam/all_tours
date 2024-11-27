function toggleMenu() {
    let menu = document.querySelector("#menu");
    if (menu.className.indexOf("w3-show") == -1) {
        menu.className += " w3-show";
    } else {
        menu.className = menu.className.replace(" w3-show", "");
    }
}

function toggleList() {
    if (document.querySelector("#sidebar").style.display === "block") {
        closeMenu()
    } else {
        openMenu()
    }
}

function openMenu() {
    document.querySelector("#sidebar").style.width = "50%";
    document.querySelector("#sidebar").style.display = "block";
}

function closeMenu() {
    document.querySelector("#sidebar").style.width = "25%";
    document.querySelector("#sidebar").style.display = "none";
}

function dropDown() {
    const menu = document.querySelector("#dd_menu");
    const caret = document.querySelector("#dd_caret");
    if (menu.className.indexOf("w3-show") == -1) {
        menu.className += " w3-show";
        caret.className = caret.className.replace("fa-caret-down", "fa-caret-up");
    } else {
        menu.className = menu.className.replace(" w3-show", "");
        caret.className = caret.className.replace("fa-caret-up", "fa-caret-down");
    }
}

function setAttributes(el, attrs) {
    Object.keys(attrs).forEach(key => el.setAttribute(key, attrs[key]));
}

async function selectLanguage(evt) {
    const sel_lang = evt.target.dataset.lang;
    const dd_btn = document.querySelector("#dd_btn");
    const cur_lang = dd_btn.dataset.curLang;

    if (cur_lang == sel_lang) {
        dropDown()
    } else {
        const requestURL = `${LANG_ROOT.slice(0, -1)}/${sel_lang}`
        const request = new Request(requestURL)
        const response = await fetch(request);
        const res = await response.text();
        location.replace(location.href)
    }
}

async function openLap(evt) {
    if (document.querySelector("#summary")) {
        document.querySelector("#summary").style.display = "none";
    }

    if (document.querySelector("#lap")) {
        document.querySelector("#lap").remove()
    }

    const display = document.querySelector("#display");
    const lapId = evt.currentTarget.dataset.lapId;


    const requestURL = `${SCRIPT_ROOT.slice(0, -6)}/${lapId}/js`;

    const request = new Request(requestURL);
    const response = await fetch(request);
    const htmlLap = await response.text();
    console.log(htmlLap)

    const lap = document.createElement('div')
    setAttributes(lap, {id: "lap", class: "w3-container w3-center tappa"})
    lap.style.display = 'block'
    lap.innerHTML = htmlLap

    display.appendChild(lap);
    const info_prev = document.querySelector("#info_prev");
    if (info_prev) {
        info_prev.addEventListener("click", openLap);
    };
    const info_next = document.querySelector("#info_next");
    if (info_next) {
        info_next.addEventListener("click", openLap);
    };
    const photos = document.querySelector("#photos");
    if (photos) {
        photos.addEventListener("click", displayLapPictures);
    };

    const tablinks = document.querySelectorAll(".tablink");
    for (const tablink of tablinks) {
        tablink.className = tablink.className.replace(" w3-theme-d2", "");
    }

    evt.target.className += " w3-theme-d2";

    closeMenu()
}

async function openHotel(evt) {
    if (document.querySelector("#summary")) {
        document.querySelector("#summary").style.display = "none";
    }

    if (document.querySelector("#hotel")) {
        document.querySelector("#hotel").remove()
    }

    console.log("running openHotel")

    const display = document.querySelector("#display");
    const hotelId = evt.target.dataset.hotelId;

    const requestURL = `${SCRIPT_ROOT.slice(0, -6)}/${hotelId}/js`;
    console.log(`${SCRIPT_ROOT.slice(0, -6)}`)
    console.log(requestURL)
    const request = new Request(requestURL);
    const response = await fetch(request);
    const htmlHotel = await response.text();
    console.log(htmlHotel)

    const hotel = document.createElement("div");
    setAttributes(hotel, {id: "hotel", class: "w3-container w3-center albergo"});
    hotel.style.display = "block";
    hotel.innerHTML = htmlHotel

    display.appendChild(hotel);

    const tablinks = document.querySelectorAll(".tablink");
    for (const tablink of tablinks) {
        tablink.className = tablink.className.replace(" w3-theme-d2", "");
    }

    evt.target.className += " w3-theme-d2";

    closeMenu()
}

async function displayLapPictures(evt) {
    console.log("executing displayLapPictures")

    const lapId = evt.target.dataset.lapId;
    const requestURL = SCRIPT_ROOT.replace("-1", `${lapId}`)
    const request = new Request(requestURL);
    const response = await fetch(request);
    const  catalog = await response.json();
    console.log(catalog);

//    display_photos(catalog)
}

function display_photos(catalog) {
    let nrPic = 4;
    let img;
    while (nrPic > 0 && catalog.length > 0) {
        img = catalog.shift();

        nrPic--;
        console.log(img);
    }
}

const buttons = document.querySelectorAll("button");

buttons.forEach((button) => {
    if (button.dataset.lapId) {
       // button.addEventListener("click", openLap);
       button.addEventListener("click", openLap);
    } else if (button.dataset.hotelId) {
       button.addEventListener("click", openHotel);
    }
})

const info_prev = document.querySelector("#info_prev");
if (info_prev) {
    info_prev.addEventListener("click", openLap);
};
const info_next = document.querySelector("#info_next");
if (info_next) {
    info_next.addEventListener("click", openLap);
};
const photos = document.querySelector("#photos");
if (photos) {
    photos.addEventListener("click", displayLapPictures);
};

const dd_btn = document.querySelector("#dd_btn");
if (dd_btn) {
    dd_btn.addEventListener("click", dropDown);
};

const ddButtons = document.querySelectorAll("button[data-lang]");
ddButtons.forEach((ddButton) => ddButton.addEventListener("click", selectLanguage));

const openNav = document.querySelector("#open_nav")
if  (openNav) {
    openNav.addEventListener("click", toggleMenu)
}

const openList = document.querySelector("#open_list")
if (openList) {
    openList.addEventListener("click", toggleList)
};

const playPictures = new Event ("picShow")

console.log(document.readyState)
const bd = document.querySelector("#album")
if (bd) {
    bd.addEventListener("picShow", displayLapPictures);
}

bd.dispatchEvent(playPictures);