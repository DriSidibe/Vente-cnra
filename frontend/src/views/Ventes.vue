
<template>
  <main class="content">

    <!-- EN-TÊTE -->
    <header class="page-header">
      <div>
        <h1>Gestion des ventes</h1>
        <p>Suivez, enregistrez et gérez vos opérations de vente.</p>
      </div>

      <button class="btn-primary" @click="ouvrirFormulaire">
        ＋ Nouvelle vente
      </button>
    </header>

    <!-- MESSAGE -->
    <div v-if="erreur" class="alert-error">
      {{ erreur }}
    </div>

    <div v-if="chargement" class="loading">
      Chargement des données...
    </div>

    <!-- STATISTIQUES -->
    <section class="stats-grid">

      <div class="stat-card">
        <div class="stat-icon blue">🛒</div>
        <div>
          <p>Total des ventes</p>
          <h2>{{ ventes.length }}</h2>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon green">💰</div>
        <div>
          <p>Chiffre d'affaires</p>
          <h2>{{ formatPrix(chiffreAffaires) }}</h2>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon orange">⏳</div>
        <div>
          <p>Ventes en attente</p>
          <h2>{{ ventesEnAttente }}</h2>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon purple">✓</div>
        <div>
          <p>Ventes validées</p>
          <h2>{{ ventesValidees }}</h2>
        </div>
      </div>

    </section>

    <!-- LISTE DES VENTES -->
    <section class="table-container">

      <div class="table-header">
        <div>
          <h2>Liste des ventes</h2>
          <p>Historique de toutes les transactions.</p>
        </div>

        <div class="filters">
          <input
            v-model="recherche"
            type="text"
            placeholder="Rechercher une vente..."
          >

          <select v-model="filtreStatut">
            <option value="">Tous les statuts</option>
            <option value="Payée">Payée</option>
            <option value="En attente">En attente</option>
            <option value="Annulée">Annulée</option>
          </select>

          <button class="btn-refresh" @click="chargerDonnees">
            ↻ Actualiser
          </button>
        </div>
      </div>

      <div class="table-responsive">
        <table>
          <thead>
            <tr>
              <th>N° Vente</th>
              <th>Client</th>
              <th>Date</th>
              <th>Montant</th>
              <th>Paiement</th>
              <th>Statut</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="vente in ventesFiltrees"
              :key="vente.id"
            >
              <td class="vente-id">#V-{{ vente.id }}</td>
              <td>{{ vente.client }}</td>
              <td>{{ formaterDate(vente.date) }}</td>
              <td class="montant">
                {{ formatPrix(vente.montant) }}
              </td>
              <td>{{ vente.paiement }}</td>

              <td>
                <span
                  class="status"
                  :class="classeStatut(vente.statut)"
                >
                  {{ vente.statut }}
                </span>
              </td>

              <td>
                <div class="actions">
                  <button
                    class="action-btn view"
                    title="Voir les détails"
                    @click="voirVente(vente)"
                  >👁</button>

                  <button
                    class="action-btn delete"
                    title="Supprimer"
                    @click="supprimerVente(vente.id)"
                  >🗑</button>
                </div>
              </td>
            </tr>

            <tr v-if="!chargement && ventesFiltrees.length === 0">
              <td colspan="7" class="empty">
                Aucune vente trouvée.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </section>

    <!-- FORMULAIRE NOUVELLE VENTE -->
    <div
      v-if="afficherFormulaire"
      class="modal-overlay"
      @click.self="fermerFormulaire"
    >
      <div class="modal">

        <div class="modal-header">
          <div>
            <h2>Nouvelle vente</h2>
            <p>Enregistrer une nouvelle transaction.</p>
          </div>

          <button class="close-btn" @click="fermerFormulaire">
            ✕
          </button>
        </div>

        <form @submit.prevent="ajouterVente">

          <!-- CLIENT -->
          <div class="form-group">
            <label>Nom du client</label>
            <input
              v-model.trim="nouvelleVente.client"
              type="text"
              placeholder="Nom du client"
              required
            >
          </div>

          <!-- PRODUITS -->
          <div class="product-selection">
            <h3>Produits vendus</h3>

            <div class="form-row">
              <div class="form-group">
                <label>Choisir un produit</label>

                <select
                  v-model.number="produitSelectionneId"
                >
                  <option :value="0">Sélectionner un produit</option>

                  <option
                    v-for="produit in produitsDisponibles"
                    :key="produit.id"
                    :value="produit.id"
                  >
                    {{ produit.nom }} - {{ formatPrix(produit.prix_vente) }}
                    (Stock : {{ produit.quantite }})
                  </option>
                </select>
              </div>

              <div class="form-group quantity-group">
                <label>Quantité</label>
                <input
                  v-model.number="quantiteSelectionnee"
                  type="number"
                  min="1"
                >
              </div>
            </div>

            <button
              type="button"
              class="btn-add-product"
              @click="ajouterProduit"
            >
              ＋ Ajouter ce produit
            </button>

            <div class="cart-table" v-if="nouvelleVente.lignes.length">
              <table>
                <thead>
                  <tr>
                    <th>Produit</th>
                    <th>Quantité</th>
                    <th>Prix unitaire</th>
                    <th>Sous-total</th>
                    <th></th>
                  </tr>
                </thead>

                <tbody>
                  <tr
                    v-for="ligne in nouvelleVente.lignes"
                    :key="ligne.produit_id"
                  >
                    <td>{{ ligne.produit }}</td>
                    <td>{{ ligne.quantite }}</td>
                    <td>{{ formatPrix(ligne.prix_unitaire) }}</td>
                    <td>{{ formatPrix(ligne.sous_total) }}</td>
                    <td>
                      <button
                        type="button"
                        class="action-btn delete"
                        @click="retirerProduit(ligne.produit_id)"
                      >✕</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <p v-else class="empty-cart">
              Aucun produit ajouté à cette vente.
            </p>

            <div class="total-box">
              <span>Montant total</span>
              <strong>{{ formatPrix(totalVente) }}</strong>
            </div>
          </div>

          <!-- PAIEMENT -->
          <div class="form-group">
            <label>Mode de paiement</label>

            <select v-model="nouvelleVente.paiement" required>
              <option value="">Choisir un mode</option>
              <option value="Espèces">Espèces</option>
              <option value="Orange Money">Orange Money</option>
              <option value="MTN Money">MTN Money</option>
              <option value="Wave">Wave</option>
              <option value="Virement bancaire">Virement bancaire</option>
            </select>
          </div>

          <!-- STATUT -->
          <div class="form-group">
            <label>Statut de la vente</label>

            <select v-model="nouvelleVente.statut">
              <option value="Payée">Payée</option>
              <option value="En attente">En attente</option>
              <option value="Annulée">Annulée</option>
            </select>
          </div>

          <div v-if="erreurFormulaire" class="alert-error">
            {{ erreurFormulaire }}
          </div>

          <div class="modal-actions">
            <button
              type="button"
              class="btn-cancel"
              @click="fermerFormulaire"
            >
              Annuler
            </button>

            <button
              type="submit"
              class="btn-primary"
              :disabled="enregistrement"
            >
              {{ enregistrement ? 'Enregistrement...' : 'Enregistrer la vente' }}
            </button>
          </div>

        </form>
      </div>
    </div>

    <!-- DETAILS VENTE -->
    <div
      v-if="venteSelectionnee"
      class="modal-overlay"
      @click.self="venteSelectionnee = null"
    >
      <div class="modal">

        <div class="modal-header">
          <div>
            <h2>Détails de la vente #V-{{ venteSelectionnee.id }}</h2>
            <p>Informations de la transaction.</p>
          </div>

          <button class="close-btn" @click="venteSelectionnee = null">
            ✕
          </button>
        </div>

        <div class="details">
          <p><strong>Client :</strong> {{ venteSelectionnee.client }}</p>
          <p><strong>Date :</strong> {{ formaterDate(venteSelectionnee.date) }}</p>
          <p><strong>Montant :</strong> {{ formatPrix(venteSelectionnee.montant) }}</p>
          <p><strong>Paiement :</strong> {{ venteSelectionnee.paiement }}</p>
          <p><strong>Statut :</strong> {{ venteSelectionnee.statut }}</p>
        </div>

        <h3>Produits de la vente</h3>

        <div class="table-responsive">
          <table>
            <thead>
              <tr>
                <th>Produit</th>
                <th>Quantité</th>
                <th>Prix</th>
                <th>Total</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="ligne in venteSelectionnee.lignes"
                :key="ligne.id"
              >
                <td>{{ ligne.produit }}</td>
                <td>{{ ligne.quantite }}</td>
                <td>{{ formatPrix(ligne.prix_unitaire) }}</td>
                <td>{{ formatPrix(ligne.sous_total) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </div>

  </main>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

import {
  apiGet,
  apiPost,
  apiDelete,
  ApiError
} from '@/utils/scripts/api'


// ==========================================
// TYPESCRIPT : INTERFACES
// ==========================================

type StatutVente = 'Payée' | 'En attente' | 'Annulée'

type ModePaiement =
  | 'Espèces'
  | 'Orange Money'
  | 'MTN Money'
  | 'Wave'
  | 'Virement bancaire'

interface Produit {
  id: number
  nom: string
  reference: string
  categorie: string
  prix_vente: string | number
  quantite: number
  actif: boolean
}

interface LigneVente {
  id: number
  produit_id: number
  produit: string
  reference: string
  quantite: number
  prix_unitaire: string | number
  sous_total: string | number
}

interface Vente {
  id: number
  client: string
  date: string
  montant: string | number
  paiement: ModePaiement
  statut: StatutVente
  lignes: LigneVente[]
}

interface LigneVenteFormulaire {
  produit_id: number
  produit: string
  quantite: number
  prix_unitaire: number
  sous_total: number
}

interface NouvelleVente {
  client: string
  paiement: ModePaiement | ''
  statut: StatutVente
  lignes: LigneVenteFormulaire[]
}

interface CreationVente {
  client: string
  paiement: ModePaiement
  statut: StatutVente
  lignes: {
    produit_id: number
    quantite: number
  }[]
}

interface StatistiquesVente {
  total_ventes: number
  chiffre_affaires: string
  ventes_en_attente: number
  ventes_validees: number
}


// ==========================================
// ÉTATS
// ==========================================

const ventes = ref<Vente[]>([])
const produits = ref<Produit[]>([])

const chargement = ref(false)
const enregistrement = ref(false)

const afficherFormulaire = ref(false)

const recherche = ref('')
const filtreStatut = ref('')

const erreur = ref('')
const erreurFormulaire = ref('')

const venteSelectionnee = ref<Vente | null>(null)

const produitSelectionneId = ref<number>(0)
const quantiteSelectionnee = ref<number>(1)

const nouvelleVente = ref<NouvelleVente>({
  client: '',
  paiement: '',
  statut: 'Payée',
  lignes: []
})


// ==========================================
// CHARGEMENT DES DONNÉES
// ==========================================

async function chargerDonnees(): Promise<void> {
  chargement.value = true
  erreur.value = ''

  try {
    const [ventesAPI, produitsAPI] = await Promise.all([
      apiGet<Vente[]>('/ventes/'),
      apiGet<Produit[]>('/produits/')
    ])

    ventes.value = ventesAPI
    produits.value = produitsAPI.filter(produit => produit.actif)

  } catch (error: unknown) {
    erreur.value = obtenirMessageErreur(error)
  } finally {
    chargement.value = false
  }
}


// ==========================================
// STATISTIQUES
// ==========================================

const chiffreAffaires = computed<number>(() => {
  return ventes.value
    .filter(vente => vente.statut === 'Payée')
    .reduce((total, vente) => total + Number(vente.montant), 0)
})

const ventesEnAttente = computed<number>(() => {
  return ventes.value.filter(
    vente => vente.statut === 'En attente'
  ).length
})

const ventesValidees = computed<number>(() => {
  return ventes.value.filter(
    vente => vente.statut === 'Payée'
  ).length
})


// ==========================================
// RECHERCHE ET FILTRAGE
// ==========================================

const ventesFiltrees = computed<Vente[]>(() => {
  return ventes.value.filter(vente => {

    const terme = recherche.value.toLowerCase().trim()

    const rechercheOK =
      vente.client.toLowerCase().includes(terme) ||
      String(vente.id).includes(terme)

    const statutOK =
      !filtreStatut.value ||
      vente.statut === filtreStatut.value

    return rechercheOK && statutOK
  })
})


// ==========================================
// PRODUITS DISPONIBLES
// ==========================================

const produitsDisponibles = computed<Produit[]>(() => {
  return produits.value.filter(produit => {
    const dejaAjoute = nouvelleVente.value.lignes.find(
      ligne => ligne.produit_id === produit.id
    )

    return produit.quantite > 0 && !dejaAjoute
  })
})


// ==========================================
// CALCUL DU TOTAL
// ==========================================

const totalVente = computed<number>(() => {
  return nouvelleVente.value.lignes.reduce(
    (total, ligne) => total + ligne.sous_total,
    0
  )
})


// ==========================================
// FORMATAGE
// ==========================================

function formatPrix(montant: string | number): string {
  return new Intl.NumberFormat('fr-FR', {
    maximumFractionDigits: 0
  }).format(Number(montant)) + ' FCFA'
}

function formaterDate(date: string): string {
  if (!date) return ''

  const [annee, mois, jour] = date.split('-')

  return `${jour}/${mois}/${annee}`
}

function classeStatut(statut: StatutVente): string {
  if (statut === 'Payée') return 'paid'
  if (statut === 'En attente') return 'pending'

  return 'cancelled'
}

function obtenirMessageErreur(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message
  }

  if (error instanceof Error) {
    return error.message
  }

  return 'Une erreur inattendue est survenue.'
}


// ==========================================
// OUVRIR ET FERMER LE FORMULAIRE
// ==========================================

function ouvrirFormulaire(): void {
  erreurFormulaire.value = ''
  afficherFormulaire.value = true
}

function fermerFormulaire(): void {
  afficherFormulaire.value = false
  erreurFormulaire.value = ''

  nouvelleVente.value = {
    client: '',
    paiement: '',
    statut: 'Payée',
    lignes: []
  }

  produitSelectionneId.value = 0
  quantiteSelectionnee.value = 1
}


// ==========================================
// AJOUTER UN PRODUIT AU PANIER
// ==========================================

function ajouterProduit(): void {
  erreurFormulaire.value = ''

  const produit = produits.value.find(
    element => element.id === produitSelectionneId.value
  )

  if (!produit) {
    erreurFormulaire.value = 'Veuillez sélectionner un produit.'
    return
  }

  const quantite = Number(quantiteSelectionnee.value)

  if (!Number.isInteger(quantite) || quantite <= 0) {
    erreurFormulaire.value = 'Veuillez saisir une quantité valide.'
    return
  }

  if (quantite > produit.quantite) {
    erreurFormulaire.value = 'Stock insuffisant.'
    return
  }

  const sousTotal = Number(produit.prix_vente) * quantite

  nouvelleVente.value.lignes.push({
    produit_id: produit.id,
    produit: produit.nom,
    quantite,
    prix_unitaire: Number(produit.prix_vente),
    sous_total: sousTotal
  })

  produitSelectionneId.value = 0
  quantiteSelectionnee.value = 1
}


// ==========================================
// RETIRER UN PRODUIT
// ==========================================

function retirerProduit(produitId: number): void {
  nouvelleVente.value.lignes =
    nouvelleVente.value.lignes.filter(
      ligne => ligne.produit_id !== produitId
    )
}


// ==========================================
// ENREGISTRER UNE VENTE
// ==========================================

async function ajouterVente(): Promise<void> {
  erreurFormulaire.value = ''

  if (!nouvelleVente.value.client.trim()) {
    erreurFormulaire.value = 'Le nom du client est obligatoire.'
    return
  }

  if (!nouvelleVente.value.paiement) {
    erreurFormulaire.value = 'Veuillez choisir un mode de paiement.'
    return
  }

  if (nouvelleVente.value.lignes.length === 0) {
    erreurFormulaire.value = 'Ajoutez au moins un produit.'
    return
  }

  const donnees: CreationVente = {
    client: nouvelleVente.value.client,
    paiement: nouvelleVente.value.paiement,
    statut: nouvelleVente.value.statut,
    lignes: nouvelleVente.value.lignes.map(ligne => ({
      produit_id: ligne.produit_id,
      quantite: ligne.quantite
    }))
  }

  enregistrement.value = true

  try {
    await apiPost<Vente>('/ventes/', donnees)

    fermerFormulaire()

    await chargerDonnees()

  } catch (error: unknown) {
    erreurFormulaire.value = obtenirMessageErreur(error)
  } finally {
    enregistrement.value = false
  }
}


// ==========================================
// AFFICHER LES DÉTAILS
// ==========================================

function voirVente(vente: Vente): void {
  venteSelectionnee.value = vente
}


// ==========================================
// SUPPRIMER UNE VENTE
// ==========================================

async function supprimerVente(id: number): Promise<void> {

  const confirmation = confirm(
    'Voulez-vous vraiment supprimer cette vente ?'
  )

  if (!confirmation) return

  erreur.value = ''

  try {
    await apiDelete(
      `/supprimer_vente/${id}/`
    )

    if (venteSelectionnee.value?.id === id) {
      venteSelectionnee.value = null
    }

    await chargerDonnees()

  } catch (error: unknown) {
    erreur.value = obtenirMessageErreur(error)
  }
}


// ==========================================
// INITIALISATION
// ==========================================

onMounted(() => {
  chargerDonnees()
})

</script>

<style scoped>
* {
  box-sizing: border-box;
}

.content {
  padding: 25px;
  background: #f5f6fa;
  min-height: 100vh;
  color: #252a35;
}

/* HEADER */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  gap: 15px;
}

