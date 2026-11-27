
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { apiGet, ApiError } from '@/utils/scripts/api'

interface Produit {
  id: number
  nom: string
  reference: string
  description?: string
  categorie: string
  prix_achat: number
  prix_vente: number
  quantite: number
  seuil_alerte: number
  image?: string | null
  actif: boolean
}

type FiltreStock = 'tous' | 'disponible' | 'faible' | 'rupture'

const produits = ref<Produit[]>([])
const recherche = ref('')
const filtreActif = ref<FiltreStock>('tous')
const chargement = ref(false)
const erreur = ref('')
const derniereActualisation = ref('')

// Récupération des produits depuis Django
async function chargerStock() {
  chargement.value = true
  erreur.value = ''

  try {
    const resultat = await apiGet<Produit[]>('/stock/')

    produits.value = Array.isArray(resultat) ? resultat : []
    derniereActualisation.value = new Date().toLocaleTimeString('fr-FR')
  } catch (err) {
    console.error('Erreur de chargement du stock :', err)

    if (err instanceof ApiError) {
      erreur.value = `Erreur ${err.status} : impossible de charger le stock.`
    } else {
      erreur.value = 'Impossible de contacter le serveur.'
    }
  } finally {
    chargement.value = false
  }
}

// Statistiques
const totalProduits = computed(() => produits.value.length)

const quantiteTotale = computed(() =>
  produits.value.reduce((total, produit) => total + Number(produit.quantite || 0), 0)
)

const produitsDisponibles = computed(() =>
  produits.value.filter(produit => produit.quantite > produit.seuil_alerte).length
)

const produitsFaibles = computed(() =>
  produits.value.filter(
    produit => produit.quantite > 0 && produit.quantite <= produit.seuil_alerte
  ).length
)

const produitsEnRupture = computed(() =>
  produits.value.filter(produit => produit.quantite === 0).length
)

// Détermination de l'état du stock
function obtenirStatut(produit: Produit): string {
  if (produit.quantite === 0) return 'Rupture'
  if (produit.quantite <= produit.seuil_alerte) return 'Stock faible'
  return 'Disponible'
}

function classeStatut(produit: Produit): string {
  if (produit.quantite === 0) return 'rupture'
  if (produit.quantite <= produit.seuil_alerte) return 'faible'
  return 'disponible'
}

// Recherche et filtrage
const produitsFiltres = computed(() => {
  const terme = recherche.value.toLowerCase().trim()

  return produits.value.filter(produit => {
    const correspondRecherche =
      produit.nom.toLowerCase().includes(terme) ||
      produit.reference.toLowerCase().includes(terme) ||
      produit.categorie.toLowerCase().includes(terme)

    let correspondFiltre = true

    if (filtreActif.value === 'disponible') {
      correspondFiltre = produit.quantite > produit.seuil_alerte
    } else if (filtreActif.value === 'faible') {
      correspondFiltre =
        produit.quantite > 0 &&
        produit.quantite <= produit.seuil_alerte
    } else if (filtreActif.value === 'rupture') {
      correspondFiltre = produit.quantite === 0
    }

    return correspondRecherche && correspondFiltre
  })
})

function choisirFiltre(filtre: FiltreStock) {
  filtreActif.value = filtre
}

onMounted(() => {
  chargerStock()
})
</script>

