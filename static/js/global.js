// DARK MODE TOGGLE
document.querySelectorAll(".toggle-dark").forEach(btn => {
    btn.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");
    });
});

// DESKTOP DROPDOWN HOVER
document.querySelectorAll(".main-nav .dropdown").forEach(dropdown => {
    const menu = dropdown.querySelector(".dropdown-menu");
    dropdown.addEventListener("mouseenter", () => menu.classList.add("show"));
    dropdown.addEventListener("mouseleave", () => menu.classList.remove("show"));
});

// PROFILE DROPDOWN: hover for desktop, click always works
const profileWrapper = document.getElementById("profileDropdownWrapper");
const profileMenu = document.getElementById("profileDropdownMenu");
profileWrapper.addEventListener("mouseenter", () => {
    if (window.innerWidth >= 768) profileMenu.classList.add("show");
});
profileWrapper.addEventListener("mouseleave", () => {
    if (window.innerWidth >= 768) profileMenu.classList.remove("show");
});

// MOBILE BOTTOM SEARCH TOGGLE
const bottomSearchIcon = document.querySelector('.mobile-bottom-nav .bi-search');
if (bottomSearchIcon) {
    bottomSearchIcon.addEventListener('click', () => {
        const mobileSearch = document.getElementById('mobileSearch');
        mobileSearch.classList.toggle('d-none');
        const input = mobileSearch.querySelector('input');
        if(input) input.focus();
    });
}
