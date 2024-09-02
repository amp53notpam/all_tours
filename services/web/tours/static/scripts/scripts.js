/*
function openHotel(evt) {
  document.querySelector("#summary").style.display = "none";

  const hotels = document.querySelectorAll(".albergo");
  hotels.forEach((hotel) => {
    hotel.style.display = "none";
  });
  const tablinks = document.querySelectorAll(".tablink");
  tablinks.forEach((tablink) => {
    tablink.className = tablink.className.replace(" w3-theme-d2", "");
  });

  document.querySelector(`#hotel_${evt.target.dataset.hotelId}`).style.display = "block";
  evt.currentTarget.className += " w3-theme-d2";

  closeMenu()
}
*/

function toggleMenu() {
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

async function openLap(evt) {
  if (document.querySelector("#summary")) {
    document.querySelector("#summary").style.display = "none";
  }

  const display = document.querySelector("#display");

  const lapId = evt.target.dataset.lapId;

  const requestURL =
    `${SCRIPT_ROOT.slice(0, -3)}/${lapId}`;
  console.log(requestURL);
  const request = new Request(requestURL);

  const response = await fetch(request);
  const lapText = await response.text();
  console.log(lapText);

  const lap = JSON.parse(lapText);

  // remove the previous lap, if any

  if (document.querySelector("#lap")) {
    document.querySelector("#lap").remove()
  }

  const outerDiv = document.createElement("div");
  setAttributes(outerDiv, {id: "lap", class: "w3-container w3-center tappa"})
  outerDiv.style.display = "block";

  populateHeaderLap(lap, outerDiv);
  populateLap(lap, outerDiv);

  display.appendChild(outerDiv);

  const tablinks = document.querySelectorAll(".tablink");
  for (const tablink of tablinks) {
    tablink.className = tablink.className.replace(" w3-theme-d2", "");
  }

  document.querySelector(`#btn_${lapId}`).className += " w3-theme-d2";

  closeMenu()
}

function populateHeaderLap(lap, outerDiv) {
    const header = document.createElement("header");
    const innerDiv = document.createElement("div");
    innerDiv.setAttribute("class", "w3-display-container");
    innerDiv.style.height = "200px";
    const h2 = document.createElement("h2");
    h2.textContent = `${lap.this_lap.start} - ${lap.this_lap.destination}`;
    h2.setAttribute("class", "w3-display-middle");
    innerDiv.appendChild(h2);
    header.appendChild(innerDiv);
    outerDiv.appendChild(header);
}

function populateLap(lap, outerDiv) {
    const myArticle = document.createElement("article");
    myArticle.style.margin = "0 5% 0 5%";

    const div1 = document.createElement("div");
    div1.setAttribute("class", "row w3-row");
    const divLabel1 =document.createElement("div");
    divLabel1.setAttribute("class", "w3-container w3-third 3w-mobile");
    const paraLabel1 = document.createElement("p");
    paraLabel1.setAttribute("class", "w3-left-align wbold");
    paraLabel1.textContent = "Data:";
    const divData1 = document.createElement("div");
    divData1.setAttribute("class", "w3-container w3-twothird w3-mobile");
    const paraInfo1 = document.createElement("p");
    paraInfo1.setAttribute("class", "w3-left-align");
    paraInfo1.textContent = lap.this_lap.date;

    divData1.appendChild(paraInfo1);
    divLabel1.appendChild(paraLabel1);
    div1.appendChild(divLabel1);
    div1.appendChild(divData1);
    myArticle.appendChild(div1);

    if (lap.this_lap.distance) {
        const div2 = document.createElement("div");
        div2.setAttribute("class", "row w3-row");
        const divLabel2 =document.createElement("div");
        divLabel2.setAttribute("class", "w3-container w3-third 3w-mobile");
        const paraLabel2 = document.createElement("p");
        paraLabel2.setAttribute("class", "w3-left-align wbold");
        paraLabel2.textContent = "Distanza:";
        const divData2 = document.createElement("div");
        divData2.setAttribute("class", "w3-container w3-twothird w3-mobile");
        const paraInfo2 = document.createElement("p");
        paraInfo2.setAttribute("class", "w3-left-align");
        paraInfo2.textContent = `${lap.this_lap.distance} km`;

        divData2.appendChild(paraInfo2);
        divLabel2.appendChild(paraLabel2);
        div2.appendChild(divLabel2);
        div2.appendChild(divData2);
        myArticle.appendChild(div2);
    }

    if (lap.this_lap.ascent) {
        const div3 = document.createElement("div");
        div3.setAttribute("class", "row w3-row");
        const divLabel3 =document.createElement("div");
        divLabel3.setAttribute("class", "w3-container w3-third 3w-mobile");
        const paraLabel3 = document.createElement("p");
        paraLabel3.setAttribute("class", "w3-left-align wbold");
        paraLabel3.textContent = "Dislivello salita:";
        const divData3 = document.createElement("div");
        divData3.setAttribute("class", "w3-container w3-twothird w3-mobile");
        const paraInfo3 = document.createElement("p");
        paraInfo3.setAttribute("class", "w3-left-align");
        paraInfo3.textContent = `${lap.this_lap.ascent} m`;

        divData3.appendChild(paraInfo3);
        divLabel3.appendChild(paraLabel3);
        div3.appendChild(divLabel3);
        div3.appendChild(divData3);
        myArticle.appendChild(div3);
    }

    if (lap.this_lap.descent) {
        const div4 = document.createElement("div");
        div4.setAttribute("class", "row w3-row");
        const divLabel4 =document.createElement("div");
        divLabel4.setAttribute("class", "w3-container w3-third 3w-mobile");
        const paraLabel4 = document.createElement("p");
        paraLabel4.setAttribute("class", "w3-left-align wbold");
        paraLabel4.textContent = "Dislivello discesa:";
        const divData4 = document.createElement("div");
        divData4.setAttribute("class", "w3-container w3-twothird w3-mobile");
        const paraInfo4 = document.createElement("p");
        paraInfo4.setAttribute("class", "w3-left-align");
        paraInfo4.textContent = `${lap.this_lap.descent} m`;

        divData4.appendChild(paraInfo4);
        divLabel4.appendChild(paraLabel4);
        div4.appendChild(divLabel4);
        div4.appendChild(divData4);
        myArticle.appendChild(div4);
    }

    if (lap.this_lap.duration) {
        const div5 = document.createElement("div");
        div5.setAttribute("class", "row w3-row");
        const divLabel5 =document.createElement("div");
        divLabel5.setAttribute("class", "w3-container w3-third 3w-mobile");
        const paraLabel5 = document.createElement("p");
        paraLabel5.setAttribute("class", "w3-left-align wbold");
        paraLabel5.textContent = "Tempo:";
        const divData5 = document.createElement("div");
        divData5.setAttribute("class", "w3-container w3-twothird w3-mobile");
        const paraInfo5 = document.createElement("p");
        paraInfo5.setAttribute("class", "w3-left-align");
        paraInfo5.textContent = lap.this_lap.duration;

        divData5.appendChild(paraInfo5);
        divLabel5.appendChild(paraLabel5);
        div5.appendChild(divLabel5);
        div5.appendChild(divData5);
        myArticle.appendChild(div5);
    }

    if (lap.this_lap.media) {
        const div6 = document.createElement("div");
        div6.setAttribute("class", "row w3-row");
        const divLabel6 =document.createElement("div");
        divLabel6.setAttribute("class", "w3-container w3-third 3w-mobile");
        const paraLabel6 = document.createElement("p");
        paraLabel6.setAttribute("class", "w3-left-align wbold");
        paraLabel6.textContent = "Media:";
        const divData6 = document.createElement("div");
        divData6.setAttribute("class", "w3-container w3-twothird w3-mobile");
        const paraInfo6 = document.createElement("p");
        paraInfo6.setAttribute("class", "w3-left-align");
        paraInfo6.textContent = `${lap.this_lap.media} km/h`;

        divData6.appendChild(paraInfo6);
        divLabel6.appendChild(paraLabel6);
        div6.appendChild(divLabel6);
        div6.appendChild(divData6);
        myArticle.appendChild(div6);
    }

    const div7 = document.createElement("div");
    div7.setAttribute("class", "row w3-row");
    const divLabel7 =document.createElement("div");
    divLabel7.setAttribute("class", "w3-container w3-third 3w-mobile");
    const paraLabel7 = document.createElement("p");
    paraLabel7.setAttribute("class", "w3-left-align wbold");
    paraLabel7.textContent = "Fatta:";
    const divData7 = document.createElement("div");
    divData7.setAttribute("class", "w3-container w3-twothird w3-mobile");
    const paraInfo7 = document.createElement("p");
    if (lap.this_lap.done) {
        paraInfo7.setAttribute("class", "w3-left-align");
        const span = document.createElement("span");
        span.setAttribute("class", "material-symbols-outlined done");
        span.textContent="done";
        paraInfo7.appendChild(span);
    }

    divData7.appendChild(paraInfo7);
    divLabel7.appendChild(paraLabel7);
    div7.appendChild(divLabel7);
    div7.appendChild(divData7);
    myArticle.appendChild(div7);

    if (lap.this_lap.gpx) {
        const div8 = document.createElement("div");
        div8.setAttribute("class", "row w3-row");
        const divLabel8 =document.createElement("div");
        divLabel8.setAttribute("class", "w3-container w3-third 3w-mobile");
        const paraLabel8 = document.createElement("p");
        paraLabel8.setAttribute("class", "w3-left-align wbold");
        paraLabel8.textContent = "Traccia gpx:";
        const divData8 = document.createElement("div");
        divData8.setAttribute("class", "w3-container w3-twothird w3-mobile");
        const paraInfo8 = document.createElement("p");
        paraInfo8.setAttribute("class", "w3-left-align");
        const a8 = document.createElement("a");
        a8.setAttribute("href", lap.this_lap.gpx);
        a8.textContent = `${lap.this_lap.start} - ${lap.this_lap.destination}`;

        paraInfo8.appendChild(a8)
        divData8.appendChild(paraInfo8);
        divLabel8.appendChild(paraLabel8);
        div8.appendChild(divLabel8);
        div8.appendChild(divData8);
        myArticle.appendChild(div8);
    }

    if (lap.this_lap.hotels.length) {
        const div9= document.createElement("div");
        div9.setAttribute("class", "row w3-row");
        const divLabel9 =document.createElement("div");
        divLabel9.setAttribute("class", "w3-container w3-third 3w-mobile");
        const paraLabel9 = document.createElement("p");
        paraLabel9.setAttribute("class", "w3-left-align wbold");
        paraLabel9.textContent = "Alberghi:";
        const divData9 = document.createElement("div");
        divData9.setAttribute("class", "w3-container w3-twothird w3-mobile");
        let paraInfo9, a9;
        for (hotel of lap.this_lap.hotels) {
            paraInfo9 = document.createElement("p");
            paraInfo9.setAttribute("class", "w3-left-align");
            a9 = document.createElement("a");
            a9.setAttribute("href", hotel.URL);
            a9.textContent = hotel.name;
            paraInfo9.appendChild(a9);
            divData9.appendChild(paraInfo9);
        }

        divLabel9.appendChild(paraLabel9);
        div9.appendChild(divLabel9);
        div9.appendChild(divData9);
        myArticle.appendChild(div9);
    }

    if (lap.prev_lap) {
        const div10 = document.createElement("div");
        div10.setAttribute("class", "row w3-row");
        const divLabel10 =document.createElement("div");
        divLabel10.setAttribute("class", "w3-container w3-third 3w-mobile");
        const paraLabel10 = document.createElement("p");
        paraLabel10.setAttribute("class", "w3-left-align wbold");
        paraLabel10.textContent = "Tappa precedente:";
        const divData10 = document.createElement("div");
        divData10.setAttribute("class", "w3-container w3-twothird w3-mobile");
        const paraInfo10 = document.createElement("p");
        paraInfo10.setAttribute("class", "w3-left-align");
        paraInfo10.dataset.lapId = lap.prev_lap.id;
        paraInfo10.textContent = `${lap.prev_lap.start} - ${lap.prev_lap.destination}`;
        paraInfo10.addEventListener("click", openLap);

        divData10.appendChild(paraInfo10);
        divLabel10.appendChild(paraLabel10);
        div10.appendChild(divLabel10);
        div10.appendChild(divData10);
        myArticle.appendChild(div10);
    }

    if (lap.next_lap) {
        const div11 = document.createElement("div");
        div11.setAttribute("class", "row w3-row");
        const divLabel11 =document.createElement("div");
        divLabel11.setAttribute("class", "w3-container w3-third 3w-mobile");
        const paraLabel11 = document.createElement("p");
        paraLabel11.setAttribute("class", "w3-left-align wbold");
        paraLabel11.textContent = "Tappa successiva:";
        const divData11 = document.createElement("div");
        divData11.setAttribute("class", "w3-container w3-twothird w3-mobile");
        const paraInfo11 = document.createElement("p");
        paraInfo11.setAttribute("class", "w3-left-align");
        paraInfo11.dataset.lapId = lap.next_lap.id;
        paraInfo11.textContent = `${lap.next_lap.start} - ${lap.next_lap.destination}`;
        paraInfo11.addEventListener("click", openLap);

        divData11.appendChild(paraInfo11);
        divLabel11.appendChild(paraLabel11);
        div11.appendChild(divLabel11);
        div11.appendChild(divData11);
        myArticle.appendChild(div11);
    }

    if (Object.hasOwn(session, '_user_id')) {
        const div12 = document.createElement("div");
        div12.setAttribute("class", "w3-container w3-center");
        div12.style.marginTop = "60px";
        const div13 = document.createElement("div");
        div13.setAttribute("class", "w3-bar");
        const a12 = document.createElement("a");
        setAttributes(a12, {href: lap.this_lap.update, class: "w3-bar-item w3-ripple", title: "Modifica questa tappa"})
        const span12 = document.createElement("span");
        span12.setAttribute("class", "material-symbols-outlined icon28");
        span12.textContent = "edit"
        const a13 = document.createElement("a");
        setAttributes(a13, {href: lap.this_lap.delete, class: "w3-bar-item w3-ripple", title: "Cancella questa tappa"})
        const span13 = document.createElement("span");
        span13.setAttribute("class", "material-symbols-outlined icon28");
        span13.textContent = "delete";
        a13.appendChild(span13);
        a12.appendChild(span12);
        div13.appendChild(a12);
        div13.appendChild(a13);
        div12.appendChild(div13);
        myArticle.appendChild(div12);
    }

    outerDiv.appendChild(myArticle);
}

async function openHotel(evt) {
  if (document.querySelector("#summary")) {
    document.querySelector("#summary").style.display = "none";
  }

  const display = document.querySelector("#display");

  const hotelId = evt.target.dataset.hotelId;
  const requestURL =
    `${SCRIPT_ROOT.slice(0, -3)}/${hotelId}`;
  console.log(requestURL);
  const request = new Request(requestURL);

  const response = await fetch(request);
  const hotelText = await response.text();
  console.log(hotelText);

  const hotel = JSON.parse(hotelText);

  // remove the previous lap, if any

  if (document.querySelector("#hotel")) {
    document.querySelector("#hotel").remove()
  }

  const outerDiv = document.createElement("div");
  setAttributes(outerDiv, {id: "hotel", class: "w3-container w3-center albergo"});
  outerDiv.style.display = "block";

  populateHeaderHotel(hotel, outerDiv);
  populateHotel(hotel, outerDiv);

  display.appendChild(outerDiv);

  const tablinks = document.querySelectorAll(".tablink");
  for (const tablink of tablinks) {
    tablink.className = tablink.className.replace(" w3-theme-d2", "");
  }

  evt.target.className += " w3-theme-d2";

  closeMenu()
}

function populateHeaderHotel(hotel, outerDiv) {
    const header = document.createElement("header");
    const innerDiv = document.createElement("div");

    innerDiv.setAttribute("class", "w3-display-container");
    innerDiv.style.height = "200px";
    const hotelImg = document.createElement("img");
    setAttributes(hotelImg, {src: hotel.this_hotel.photo, class: "w3-display-left w3-margin-left w3-margin-top webp"});
    const h2 = document.createElement("h2");
    h2.textContent = hotel.this_hotel.name;
    h2.setAttribute("class", "w3-display-middle");
    innerDiv.appendChild(hotelImg)
    innerDiv.appendChild(h2);
    header.appendChild(innerDiv);
    outerDiv.appendChild(header);
}

function populateHotel(hotel, outerDiv) {
    const myArticle = document.createElement("article");
    myArticle.style.margin = "60px 5% 0 5%";

    const div1 = document.createElement("div");
    div1.setAttribute("class", "row w3-row");
    const divLabel1 =document.createElement("div");
    divLabel1.setAttribute("class", "w3-container w3-third 3w-mobile");
    const paraLabel1 = document.createElement("p");
    paraLabel1.setAttribute("class", "w3-left-align wbold");
    paraLabel1.textContent = "Indirizzo:";
    const divData1 = document.createElement("div");
    divData1.setAttribute("class", "w3-container w3-twothird w3-mobile");
    const paraInfo1 = document.createElement("p");
    paraInfo1.setAttribute("class", "w3-left-align");
    paraInfo1.textContent = hotel.this_hotel.address;
    divData1.appendChild(paraInfo1);
    divLabel1.appendChild(paraLabel1);
    div1.appendChild(divLabel1);
    div1.appendChild(divData1);
    myArticle.appendChild(div1);
    
    const div2 = document.createElement("div");
    div2.setAttribute("class", "row w3-row");
    const divLabel2 =document.createElement("div");
    divLabel2.setAttribute("class", "w3-container w3-third 3w-mobile");
    const paraLabel2 = document.createElement("p");
    paraLabel2.setAttribute("class", "w3-left-align wbold");
    paraLabel2.textContent = "Città:";
    const divData2 = document.createElement("div");
    divData2.setAttribute("class", "w3-container w3-twothird w3-mobile");
    const paraInfo2 = document.createElement("p");
    paraInfo2.setAttribute("class", "w3-left-align");
    paraInfo2.textContent = hotel.this_hotel.town;
    divData2.appendChild(paraInfo2);
    divLabel2.appendChild(paraLabel2);
    div2.appendChild(divLabel2);
    div2.appendChild(divData2);
    myArticle.appendChild(div2);

    const div3 = document.createElement("div");
    div3.setAttribute("class", "row w3-row");
    const divLabel3 =document.createElement("div");
    divLabel3.setAttribute("class", "w3-container w3-third 3w-mobile");
    const paraLabel3 = document.createElement("p");
    paraLabel3.setAttribute("class", "w3-left-align wbold");
    paraLabel3.textContent = "Prenotazione:";
    const divData3 = document.createElement("div");
    divData3.setAttribute("class", "w3-container w3-twothird w3-mobile");
    const paraInfo3 = document.createElement("p");
    if (hotel.this_hotel.reserved) {
        paraInfo3.setAttribute("class", "w3-left-align");
        const span = document.createElement("span");
        span.setAttribute("class", "material-symbols-outlined done");
        span.textContent="done";
        paraInfo3.appendChild(span);
    }
    divData3.appendChild(paraInfo3);
    divLabel3.appendChild(paraLabel3);
    div3.appendChild(divLabel3);
    div3.appendChild(divData3);
    myArticle.appendChild(div3);

    if (hotel.this_hotel.check_in) {
        const div4 = document.createElement("div");
        div4.setAttribute("class", "row w3-row");
        const divLabel4 =document.createElement("div");
        divLabel4.setAttribute("class", "w3-container w3-third 3w-mobile");
        const paraLabel4 = document.createElement("p");
        paraLabel4.setAttribute("class", "w3-left-align wbold");
        paraLabel4.textContent = "Check-in:";
        const divData4 = document.createElement("div");
        divData4.setAttribute("class", "w3-container w3-twothird w3-mobile");
        const paraInfo4 = document.createElement("p");
        paraInfo4.setAttribute("class", "w3-left-align");
        paraInfo4.textContent = hotel.this_hotel.check_in;
        divData4.appendChild(paraInfo4);
        divLabel4.appendChild(paraLabel4);
        div4.appendChild(divLabel4);
        div4.appendChild(divData4);
        myArticle.appendChild(div4);
    };

    if (hotel.this_hotel.check_out) {
        const div5 = document.createElement("div");
        div5.setAttribute("class", "row w3-row");
        const divLabel5 =document.createElement("div");
        divLabel5.setAttribute("class", "w3-container w3-third 3w-mobile");
        const paraLabel5 = document.createElement("p");
        paraLabel5.setAttribute("class", "w3-left-align wbold");
        paraLabel5.textContent = "Check-out:";
        const divData5 = document.createElement("div");
        divData5.setAttribute("class", "w3-container w3-twothird w3-mobile");
        const paraInfo5 = document.createElement("p");
        paraInfo5.setAttribute("class", "w3-left-align");
        paraInfo5.textContent = hotel.this_hotel.check_out;
        divData5.appendChild(paraInfo5);
        divLabel5.appendChild(paraLabel5);
        div5.appendChild(divLabel5);
        div5.appendChild(divData5);
        myArticle.appendChild(div5);
    }

    if (hotel.this_hotel.price) {
        const div6 = document.createElement("div");
        div6.setAttribute("class", "row w3-row");
        const divLabel6 =document.createElement("div");
        divLabel6.setAttribute("class", "w3-container w3-third 3w-mobile");
        const paraLabel6 = document.createElement("p");
        paraLabel6.setAttribute("class", "w3-left-align wbold");
        paraLabel6.textContent = "Costo:";
        const divData6 = document.createElement("div");
        divData6.setAttribute("class", "w3-container w3-twothird w3-mobile");
        const paraInfo6 = document.createElement("p");
        paraInfo6.setAttribute("class", "w3-left-align");
        paraInfo6.textContent = `€ ${hotel.this_hotel.price}`;
        divData6.appendChild(paraInfo6);
        divLabel6.appendChild(paraLabel6);
        div6.appendChild(divLabel6);
        div6.appendChild(divData6);
        myArticle.appendChild(div6);
    }

    if (hotel.this_hotel.tappa) {
        const div7 = document.createElement("div");
        div7.setAttribute("class", "row w3-row");
        const divLabel7 =document.createElement("div");
        divLabel7.setAttribute("class", "w3-container w3-third 3w-mobile");
        const paraLabel7 = document.createElement("p");
        paraLabel7.setAttribute("class", "w3-left-align wbold");
        paraLabel7.textContent = "Tappa:";
        const divData7 = document.createElement("div");
        divData7.setAttribute("class", "w3-container w3-twothird w3-mobile");
        const paraInfo7 = document.createElement("p");
        paraInfo7.setAttribute("class", "w3-left-align");
        const a7 = document.createElement("a");
        a7.setAttribute("href", hotel.this_hotel.tappa.URL);
        a7.textContent = `${hotel.this_hotel.tappa.start} - ${hotel.this_hotel.tappa.destination}`;
        paraInfo7.appendChild(a7);
        divData7.appendChild(paraInfo7);
        divLabel7.appendChild(paraLabel7);
        div7.appendChild(divLabel7);
        div7.appendChild(divData7);
        myArticle.appendChild(div7);
    }

    if (hotel.this_hotel.link) {
        const div7 = document.createElement("div");
        div7.setAttribute("class", "row w3-row");
        const divLabel7 =document.createElement("div");
        divLabel7.setAttribute("class", "w3-container w3-third 3w-mobile");
        const paraLabel7 = document.createElement("p");
        paraLabel7.setAttribute("class", "w3-left-align wbold");
        paraLabel7.textContent = "Sito web:";
        const divData7 = document.createElement("div");
        divData7.setAttribute("class", "w3-container w3-twothird w3-mobile");
        const paraInfo7 = document.createElement("p");
        paraInfo7.setAttribute("class", "w3-left-align");
        const a7 = document.createElement("a");
        setAttributes(a7, {href: hotel.this_hotel.link, target:"_blank"});
        a7.textContent = hotel.this_hotel.name;
        paraInfo7.appendChild(a7);
        divData7.appendChild(paraInfo7);
        divLabel7.appendChild(paraLabel7);
        div7.appendChild(divLabel7);
        div7.appendChild(divData7);
        myArticle.appendChild(div7);
    }
    if (Object.hasOwn(session, '_user_id')) {
        const div12 = document.createElement("div");
        div12.setAttribute("class", "w3-container w3-center");
        div12.style.marginTop = "60px";
        const div13 = document.createElement("div");
        div13.setAttribute("class", "w3-bar");
        const a12 = document.createElement("a");
        setAttributes(a12, {href: hotel.this_hotel.update, class: "w3-bar-item w3-ripple", title: "Modifica questo hotel"})
        const span12 = document.createElement("span");
        span12.setAttribute("class", "material-symbols-outlined icon28");
        span12.textContent = "edit"
        const a13 = document.createElement("a");
        setAttributes(a13, {href: hotel.this_hotel.delete, class: "w3-bar-item w3-ripple", title: "Cancella questo hotel"})
        const span13 = document.createElement("span");
        span13.setAttribute("class", "material-symbols-outlined icon28");
        span13.textContent = "delete";
        a13.appendChild(span13);
        a12.appendChild(span12);
        div13.appendChild(a12);
        div13.appendChild(a13);
        div12.appendChild(div13);
        myArticle.appendChild(div12);
    }
    outerDiv.appendChild(myArticle);
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