<template>
  <main class="content">

    <!-- EN-TÊTE -->
    <header class="page-header">
      <div>
        <h1>Gestion du stock</h1>
        <p>Suivez les quantités disponibles et les alertes de stock.</p>
      </div>

      <button
        class="btn-refresh"
        @click="chargerStock"
        :disabled="chargement"
      >
        <span>{{ chargement ? '⏳' : '↻' }}</span>
        {{ chargement ? 'Actualisation...' : 'Actualiser' }}
      </button>
    </header>

    <!-- STATISTIQUES -->
    <section class="stats-grid">

      <article class="stat-card">
        <div class="stat-icon blue">▣</div>
        <div>
          <p>Total des produits</p>
          <h2>{{ totalProduits }}</h2>
          <small>Produits enregistrés</small>
        </div>
      </article>

      <article class="stat-card">
        <div class="stat-icon purple">▤</div>
        <div>
          <p>Quantité totale</p>
          <h2>{{ quantiteTotale }}</h2>
          <small>Articles en stock</small>
        </div>
      </article>

      <article class="stat-card">
        <div class="stat-icon green">✓</div>
        <div>
          <p>Stock disponible</p>
          <h2>{{ produitsDisponibles }}</h2>
          <small>Produits au-dessus du seuil</small>
        </div>
      </article>

      <article class="stat-card">
        <div class="stat-icon orange">!</div>
        <div>
          <p>Stock faible</p>
          <h2>{{ produitsFaibles }}</h2>
          <small>À réapprovisionner</small>
        </div>
      </article>

      <article class="stat-card">
        <div class="stat-icon red">×</div>
        <div>
          <p>Rupture de stock</p>
          <h2>{{ produitsEnRupture }}</h2>
          <small>Produits indisponibles</small>
        </div>
      </article>

    </section>

    <!-- ALERTE -->
    <div
      v-if="produitsFaibles > 0 || produitsEnRupture > 0"
      class="alert-stock"
    >
      <span class="alert-icon">⚠</span>
      <div>
        <strong>Attention : des produits nécessitent un réapprovisionnement.</strong>
        <p>
          {{ produitsFaibles }} produit(s) avec un stock faible et
          {{ produitsEnRupture }} produit(s) en rupture.
        </p>
      </div>
    </div>

    <!-- TABLEAU DU STOCK -->
    <section class="stock-container">

      <div class="table-header">
        <div>
          <h2>État des stocks</h2>
          <p>Consultez les quantités de tous vos produits.</p>
        </div>
        <span class="product-count">
          {{ produitsFiltres.length }} résultat(s)
        </span>
      </div>

      <!-- RECHERCHE ET FILTRES -->
      <div class="filters">

        <div class="search-box">
          <span>⌕</span>
          <input
            v-model="recherche"
            type="text"
            placeholder="Rechercher un produit, une référence..."
          />
        </div>

        <div class="filter-buttons">
          <button
            :class="{ active: filtreActif === 'tous' }"
            @click="choisirFiltre('tous')"
          >
            Tous
          </button>

          <button
            :class="{ active: filtreActif === 'disponible' }"
            @click="choisirFiltre('disponible')"
          >
            Disponibles
          </button>

          <button
            :class="{ active: filtreActif === 'faible' }"
            @click="choisirFiltre('faible')"
          >
            Stock faible
          </button>

          <button
            :class="{ active: filtreActif === 'rupture' }"
            @click="choisirFiltre('rupture')"
          >
            Rupture
          </button>
        </div>

      </div>

      <!-- ERREUR -->
      <div v-if="erreur" class="error-message">
        {{ erreur }}
        <button @click="chargerStock">Réessayer</button>
      </div>

      <!-- CHARGEMENT -->
      <div v-else-if="chargement && produits.length === 0" class="loading">
        Chargement des données du stock...
      </div>

      <!-- TABLEAU -->
      <div v-else class="table-responsive">

        <table>
          <thead>
            <tr>
              <th>PRODUIT</th>
              <th>RÉFÉRENCE</th>
              <th>CATÉGORIE</th>
              <th>QUANTITÉ</th>
              <th>SEUIL D'ALERTE</th>
              <th>ÉTAT DU STOCK</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="produit in produitsFiltres" :key="produit.id">

              <td>
                <div class="product-name">
                  <div class="product-avatar">
                    {{ produit.nom.charAt(0).toUpperCase() }}
                  </div>
                  <strong>{{ produit.nom }}</strong>
                </div>
              </td>

              <td>
                <span class="reference">{{ produit.reference }}</span>
              </td>

              <td>
                {{ produit.categorie }}
              </td>

              <td>
                <div class="quantity-cell">
                  <strong>{{ produit.quantite }}</strong>
                  <span>unité(s)</span>
                </div>
              </td>

              <td>
                {{ produit.seuil_alerte }}
              </td>

              <td>
                <span class="status-badge" :class="classeStatut(produit)">
                  <span class="status-dot"></span>
                  {{ obtenirStatut(produit) }}
                </span>
              </td>

            </tr>

            <tr v-if="produitsFiltres.length === 0">
              <td colspan="6" class="empty-state">
                <div>📦</div>
                <strong>Aucun produit trouvé</strong>
                <p>Modifiez votre recherche ou votre filtre.</p>
              </td>
            </tr>

          </tbody>
        </table>

      </div>

      <div class="table-footer">
        <span>
          Dernière actualisation :
          {{ derniereActualisation || 'Non disponible' }}
        </span>
        <span>{{ produitsFiltres.length }} produit(s) affiché(s)</span>
      </div>

    </section>

  </main>
</template>

<style scoped>
.content {
  padding: 25px;
  min-height: 100vh;
  background: #f5f6fa;
  color: #202333;
}

/* EN-TÊTE */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 28px;
}

.page-header h1 {
  margin: 0 0 7px;
  font-size: 27px;
  font-weight: 700;
}

.page-header p {
  margin: 0;
  color: #85899a;
  font-size: 14px;
}

.btn-refresh {
  border: none;
  border-radius: 8px;
  padding: 12px 18px;
  background: #e52b3c;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
}

.btn-refresh:hover {
  background: #c91e30;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* STATISTIQUES */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 17px;
  margin-bottom: 25px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.035);
  min-width: 0;
}

.stat-icon {
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 11px;
  font-size: 22px;
  font-weight: bold;
}

.blue {
  background: #e8efff;
  color: #4169d8;
}

.purple {
  background: #f0eaff;
  color: #8155d9;
}

.green {
  background: #e4f8ec;
  color: #16a34a;
}

