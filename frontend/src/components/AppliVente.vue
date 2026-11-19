<script setup lang="ts">

import StatisticsCharts from './subcomponents/statistics-charts.vue'

function decrement() {
    alert("Vous avez cliqué sur le chiffre d'affaires !");
}
</script>

<template>
  <div class="dashboard">

    <!-- Barre latérale -->
    <aside class="sidebar">
        <div class="logo">
            🛒 Boutique Plus
            <small>Gestion Commerciale</small>
        </div>

        <nav>
            <a class="active">🏠 Tableau de bord</a>
            <a>🛒 Ventes</a>
            <a>📦 Produits</a>
            <a>🌐 Catégories</a>
            <a>👥 Clients</a>
            <a>📊 Stock</a>
            <a>📑 Rapports</a>
            <a>👤 Utilisateurs</a>
            <a>⚙️ Paramètres</a>
            <a class="logout">⏻ Déconnexion</a>
        </nav>

        
    </aside>

    <!-- Contenu principal -->
    <main class="main">

        <header class="topbar">
            <span class="menu">☰</span>
            <div class="user-actions">
            <span class="notification">🔔</span>
            <span class="admin">Administrateur ▼</span>
            </div>
            
        </header>

        <section class="content">

            <div class="heading">
                <div>
                    <h1>Tableau de bord</h1>
                    <p>Vue d'ensemble de votre activité commerciale</p>
                </div>
                <button>📅 Ce mois-ci</button>
            </div>

            <!-- Statistiques -->
            <div class="stats">
                <StatisticsCharts chiffreAffaires="1250000" message="Chiffre d'affaires" color="blue" />
                <StatisticsCharts chiffreAffaires="125" message="Ventes réalisées" color="green" />
                <StatisticsCharts chiffreAffaires="320" message="Produits en stock" color="orange" />
                <StatisticsCharts chiffreAffaires="48" message="Clients enregistrés" color="purple" />
            </div>

            <!-- Zones de gestion -->
            <div class="panels">
                <section class="panel">
                    <h2>🛒 Nouvelle vente</h2>
                    <p>Enregistrement d'une nouvelle transaction</p>
                    <div class="placeholder">
                        Espace de gestion des ventes
                    </div>
                </section>

                <section class="panel">
                    <h2>◷ Ventes récentes</h2>
                    <div class="placeholder">
                        Historique des ventes
                    </div>
                </section>
            </div>

            <!-- Bas du tableau -->
            <div class="bottom-panels">
                <section class="panel">
                    <h3>Évolution des ventes</h3>
                    <div class="placeholder">Graphique des ventes</div>
                </section>

                <section class="panel">
                    <h3>Stock faible</h3>
                    <div class="placeholder">Alertes de stock</div>
                </section>

                <section class="panel">
                    <h3>Répartition des ventes</h3>
                    <div class="placeholder">Statistiques</div>
                </section>
            </div>

        </section>
    </main>
</div>
</template>

<style scoped>

/* Réinitialisation */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'roboto', sans-serif;
}

body {
    background: #edf1f8;
    color: #172033;
}

/* Structure générale */
.dashboard {
    display: flex;
    min-height: 100vh;
}

