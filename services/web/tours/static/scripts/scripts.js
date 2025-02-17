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

    if (! htmlLap) {
        window.location.reload();
        return
    }

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

    const lapId = evt.target.dataset.lapId;
    const requestURL = SCRIPT_ROOT.replace("-1", `${lapId}`)
    const request = new Request(requestURL);
    const response = await fetch(request);
    const  catalog = await response.json();

    const imageBox = document.querySelector("#image_box");
    imageBox.style.display = "block";
    displayPhotos(imageBox, catalog);
}

function displayPhotos(imageBox, catalog) {
    let nrPic = 4;

    while (nrPic > 0 && catalog.length > 0) {
        const pic = catalog.shift();

        const widthFactor = (pic.width > pic.height) ? 100 : pic.width / pic.height * 100
        const outerDiv = document.createElement("div");
        picName = pic.src.slice(pic.src.lastIndexOf("/") + 1);
        picId = pic.src.slice(pic.src.lastIndexOf("/") + 1, pic.src.indexOf("."));
        picId = "PIC-" + picId.replace(/_/g, "-")
        setAttributes(outerDiv, {id: picId, class: "w3-card w3-margin-top w3-border w3-border-theme w3-hover-border-theme"});
        outerDiv.style.paddingTop = "16px";
        outerDiv.style.paddingLeft = "16px";
        outerDiv.style.paddingRight = "16px";
        if (pic.type == 'image') {
            const imgRef = document.createElement("a");
            setAttributes(imgRef, {target: "_blank", href: pic.src});
            const img = document.createElement("img");
            img.setAttribute("src", pic.src);
            img.style.width = `${widthFactor}%`
            imgRef.appendChild(img);
            outerDiv.appendChild(imgRef);
        } else {
            const video = document.createElement("video");
            const width = (pic.width > pic.height) ? 640 : 640 / 16 * 9;
            const height = (pic.width > pic.height) ? 640 / 16 * 9 : 640
            setAttributes(video, {width: width, height: height, controls: true });
            const video_src = document.createElement("source");
            setAttributes(video_src, {src: pic.src, type: "video/mp4"});
            const info = document.createElement("p");
            info.textContent = 'Il browser non supporta il tag "video"';
            video.appendChild(video_src);
            video.appendChild(info);
            outerDiv.appendChild(video);
        }
        const innerDiv = document.createElement("div");
        innerDiv.setAttribute("class", "w3-container w3-center w3-padding");

        const caption = document.createElement("p");
        caption.setAttribute("class", "w3-large");
        caption.textContent = pic.caption;
        if (IS_EDITABLE) {
            const deleteRef = document.createElement("a");
            setAttributes(deleteRef, {href: "#", class: "w3-hover-theme-d3 w3-margin-left w3-right"});
            const deleteSym = document.createElement("i");
            deleteSym.setAttribute("class", "fa-solid fa-trash-can icon28");
            deleteSym.dataset.picName = picName;
            deleteSym.dataset.picId = picId;
            deleteRef.appendChild(deleteSym);
            caption.appendChild(deleteRef);
            deleteRef.addEventListener("click", delete_media);
        }

        if ( pic.lat && pic.long) {
            const mapRef = document.createElement("a");
            setAttributes(mapRef, {target: "_blank", href: pic.map, class: "w3-hover-theme-d3 w3-right"});
            const mapSym = document.createElement("i");
            mapSym.setAttribute("class", "fa-solid fa-map-location-dot icon28");
            mapRef.appendChild(mapSym);
            caption.appendChild(mapRef);
        }
        innerDiv.appendChild(caption);
        outerDiv.appendChild(innerDiv);
        imageBox.appendChild(outerDiv);
        nrPic--;
    };

    if (catalog.length > 0) {
        const moreImgDiv = document.createElement("div");
        setAttributes(moreImgDiv, {id: "more_pics", class: "w3-container w3-margin-top w3-padding w3-center"});
        const btn = document.createElement("button");
        btn.setAttribute("class", "w3-btn w3-theme w3-hover-theme")
        btn.dataset.catalog = JSON.stringify(catalog);
        btn.textContent = "Altre foto..."
        moreImgDiv.appendChild(btn);
        imageBox.appendChild(moreImgDiv);

        btn.addEventListener("click", displayMorePictures);
    };
}

function displayMorePictures(evt) {
    const catalog = JSON.parse(evt.target.dataset.catalog);
    const imageBox = document.querySelector("#image_box");

    document.querySelector("#more_pics").remove();

    displayPhotos(imageBox, catalog);
}

async function delete_media(evt) {
    console.log(evt.target.dataset.picName, evt.target.dataset.picId);
    const container = document.querySelector(`#${evt.target.dataset.picId}`);
    console.log(container);
    const requestURL = DELETE_MEDIA.replace("tbd", `${evt.target.dataset.picName}`);

    const request = new Request(requestURL);
    const response = await fetch(request);
    const  result = await response.json();

    container.style.display = "none";

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
if (bd) {
    bd.dispatchEvent(playPictures);
}
