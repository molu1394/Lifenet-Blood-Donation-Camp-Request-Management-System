function logout() {
        localStorage.removeItem("isLoggedIn");
        localStorage.removeItem("userName");
        localStorage.removeItem("userEmail");
        window.location.href = "index.html";
    }

 function updateAuthUI() {
        const navAuth = document.getElementById("nav-auth");
        const navList = document.getElementById("navbar-links");

        const isLoggedIn = localStorage.getItem("isLoggedIn") === "true";
        const existingLogout = document.getElementById("nav-logout");
        if (existingLogout) existingLogout.parentElement.remove();

        if (isLoggedIn) {
            const userName = localStorage.getItem("userName") || "Profile";
            navAuth.textContent = userName;
            navAuth.href = "profile.html";

            const li = document.createElement("li");
            li.className = "nav-item";
            li.innerHTML = `<a class="nav-link" href="#" id="nav-logout">Logout</a>`;
            navList.appendChild(li);

            document.getElementById("nav-logout").addEventListener("click", function (e) {
                e.preventDefault();
                logout();
            });
        } else {
            navAuth.textContent = "Login";
            navAuth.href = "login.html";
        }
 }  

document.addEventListener("DOMContentLoaded", function () {
    const nav = document.getElementById("navbar");
    const navCollapse = document.getElementById("navbarNav");
    const mainContent = document.querySelector(".main-content");
    const toggler = document.querySelector(".navbar-toggler");

    const bsCollapse = new bootstrap.Collapse(navCollapse, { toggle: false });
    const isSmall = () => window.innerWidth < 992;

    // Function to update margin-top based on navbar height
    const updateContentOffset = () => {
        const totalHeight = nav.offsetHeight + (navCollapse.classList.contains("show") ? navCollapse.scrollHeight : 0);
        mainContent.style.marginTop = totalHeight + "px";
    };

    // Initialize offset
    updateContentOffset();

    // Resize listener
    window.addEventListener("resize", () => {
        if (!isSmall()) bsCollapse.hide();
        updateContentOffset();
    });

    // Click toggler to open/close menu
    toggler.addEventListener("click", () => {
        if (isSmall()) {
            if (navCollapse.classList.contains("show")) {
                bsCollapse.hide();
                toggler.classList.remove("rotate"); // remove rotate when closing
            } else {
                bsCollapse.show();
                toggler.classList.add("rotate"); // add rotate when opening
            }
        }
    });

    // Reset rotation when nav closes via backdrop or other way
    navCollapse.addEventListener("hidden.bs.collapse", () => {
        toggler.classList.remove("rotate");
    });

    // Sync margin when collapse animates
    navCollapse.addEventListener("shown.bs.collapse", updateContentOffset);
    navCollapse.addEventListener("hidden.bs.collapse", updateContentOffset);
});