.orange {
  background: #fff2df;
  color: #ed941d;
}

.red {
  background: #ffe7e9;
  color: #e52b3c;
}

.stat-card p {
  margin: 0 0 5px;
  color: #85899a;
  font-size: 12px;
}

.stat-card h2 {
  margin: 0 0 4px;
  font-size: 23px;
}

.stat-card small {
  color: #a0a3af;
  font-size: 10px;
}

/* ALERTE */
.alert-stock {
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 16px 20px;
  margin-bottom: 25px;
  border: 1px solid #ffe1b3;
  border-radius: 10px;
  background: #fff9ee;
  color: #a96612;
}

.alert-icon {
  font-size: 25px;
}

.alert-stock strong {
  font-size: 14px;
}

.alert-stock p {
  margin: 5px 0 0;
  font-size: 13px;
}

/* CONTENEUR TABLEAU */
.stock-container {
  background: white;
  border-radius: 12px;
  padding: 22px;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.035);
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 22px;
  gap: 15px;
}

.table-header h2 {
  margin: 0 0 6px;
  font-size: 18px;
}

.table-header p {
  margin: 0;
  color: #85899a;
  font-size: 13px;
}

.product-count {
  background: #f0f2f8;
  color: #596078;
  padding: 8px 13px;
  border-radius: 7px;
  font-size: 12px;
}

/* FILTRES */
.filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 20px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 330px;
  max-width: 100%;
  padding: 0 13px;
  height: 42px;
  border: 1px solid #e7e8ed;
  border-radius: 8px;
}

.search-box span {
  color: #85899a;
  font-size: 23px;
}

.search-box input {
  width: 100%;
  border: none;
  outline: none;
  font-size: 13px;
  color: #202333;
}

.filter-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.filter-buttons button {
  border: 1px solid #e7e8ed;
  background: white;
  color: #686d7e;
  padding: 9px 13px;
  border-radius: 7px;
  font-size: 12px;
  cursor: pointer;
  transition: 0.2s;
}

.filter-buttons button:hover,
.filter-buttons button.active {
  background: #e52b3c;
  color: white;
  border-color: #e52b3c;
}

/* TABLEAU */
.table-responsive {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  min-width: 750px;
  border-collapse: collapse;
}

thead {
  background: #f7f8fb;
}

th {
  padding: 15px 13px;
  color: #85899a;
  text-align: left;
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
}

td {
  padding: 15px 13px;
  border-bottom: 1px solid #f0f1f5;
  font-size: 13px;
}

tbody tr:hover {
  background: #fafbfe;
}

.product-name {
  display: flex;
  align-items: center;
  gap: 11px;
  min-width: 150px;
}

.product-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #ffe7e9;
  color: #e52b3c;
  font-weight: 700;
  font-size: 15px;
}

.product-name strong {
  color: #303448;
}

.reference {
  background: #f0f2f8;
  color: #596078;
  padding: 6px 9px;
  border-radius: 5px;
  font-size: 11px;
}

.quantity-cell {
  display: flex;
  align-items: center;
  gap: 5px;
}

.quantity-cell strong {
  font-size: 15px;
}

.quantity-cell span {
  color: #9296a5;
  font-size: 10px;
}

/* BADGES */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 7px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.status-badge.disponible {
  background: #e7f8ed;
  color: #168c46;
}

.disponible .status-dot {
  background: #16a34a;
}

.status-badge.faible {
  background: #fff3df;
  color: #d88714;
}

.faible .status-dot {
  background: #ed941d;
}

.status-badge.rupture {
  background: #ffe7e9;
  color: #d82335;
}

.rupture .status-dot {
  background: #e52b3c;
}

/* ÉTATS */
.loading,
.error-message {
  padding: 30px;
  text-align: center;
  color: #85899a;
  font-size: 14px;
}

.error-message {
  color: #d82335;
}

.error-message button {
  margin-left: 10px;
  border: none;
  background: #e52b3c;
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
}

.empty-state {
  padding: 45px 15px;
  text-align: center;
  color: #85899a;
}

.empty-state div {
  font-size: 35px;
  margin-bottom: 10px;
}

.empty-state strong {
  display: block;
  color: #303448;
}

.empty-state p {
  margin: 7px 0 0;
  font-size: 12px;
}

/* PIED DU TABLEAU */
.table-footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding-top: 17px;
  color: #9296a5;
  font-size: 11px;
}

/* RESPONSIVE */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .content {
    padding: 15px;
  }

  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .filters {
    align-items: stretch;
    flex-direction: column;
  }

  .search-box {
    width: 100%;
  }

  .filter-buttons {
    overflow-x: auto;
    padding-bottom: 5px;
  }

  .filter-buttons button {
    white-space: nowrap;
  }

  .stock-container {
    padding: 15px;
  }

  .table-footer {
    flex-direction: column;
  }
}

@media (max-width: 450px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .table-header {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
