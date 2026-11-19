
/* =====================================
   BOUTIQUE PLUS - CONNEXION.JS
===================================== */

// Référence à la notification
let notificationTimer;


// =====================================
// 1. AFFICHER UNE NOTIFICATION
// =====================================

function showNotification(type, title, message) {

    const notification = document.getElementById("notification");

    const icon = document.getElementById("notificationIcon");

    const notificationTitle = document.getElementById("notificationTitle");

    const notificationMessage = document.getElementById("notificationMessage");


    // Définir le titre et le message
    notificationTitle.textContent = title;

    notificationMessage.textContent = message;


    // Réinitialiser les classes
    notification.className = "notification";


    // Choisir l'emoji selon le type
    if (type === "success") {

        icon.textContent = "🎉";

    }

    else if (type === "error") {

        icon.textContent = "😢";

        notification.classList.add("error");

    }

    else {

        icon.textContent = "🔔";

        notification.classList.add("info");

    }


    // Relancer l'animation
    void notification.offsetWidth;

    notification.classList.add("show");


    // Supprimer l'ancien minuteur
    clearTimeout(notificationTimer);


    // Fermer automatiquement après 4 secondes
    notificationTimer = setTimeout(function() {

        closeNotification();

    }, 4000);

}



// =====================================
// 2. FERMER UNE NOTIFICATION
// =====================================

function closeNotification() {

    const notification = document.getElementById("notification");

    notification.classList.remove("show");

    clearTimeout(notificationTimer);

}



// =====================================
// 3. AFFICHER LE FORMULAIRE CONNEXION
// =====================================

function showLogin() {

    document.getElementById("loginForm")
        .classList.remove("hidden");

    document.getElementById("registerForm")
        .classList.add("hidden");


    // Activer l'onglet connexion
    document.getElementById("loginTab")
        .classList.add("active");

    document.getElementById("registerTab")
        .classList.remove("active");

}



// =====================================
// 4. AFFICHER LE FORMULAIRE INSCRIPTION
// =====================================

function showRegister() {

    document.getElementById("registerForm")
        .classList.remove("hidden");

    document.getElementById("loginForm")
        .classList.add("hidden");


    // Activer l'onglet inscription
    document.getElementById("registerTab")
        .classList.add("active");

    document.getElementById("loginTab")
        .classList.remove("active");

}



// =====================================
// 5. VERIFICATION DU FORMULAIRE INSCRIPTION
// =====================================

document.getElementById("registerForm")
.addEventListener("submit", function(event) {

    event.preventDefault();


    // Récupérer les mots de passe
    let password = document.getElementById("password").value;

    let confirmPassword = document.getElementById("confirmPassword").value;


    // Vérifier si les mots de passe sont identiques
    if (password !== confirmPassword) {

        showNotification(
            "error",
            "Oups !",
            "Les mots de passe ne correspondent pas. Veuillez réessayer."
        );

        return;

    }


    // Vérifier la longueur du mot de passe
    if (password.length < 8) {

        showNotification(
            "error",
            "Mot de passe trop court !",
            "Votre mot de passe doit contenir au moins 8 caractères."
        );

        return;

    }


    // Message de succès (démonstration uniquement)
    showNotification(
        "success",
        "Bravo !",
        "Votre compte a été créé avec succès."
    );


    // Réinitialiser le formulaire
    this.reset();

});



// =====================================
// 6. VERIFICATION DU FORMULAIRE CONNEXION
// =====================================

document.getElementById("loginForm")
.addEventListener("submit", function(event) {

    event.preventDefault();


    // Récupérer les informations
    let username = this.querySelector('[name="username"]').value;

    let password = this.querySelector('[name="password"]').value;


    // Vérifier les champs
    if (username.trim() === "" || password.trim() === "") {

        showNotification(
            "error",
            "Attention !",
            "Veuillez remplir tous les champs."
        );

        return;

    }


    // Message de démonstration
    showNotification(
        "info",
        "Connexion",
        "Votre demande de connexion est en cours de traitement."
    );

});
