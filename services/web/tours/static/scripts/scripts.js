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
    const lapId = evt.target.dataset.lapId;

    const requestURL = `${SCRIPT_ROOT.slice(0, -5)}/${lapId}/js`;
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
    const photo_show = document.querySelector("#photo_show")

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

    const requestURL = `${SCRIPT_ROOT.slice(0, -5)}/${hotelId}/js`;
    console.log(`${SCRIPT_ROOT.slice(0, -5)}`)
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

//function populateHeaderHotel(hotel, outerDiv) {
//    const header = document.createElement("header");
//
//    const div1 = document.createElement("div");
//    div1.setAttribute("class", "w3-row");
//    const divImg = document.createElement("div");
//    divImg.setAttribute("class", "w3-container w3-quarter 3w-mobile");
//    const hotelImg = document.createElement("img");
//    setAttributes(hotelImg, {src: hotel.this_hotel.photo, class: "w3-margin-left w3-margin-top webp"});
//    divImg.appendChild(hotelImg)
//    const divTitle = document.createElement("div");
//    divTitle.setAttribute("class", "w3-container w3-threequarter 3w-mobile");
//    const h2 = document.createElement("h2");
//    h2.textContent = hotel.this_hotel.name;
//    h2.setAttribute("class", "w3-center w3-padding-64");
//    divTitle.appendChild(h2);
//    div1.appendChild(divImg);
//    div1.appendChild(divTitle);
//    header.appendChild(div1);
//    outerDiv.appendChild(header);
//}
//
//function populateHotel(hotel, outerDiv) {
//    const myArticle = document.createElement("article");
//    myArticle.style.margin = "60px 5% 0 5%";
//
//    const div1 = document.createElement("div");
//    div1.setAttribute("class", "row w3-row");
//    const divLabel1 =document.createElement("div");
//    divLabel1.setAttribute("class", "w3-container w3-col m4 3w-mobile");
//    const paraLabel1 = document.createElement("p");
//    paraLabel1.setAttribute("class", "w3-left-align wbold");
//    paraLabel1.textContent = "Indirizzo:";
//    const divData1 = document.createElement("div");
//    divData1.setAttribute("class", "w3-container w3-col m7 w3-mobile");
//    const paraInfo1 = document.createElement("p");
//    paraInfo1.setAttribute("class", "w3-left-align");
//    paraInfo1.textContent = hotel.this_hotel.address;
//    divData1.appendChild(paraInfo1);
//    divLabel1.appendChild(paraLabel1);
//    div1.appendChild(divLabel1);
//    div1.appendChild(divData1);
//    if (hotel.this_hotel.coord) {
//        const divData1_1 = document.createElement("div")
//        divData1_1.setAttribute("class", "w3-container w3-col m1 w3-mobile");
//        const paraInfo1_1 = document.createElement("p");
//        paraInfo1_1.setAttribute("class", "w3-left-align");
//        const a1 = document.createElement("a");
//        setAttributes(a1, {href: `geo:0.0?q=${hotel.this_hotel.coord.latitude},${hotel.this_hotel.coord.longitude}`, class: "w3-hover-theme-d3 w3-right"});
//        a1.textContent = "Mappa";
//        paraInfo1_1.appendChild(a1);
//        divData1_1.appendChild(paraInfo1_1);
//        div1.appendChild(divData1_1)
//    };
//    myArticle.appendChild(div1);
//
//    const div2 = document.createElement("div");
//    div2.setAttribute("class", "row w3-row");
//    const divLabel2 =document.createElement("div");
//    divLabel2.setAttribute("class", "w3-container w3-third 3w-mobile");
//    const paraLabel2 = document.createElement("p");
//    paraLabel2.setAttribute("class", "w3-left-align wbold");
//    paraLabel2.textContent = "Città:";
//    const divData2 = document.createElement("div");
//    divData2.setAttribute("class", "w3-container w3-twothird w3-mobile");
//    const paraInfo2 = document.createElement("p");
//    paraInfo2.setAttribute("class", "w3-left-align");
//    paraInfo2.textContent = hotel.this_hotel.town;
//    divData2.appendChild(paraInfo2);
//    divLabel2.appendChild(paraLabel2);
//    div2.appendChild(divLabel2);
//    div2.appendChild(divData2);
//    myArticle.appendChild(div2);
//
//    if (hotel.this_hotel.phone) {
//        const div14 = document.createElement("div");
//        div14.setAttribute("class", "row w3-row");
//        const divLabel14 =document.createElement("div");
//        divLabel14.setAttribute("class", "w3-container w3-third 3w-mobile");
//        const paraLabel14 = document.createElement("p");
//        paraLabel14.setAttribute("class", "w3-left-align wbold");
//        paraLabel14.textContent = "Telefono:";
//        const divData14 = document.createElement("div");
//        divData14.setAttribute("class", "w3-container w3-twothird w3-mobile");
//        const paraInfo14 = document.createElement("p");
//        paraInfo14.setAttribute("class", "w3-left-align");
//        const a14 = document.createElement("a");
//        a14.setAttribute("href", `tel:hotel.this_hotelhref_phone`);
//        a14.textContent = hotel.this_hotel.phone;
//        paraInfo14.appendChild(a14);
//        divData14.appendChild(paraInfo14)
//        divLabel14.appendChild(paraLabel14);
//        div14.appendChild(divLabel14);
//        div14.appendChild(divData14);
//        myArticle.appendChild(div14);
//    };
//
//    if (hotel.this_hotel.email) {
//        const div15 = document.createElement("div");
//        div15.setAttribute("class", "row w3-row");
//        const divLabel15 =document.createElement("div");
//        divLabel15.setAttribute("class", "w3-container w3-third 3w-mobile");
//        const paraLabel15 = document.createElement("p");
//        paraLabel15.setAttribute("class", "w3-left-align wbold");
//        paraLabel15.textContent = "E-mail:";
//        const divData15 = document.createElement("div");
//        divData15.setAttribute("class", "w3-container w3-twothird w3-mobile");
//        const paraInfo15 = document.createElement("p");
//        paraInfo15.setAttribute("class", "w3-left-align");
//        paraInfo15.textContent = hotel.this_hotel.email;
//        divData15.appendChild(paraInfo15)
//        divLabel15.appendChild(paraLabel15);
//        div15.appendChild(divLabel15);
//        div15.appendChild(divData15);
//        myArticle.appendChild(div15);
//    };
//
//    if (hotel.this_hotel.check_in) {
//        const div4 = document.createElement("div");
//        div4.setAttribute("class", "row w3-row");
//        const divLabel4 =document.createElement("div");
//        divLabel4.setAttribute("class", "w3-container w3-third 3w-mobile");
//        const paraLabel4 = document.createElement("p");
//        paraLabel4.setAttribute("class", "w3-left-align wbold");
//        paraLabel4.textContent = "Check-in:";
//        const divData4 = document.createElement("div");
//        divData4.setAttribute("class", "w3-container w3-twothird w3-mobile");
//        const paraInfo4 = document.createElement("p");
//        paraInfo4.setAttribute("class", "w3-left-align");
//        paraInfo4.textContent = hotel.this_hotel.check_in;
//        divData4.appendChild(paraInfo4);
//        divLabel4.appendChild(paraLabel4);
//        div4.appendChild(divLabel4);
//        div4.appendChild(divData4);
//        myArticle.appendChild(div4);
//    };
//
//
//
//    const div3 = document.createElement("div");
//    div3.setAttribute("class", "row w3-row");
//    const divLabel3 =document.createElement("div");
//    divLabel3.setAttribute("class", "w3-container w3-third 3w-mobile");
//    const paraLabel3 = document.createElement("p");
//    paraLabel3.setAttribute("class", "w3-left-align wbold");
//    paraLabel3.textContent = "Prenotazione:";
//    const divData3 = document.createElement("div");
//    divData3.setAttribute("class", "w3-container w3-twothird w3-mobile");
//    const paraInfo3 = document.createElement("p");
//    if (hotel.this_hotel.reserved) {
//        paraInfo3.setAttribute("class", "w3-left-align");
//        const span = document.createElement("i");
//        span.setAttribute("class", "fa-solid fa-check done");
//        paraInfo3.appendChild(span);
//    }
//    divData3.appendChild(paraInfo3);
//    divLabel3.appendChild(paraLabel3);
//    div3.appendChild(divLabel3);
//    div3.appendChild(divData3);
//    myArticle.appendChild(div3);
//
//    if (hotel.this_hotel.check_in) {
//        const div4 = document.createElement("div");
//        div4.setAttribute("class", "row w3-row");
//        const divLabel4 =document.createElement("div");
//        divLabel4.setAttribute("class", "w3-container w3-third 3w-mobile");
//        const paraLabel4 = document.createElement("p");
//        paraLabel4.setAttribute("class", "w3-left-align wbold");
//        paraLabel4.textContent = "Check-in:";
//        const divData4 = document.createElement("div");
//        divData4.setAttribute("class", "w3-container w3-twothird w3-mobile");
//        const paraInfo4 = document.createElement("p");
//        paraInfo4.setAttribute("class", "w3-left-align");
//        paraInfo4.textContent = hotel.this_hotel.check_in;
//        divData4.appendChild(paraInfo4);
//        divLabel4.appendChild(paraLabel4);
//        div4.appendChild(divLabel4);
//        div4.appendChild(divData4);
//        myArticle.appendChild(div4);
//    };
//
//    if (hotel.this_hotel.check_out) {
//        const div5 = document.createElement("div");
//        div5.setAttribute("class", "row w3-row");
//        const divLabel5 =document.createElement("div");
//        divLabel5.setAttribute("class", "w3-container w3-third 3w-mobile");
//        const paraLabel5 = document.createElement("p");
//        paraLabel5.setAttribute("class", "w3-left-align wbold");
//        paraLabel5.textContent = "Check-out:";
//        const divData5 = document.createElement("div");
//        divData5.setAttribute("class", "w3-container w3-twothird w3-mobile");
//        const paraInfo5 = document.createElement("p");
//        paraInfo5.setAttribute("class", "w3-left-align");
//        paraInfo5.textContent = hotel.this_hotel.check_out;
//        divData5.appendChild(paraInfo5);
//        divLabel5.appendChild(paraLabel5);
//        div5.appendChild(divLabel5);
//        div5.appendChild(divData5);
//        myArticle.appendChild(div5);
//    }
//
//    if (hotel.this_hotel.price) {
//        const div6 = document.createElement("div");
//        div6.setAttribute("class", "row w3-row");
//        const divLabel6 =document.createElement("div");
//        divLabel6.setAttribute("class", "w3-container w3-third 3w-mobile");
//        const paraLabel6 = document.createElement("p");
//        paraLabel6.setAttribute("class", "w3-left-align wbold");
//        paraLabel6.textContent = "Costo:";
//        const divData6 = document.createElement("div");
//        divData6.setAttribute("class", "w3-container w3-twothird w3-mobile");
//        const paraInfo6 = document.createElement("p");
//        paraInfo6.setAttribute("class", "w3-left-align");
//        paraInfo6.textContent = `€ ${hotel.this_hotel.price}`;
//        divData6.appendChild(paraInfo6);
//        divLabel6.appendChild(paraLabel6);
//        div6.appendChild(divLabel6);
//        div6.appendChild(divData6);
//        myArticle.appendChild(div6);
//    }
//
//    if (hotel.this_hotel.tappa) {
//        const div7 = document.createElement("div");
//        div7.setAttribute("class", "row w3-row");
//        const divLabel7 =document.createElement("div");
//        divLabel7.setAttribute("class", "w3-container w3-third 3w-mobile");
//        const paraLabel7 = document.createElement("p");
//        paraLabel7.setAttribute("class", "w3-left-align wbold");
//        paraLabel7.textContent = "Tappa:";
//        const divData7 = document.createElement("div");
//        divData7.setAttribute("class", "w3-container w3-twothird w3-mobile");
//        const paraInfo7 = document.createElement("p");
//        paraInfo7.setAttribute("class", "w3-left-align");
//        const a7 = document.createElement("a");
//        a7.setAttribute("href", hotel.this_hotel.tappa.URL);
//        a7.textContent = `${hotel.this_hotel.tappa.start} - ${hotel.this_hotel.tappa.destination}`;
//        paraInfo7.appendChild(a7);
//        divData7.appendChild(paraInfo7);
//        divLabel7.appendChild(paraLabel7);
//        div7.appendChild(divLabel7);
//        div7.appendChild(divData7);
//        myArticle.appendChild(div7);
//    }
//
//    if (hotel.this_hotel.link) {
//        const div7 = document.createElement("div");
//        div7.setAttribute("class", "row w3-row");
//        const divLabel7 =document.createElement("div");
//        divLabel7.setAttribute("class", "w3-container w3-third 3w-mobile");
//        const paraLabel7 = document.createElement("p");
//        paraLabel7.setAttribute("class", "w3-left-align wbold");
//        paraLabel7.textContent = "Sito web:";
//        const divData7 = document.createElement("div");
//        divData7.setAttribute("class", "w3-container w3-twothird w3-mobile");
//        const paraInfo7 = document.createElement("p");
//        paraInfo7.setAttribute("class", "w3-left-align");
//        const a7 = document.createElement("a");
//        setAttributes(a7, {href: hotel.this_hotel.link, target:"_blank"});
//        a7.textContent = hotel.this_hotel.name;
//        paraInfo7.appendChild(a7);
//        divData7.appendChild(paraInfo7);
//        divLabel7.appendChild(paraLabel7);
//        div7.appendChild(divLabel7);
//        div7.appendChild(divData7);
//        myArticle.appendChild(div7);
//    }
//    if (Object.hasOwn(session, '_user_id')) {
//        const div12 = document.createElement("div");
//        div12.setAttribute("class", "w3-container w3-center");
//        div12.style.marginTop = "60px";
//        const div13 = document.createElement("div");
//        div13.setAttribute("class", "w3-bar");
//        const a12 = document.createElement("a");
//        setAttributes(a12, {href: hotel.this_hotel.update, class: "w3-bar-item w3-ripple", title: "Modifica questo hotel"})
//        const span12 = document.createElement("i");
//        span12.setAttribute("class", "fa-solid fa-pencil icon28");
//        const a13 = document.createElement("a");
//        setAttributes(a13, {href: hotel.this_hotel.delete, class: "w3-bar-item w3-ripple", title: "Cancella questo hotel"})
//        const span13 = document.createElement("i");
//        span13.setAttribute("class", "fa-solid fa-trash-can icon28");
//        a13.appendChild(span13);
//        a12.appendChild(span12);
//        div13.appendChild(a12);
//        div13.appendChild(a13);
//        div12.appendChild(div13);
//        myArticle.appendChild(div12);
//    }
//    outerDiv.appendChild(myArticle);
//}


const buttons = document.querySelectorAll("button");
console.log(buttons)

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

const photo_show = document.querySelector("#photo_show")
if (photo_show) {
    photo_show.addEventListner("click", lapPicturesShow)
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

const dd_btn = document.querySelector("#dd_btn");
if (dd_btn) {
    dd_btn.addEventListener("click", dropDown);
}

const ddButtons = document.querySelectorAll("button[data-lang]");
ddButtons.forEach((ddButton) => ddButton.addEventListener("click", selectLanguage));

const openNav = document.querySelector("#open_nav")
openNav.addEventListener("click", toggleMenu)

const openList = document.querySelector("#open_list")
if (open_list) {
    openList.addEventListener("click", toggleList)
}