/* Barre latérale */
.sidebar {
    width: 245px;
    height: 100vh;
    background: linear-gradient(180deg, #17243c, #101a2c);
    color: white;

    position: fixed;
    top: 0;
    left: 0;

    display: flex;
    flex-direction: column;

    padding-bottom: 15px;
}

.logo {
    padding: 27px 20px;
    font-size: 21px;
    font-weight: bold;
    border-bottom: 1px solid #344158;
}

.logo small {
    display: block;
    font-size: 12px;
    margin-top: 8px;
    color: #cbd5e1;
}

.sidebar nav {
    margin-top: 20px;

    display: flex;
    flex-direction: column;

    flex: 1;
    overflow-y: auto;
}

.sidebar nav a,
.logout {
    display: block;
    color: white;
    padding: 15px 22px;
    text-decoration: none;
    cursor: pointer;
    transition: .3s;
}

.sidebar nav a:hover,
.sidebar nav .active {
    background: #0875ff;
}

.logout {
    position: static;

    display: block;
    width: 100%;

    padding: 18px 22px;
    margin-top: auto;

    color: white;
    text-decoration: none;

    border-top: 1px solid #344158;
    cursor: pointer;
}

/* Zone principale */
.main {
    margin-left: 245px;
    width: calc(100% - 245px);
}

/* Barre supérieure */
.topbar {
    height: 65px;
    background: rgba(255,255,255,.75);
    backdrop-filter: blur(15px);
    border-bottom: 1px solid #dce3ef;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 30px;
}

.user-actions {
    display: flex;
    align-items: center;
    gap: 25px;
}

.notification {
    font-size: 22px;
    cursor: pointer;
}

.admin{
    font-weight: bold;
    cursor: pointer;
}

.menu {
    font-size: 26px;
    cursor: pointer;
}

/* Contenu */
.content {
    padding: 25px;
}

.heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
}

.heading h1 {
    font-size: 30px;
}

.heading p {
    color: #71809b;
    margin-top: 5px;
}

button {
    padding: 12px 18px;
    border: 1px solid #d5deeb;
    background: white;
    border-radius: 8px;
    cursor: pointer;
}

/* Cartes statistiques */
.stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin-bottom: 25px;
}





/* Panneaux */
.panels {
    display: grid;
    grid-template-columns: 1.5fr 1fr;
    gap: 18px;
    margin-bottom: 20px;
}

.bottom-panels {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
}

.panel {
    background: rgba(255,255,255,.78);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255,255,255,.9);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 5px 20px rgba(31,54,91,.06);
}

.panel h2,
.panel h3 {
    margin-bottom: 15px;
}

.panel p {
    color: #75819a;
}

.placeholder {
    margin-top: 18px;
    min-height: 130px;
    background: rgba(239,243,250,.8);
    border: 1px dashed #c5d0e0;
    border-radius: 9px;
    display: flex;
    justify-content: center;
    align-items: center;
    color: #71809b;
}

/* Adaptation mobile */
@media screen and (max-width: 1000px) {
    .stats {
        grid-template-columns: repeat(2, 1fr);
    }

    .bottom-panels {
        grid-template-columns: 1fr 1fr;
    }
}

@media screen and (max-width: 650px) {
    .sidebar {
        width: 65px;
        overflow: hidden;
    }

    .sidebar .logo {
        font-size: 0;
        padding: 25px 10px;
    }

    .sidebar .logo small {
        display: none;
    }

    .sidebar nav a {
        font-size: 0;
        padding: 18px;
    }

    .sidebar nav a:first-letter {
        font-size: 20px;
    }

    .logout {
        font-size: 0;
    }

    .main {
        margin-left: 65px;
        width: calc(100% - 65px);
    }

    .content {
        padding: 12px;
    }

    .heading {
        align-items: flex-start;
        gap: 10px;
    }

    .heading h1 {
        font-size: 22px;
    }

    .stats {
        grid-template-columns: 1fr;
    }

    .panels,
    .bottom-panels {
        grid-template-columns: 1fr;
    }

    .stat h2 {
        font-size: 21px;
    }
}

/* Barre de défilement transparente */
.sidebar nav {
    scrollbar-width: thin;
    scrollbar-color: rgba(255,255,255,0.25) transparent;
}

.sidebar nav::-webkit-scrollbar {
    width: 6px;
}

.sidebar nav::-webkit-scrollbar-track {
    background: transparent;
}

.sidebar nav::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.25);
    border-radius: 10px;
}

.sidebar nav::-webkit-scrollbar-thumb:hover {
    background: rgba(255,255,255,0.5);
}
</style>
