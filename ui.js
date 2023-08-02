const now = new Date();
const hour = now.getHours();
const el = document.getElementById("row-" + hour)
if (el) {
    for (let i = 0; i < 2; ++i) {
        el.getElementsByTagName('td')[i].style = "font-weight: 900; background-color: #111;"
    }
}