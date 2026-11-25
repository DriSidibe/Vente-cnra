<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { deconnecter, utilisateur } from '@/utils/scripts/auth'

const router = useRouter()

const liens = [
    { route: 'tableau-de-bord', icone: '🏠', texte: 'Tableau de bord' },
    { route: 'ventes', icone: '🛒', texte: 'Ventes' },
    { route: 'produits', icone: '📦', texte: 'Produits' },
    { route: 'categories', icone: '🌐', texte: 'Catégories' },
    { route: 'clients', icone: '👥', texte: 'Clients' },
    { route: 'stock', icone: '📊', texte: 'Stock' },
    { route: 'rapports', icone: '📑', texte: 'Rapports' },
    { route: 'utilisateurs', icone: '👤', texte: 'Utilisateurs' },
    { route: 'parametres', icone: '⚙️', texte: 'Paramètres' },
]

const nomAffiche = computed(() => {
    const u = utilisateur.value
    if (!u) return ''
    return `${u.first_name} ${u.last_name}`.trim() || u.username
})

async function seDeconnecter() {
    try {
        await deconnecter()
    } catch (erreur) {
        console.error('Erreur lors de la déconnexion :', erreur)
    }
    router.push({ name: 'connexion' })
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
            <RouterLink v-for="lien in liens" :key="lien.route" :to="{ name: lien.route }"
                exact-active-class="active">{{ lien.icone }} {{ lien.texte }}</RouterLink>
            <a class="logout" href="#" @click.prevent="seDeconnecter">⏻ Déconnexion</a>
        </nav>

        
    </aside>

    <!-- Contenu principal -->
    <main class="main">

        <header class="topbar">
            <span class="menu">☰</span>
            <div class="user-actions">
            <span class="notification">🔔</span>
            <span class="admin">{{ nomAffiche }} ▼</span>
            </div>
            
        </header>

        <RouterView />
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

/* Structure générale */
.dashboard {
    background: #edf1f8;
    color: #172033;
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

/* Adaptation mobile */
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
