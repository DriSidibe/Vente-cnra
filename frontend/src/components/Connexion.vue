<script setup lang="ts">

import { ref } from 'vue';

interface Notif {
    icon: string;
    titre: string;
    message: string;
}


let notif = ref<Notif>({
    icon: "",
    titre: "Connexion réussie",
    message : "Vous êtes maintenant connecté à votre compte.",
});
let showLoginForm = ref(true);
let showNotif= ref(false);


function showLogin() {
    showLoginForm.value = true;
}

function showRegister() {
    showLoginForm.value = false;
    showNotification("signup", "Inscription réussie", "Votre compte a été créé avec succès.");
    showNotif.value = true;
}

function closeNotification() {
    const notification = document.getElementById('notification');
    if (notification) {
        notification.classList.remove('show');
    }
}

function showNotification(type:string, title:string, message:string) {
        if(type="login") {
            notif.value.icon = "✔️";
            notif.value.titre = title;
            notif.value.message = message;
            showNotif.value = true;
        }
        if(type="signup") {
            notif.value.icon = "📝";
            notif.value.titre = title;
            notif.value.message = message;
            showNotif.value = true;
        }
}

function login() {
    showNotification("login", "Connexion réussie", "Vous êtes maintenant connecté à votre compte.");
    showNotif.value = true;
}

function signup() {
    showNotification("signup", "Inscription réussie", "Votre compte a été créé avec succès.");
    showNotif.value = true;
}
</script>

<template>
    <!-- Zone des notifications -->
    <div v-if="showNotif" class="" style="position: fixed; top: 20px; right: 20px; z-index: 9999;" id="notification">
        <div class="" id="">{{ notif.icon }}</div>

        <div class="">
            <strong id="">{{ notif.titre }}</strong>
            <p id="">
                {{ notif.message }}
            </p>
        </div>

        <button class="close-notification"
            @click="closeNotification()">×</button>

        <div class="notification-progress"></div>
    </div>
    <div class="container">

        <div class="login-box">

            <!-- Logo -->
            <div class="logo">
                🛒
                <h1>Boutique Plus</h1>
                <p>Gestion Commerciale</p>
            </div>

            <!-- Boutons de navigation -->
            <div class="tabs" >
                <button class="tab active" id="loginTab"
                    @click="showLogin()" :style="{ backgroundColor: showLoginForm ? '#0875ff' : 'white', color: showLoginForm ? 'white' : '#526078' }">
                    Connexion
                </button>

                <button class="tab" id="registerTab"
                    @click="showRegister()" :style="{ backgroundColor: !showLoginForm ? '#0875ff' : 'white', color: !showLoginForm ? 'white' : '#526078' }">
                    Créer un compte
                </button>
            </div>

            <!-- FORMULAIRE CONNEXION -->
            <form v-if="showLoginForm" class="form">

                <h2>Bienvenue !</h2>
                <p class="subtitle">Connectez-vous à votre espace</p>

                <div class="form-group">
                    <label>Nom utilisateur</label>
                    <input type="text"
                        name="username"
                        placeholder="Votre nom utilisateur"
                        required>
                </div>

                <div class="form-group">
                    <label>Mot de passe</label>
                    <input type="password"
                        name="password"
                        placeholder="Votre mot de passe"
                        required>
                </div>

                <button type="button" class="submit-btn" @click="login">
                    Se connecter
                </button>

            </form>

            <!-- FORMULAIRE INSCRIPTION -->
            <form v-else class="form">

                <h2>Créer un compte</h2>
                <p class="subtitle">Remplissez les informations ci-dessous</p>

                <div class="form-group">
                    <label>Nom</label>
                    <input type="text"
                        name="nom"
                        placeholder="Votre nom"
                        required>
                </div>

                <div class="form-group">
                    <label>Prénom</label>
                    <input type="text"
                        name="prenom"
                        placeholder="Votre prénom"
                        required>
                </div>

                <div class="form-group">
                    <label>Nom utilisateur</label>
                    <input type="text"
                        name="username"
                        placeholder="Choisissez un nom utilisateur"
                        required>
                </div>

                <div class="form-group">
                    <label>Mot de passe</label>
                    <input type="password"
                        id="password"
                        name="password"
                        placeholder="Créer un mot de passe"
                        minlength="8"
                        required>
                </div>

                <div class="form-group">
                    <label>Confirmer le mot de passe</label>
                    <input type="password"
                        id="confirmPassword"
                        name="confirm_password"
                        placeholder="Confirmer votre mot de passe"
                        minlength="8"
                        required>
                </div>

                <button type="button" class="submit-btn" @click="signup()">
                    Créer mon compte
                </button>

            </form>

            <p class="footer">
                © 2026 Boutique Plus - Gestion Commerciale
            </p>

        </div>

    </div>
</template>

