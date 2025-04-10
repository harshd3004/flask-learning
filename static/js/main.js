document.addEventListener("DOMContentLoaded",()=> {
    console.log("Website loaded succesfully");
})

const toggle = document.getElementById("darkModeToggle")
toggle.addEventListener('change',()=>{
    
    document.documentElement.setAttribute(
        "data-bs-theme",
        toggle.checked ? "dark" : "light"
    );
})