.page-header h1 {
  font-size: 27px;
  margin: 0 0 8px;
}

.page-header p,
.table-header p {
  color: #8a8f9c;
  margin: 0;
  font-size: 14px;
}

/* BOUTONS */
.btn-primary {
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 7px;
  padding: 12px 18px;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-primary:disabled {
  opacity: .6;
  cursor: not-allowed;
}

.btn-refresh {
  padding: 10px 14px;
  background: #e8efff;
  color: #2563eb;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

/* MESSAGES */
.alert-error {
  background: #ffe8e8;
  color: #c62828;
  border: 1px solid #ffcaca;
  padding: 12px 15px;
  border-radius: 7px;
  margin-bottom: 18px;
  font-size: 13px;
}

.loading {
  padding: 12px;
  color: #2563eb;
}

/* STATISTIQUES */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 10px;
  padding: 22px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  font-size: 22px;
}

.blue { background: #e6efff; }
.green { background: #e1f8ed; }
.orange { background: #fff1df; }
.purple { background: #f0e9ff; }

.stat-card p {
  font-size: 13px;
  color: #8a8f9c;
  margin: 0 0 8px;
}

.stat-card h2 {
  font-size: 21px;
  margin: 0;
}

/* TABLEAU */
.table-container {
  background: white;
  border-radius: 10px;
  padding: 23px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  margin-bottom: 25px;
}

.table-header h2 {
  font-size: 19px;
  margin: 0 0 7px;
}

.filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filters input,
.filters select {
  padding: 11px;
  border: 1px solid #e1e4eb;
  border-radius: 6px;
  outline: none;
}

.table-responsive {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 850px;
}

th {
  text-align: left;
  padding: 15px 12px;
  background: #f8f9fc;
  color: #777f8e;
  font-size: 12px;
}

td {
  padding: 17px 12px;
  border-bottom: 1px solid #edf0f4;
  font-size: 13px;
}

.vente-id {
  color: #2563eb;
  font-weight: 700;
}

.montant {
  font-weight: 700;
}

.status {
  padding: 6px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.paid {
  background: #e1f8ed;
  color: #16834e;
}

.pending {
  background: #fff1df;
  color: #d17a14;
}

.cancelled {
  background: #ffe5e5;
  color: #d13b3b;
}

.actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  border: none;
  padding: 7px 9px;
  border-radius: 5px;
  cursor: pointer;
}

.view {
  background: #e8efff;
}

.delete {
  background: #ffe8e8;
}

.empty {
  text-align: center;
  padding: 30px;
  color: #999;
}

/* MODALES */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 15px;
  z-index: 1000;
}

.modal {
  width: 100%;
  max-width: 650px;
  background: white;
  border-radius: 12px;
  padding: 25px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 25px;
}

.modal-header h2 {
  margin: 0 0 7px;
  font-size: 21px;
}

.modal-header p {
  color: #888;
  font-size: 13px;
  margin: 0;
}

.close-btn {
  border: none;
  background: #f1f2f5;
  padding: 8px 11px;
  border-radius: 5px;
  cursor: pointer;
}

.form-group {
  margin-bottom: 17px;
  width: 100%;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 12px;
  border: 1px solid #dddfe5;
  border-radius: 6px;
  outline: none;
  background: white;
}

.form-group input:focus,
.form-group select:focus {
  border-color: #2563eb;
}

.form-row {
  display: flex;
  gap: 15px;
}

.quantity-group {
  max-width: 130px;
}

.product-selection {
  padding: 18px;
  background: #f8f9fc;
  border-radius: 8px;
  margin-bottom: 20px;
}

.product-selection h3 {
  font-size: 15px;
  margin: 0 0 18px;
}

.btn-add-product {
  padding: 10px 15px;
  background: #e8efff;
  color: #2563eb;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.cart-table {
  margin-top: 18px;
  overflow-x: auto;
}

.cart-table table {
  min-width: 550px;
  background: white;
}

.cart-table th,
.cart-table td {
  padding: 10px;
}

.empty-cart {
  color: #999;
  font-size: 13px;
  text-align: center;
  padding: 15px;
}

.total-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 17px;
  margin-top: 15px;
  background: white;
  border-radius: 7px;
}

.total-box strong {
  color: #2563eb;
  font-size: 19px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 25px;
}

.btn-cancel {
  background: #f0f1f4;
  border: none;
  border-radius: 7px;
  padding: 12px 18px;
  cursor: pointer;
}

.details p {
  padding: 12px 0;
  border-bottom: 1px solid #eee;
  font-size: 14px;
}

/* RESPONSIVE */
@media (max-width: 1000px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 650px) {
  .content {
    padding: 15px;
  }

  .page-header,
  .table-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .filters {
    width: 100%;
    flex-direction: column;
  }

  .filters input,
  .filters select {
    width: 100%;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .form-row {
    flex-direction: column;
    gap: 0;
  }

  .quantity-group {
    max-width: 100%;
  }

  .modal-actions {
    flex-direction: column;
  }
}
</style>
