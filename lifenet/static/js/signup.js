// Profile picture preview
    const profileInput = document.getElementById("id_profile_pic");
    const previewImg = document.getElementById("profilePreview");

    if (profileInput) {
        profileInput.addEventListener("change", function (event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    previewImg.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    window.onload = function() {
        const profileInput = document.querySelector("#id_first_name");  
        if (profileInput) {
            profileInput.focus();
        }
    };
    window.onload = function() {
        let errorField = document.querySelector(".errorlist + input, .errorlist + select, .errorlist + textarea");
        if (errorField) {
            errorField.focus();
            errorField.scrollIntoView({behavior: "smooth", block: "center"});
        }
    };

    document.querySelectorAll(".toggle-password").forEach(btn => {
        btn.addEventListener("click", function() {
            const inputId = this.getAttribute("data-target");
            const input = document.getElementById(inputId);
            const icon = this.querySelector("i");

            if (input.type === "password") {
            input.type = "text";
            icon.classList.remove("bi-eye");
            icon.classList.add("bi-eye-slash");
            } else {
            input.type = "password";
            icon.classList.remove("bi-eye-slash");
            icon.classList.add("bi-eye");
            }
        });
        });