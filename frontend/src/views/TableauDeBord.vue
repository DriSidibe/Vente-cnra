<script setup lang="ts">
import StatisticsCharts from '@/components/subcomponents/statistics-charts.vue'
</script>

<template>
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
            <StatisticsCharts :valeur="1250000" unite="FCFA" message="Chiffre d'affaires" color="blue" />
            <StatisticsCharts :valeur="125" message="Ventes réalisées" color="green" />
            <StatisticsCharts :valeur="320" message="Produits en stock" color="orange" />
            <StatisticsCharts :valeur="48" message="Clients enregistrés" color="purple" />
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
</template>

<style scoped>
/* Réinitialisation */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'roboto', sans-serif;
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
}
</style>
