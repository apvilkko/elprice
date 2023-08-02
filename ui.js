const now = new Date();
const hour = now.getHours();
const el = document.getElementById("row-" + hour);
if (el) {
    for (let i = 0; i < 2; ++i) {
        const e = el.getElementsByTagName('td')[i];
        e.style.fontWeight = "900";
        if (i > 0) {
            e.innerText = "[ " + e.innerText +  " ]"
        }
    }
}