<style scoped>

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Roboto', sans-serif;
}

body {
    min-height: 100vh;
    background: linear-gradient(135deg, #2d4b84, #283b54);
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
}

/* Conteneur principal */
.container {
    width: 100%;
    max-width: 450px;
}

/* Carte de connexion */
.login-box {
    background: rgba(255, 255, 255, 0.96);
    padding: 35px;
    border-radius: 18px;
    box-shadow: 0 15px 45px rgba(0, 0, 0, 0.25);
}

/* Logo */
.logo {
    text-align: center;
    margin-bottom: 25px;
}

.logo {
    font-size: 35px;
}

.logo h1 {
    font-size: 25px;
    color: #17243c;
    margin-top: 8px;
}

.logo p {
    font-size: 13px;
    color: #71809b;
    margin-top: 5px;
}

/* Onglets */
.tabs {
    display: flex;
    background: #edf1f8;
    padding: 5px;
    border-radius: 10px;
    margin-bottom: 25px;
}

.tab {
    flex: 1;
    padding: 12px 5px;
    border: none;
    background: transparent;
    border-radius: 8px;
    font-size: 14px;
    cursor: pointer;
    color: #526078;
    transition: .3s;
}

.tab.active {
    background: #0875ff;
    color: white;
}

/* Formulaires */
.form h2 {
    color: #17243c;
    font-size: 23px;
    margin-bottom: 7px;
}

.subtitle {
    color: #71809b;
    font-size: 14px;
    margin-bottom: 22px;
}

/* Champs */
.form-group {
    margin-bottom: 17px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #17243c;
    font-size: 14px;
}

.form-group input {
    width: 100%;
    height: 46px;
    padding: 0 13px;
    border: 1px solid #d5deeb;
    border-radius: 8px;
    outline: none;
    font-size: 14px;
    transition: .3s;
}

.form-group input:focus {
    border-color: #0875ff;
    box-shadow: 0 0 0 3px rgba(8, 117, 255, .12);
}

.form-group input::placeholder {
    color: #a0aabd;
}

/* Bouton */
.submit-btn {
    width: 100%;
    height: 48px;
    border: none;
    border-radius: 8px;
    background: linear-gradient(135deg, #0875ff, #0054d9);
    color: white;
    font-size: 15px;
    font-weight: 700;
    cursor: pointer;
    transition: .3s;
    margin-top: 8px;
}

.submit-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(8, 117, 255, .25);
}

/* Masquer un formulaire */
.hidden {
    display: none;
}

/* Pied de page */
.footer {
    text-align: center;
    color: #8a96a9;
    font-size: 12px;
    margin-top: 25px;
}

/* Adaptation mobile */
@media (max-width: 480px) {
    .login-box {
        padding: 25px 20px;
    }

    .logo h1 {
        font-size: 22px;
    }
}
/* NOTIFICATIONS PERSONNALISÉES */

.notification {
    position: fixed;
    top: 25px;
    right: 25px;
    width: 350px;
    min-height: 85px;

    background: white;
    display: flex;
    align-items: center;
    gap: 15px;

    padding: 18px;
    border-radius: 12px;

    box-shadow: 0 8px 30px rgba(0,0,0,0.15);

    transform: translateX(120%);
    opacity: 0;

    transition: all 0.5s ease;
    z-index: 9999;
    overflow: hidden;
}

/* Apparition */
.notification.show {
    transform: translateX(0);
    opacity: 1;
}

/* Icône */
.notification-icon {
    width: 45px;
    height: 45px;
    min-width: 45px;

    display: flex;
    justify-content: center;
    align-items: center;

    background: #19bd72;
    border-radius: 50%;

    font-size: 27px;
}
/* Texte */
.notification-content strong {
    display: block;
    color: #17243c;
    font-size: 16px;
    margin-bottom: 5px;
}

.notification-content p {
    color: #71809b;
    font-size: 13px;
    line-height: 1.4;
}

/* Bouton fermer */
.close-notification {
    margin-left: auto;
    border: none;
    background: none;
    font-size: 22px;
    color: #71809b;
    cursor: pointer;
}

/* Barre de progression */
.notification-progress {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: #19bd72;
}

.notification.show .notification-progress {
    animation: progress 4s linear forwards;
}

@keyframes progress {
    from {
        width: 100%;
    }

    to {
        width: 0;
    }
}

/* Notification erreur */
.notification.error .notification-icon {
    background: #e53935;
}

.notification.error .notification-progress {
    background: #e53935;
}

/* Notification information */
.notification.info .notification-icon {
    background: #0875ff;
}

.notification.info .notification-progress {
    background: #0875ff;
}

/* Adaptation mobile */
@media (max-width: 480px) {
    .notification {
        width: calc(100% - 30px);
        right: 15px;
        top: 15px;
    }
}
</style>