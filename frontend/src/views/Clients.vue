
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  apiGet,
  apiPost,
  apiPut,
  apiDelete,
  ApiError
} from '@/utils/scripts/api'

// ==========================================
// INTERFACE UTILISATEUR
// ==========================================

interface Utilisateur {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  is_active: boolean
  is_superuser: boolean
}

interface FormulaireClient {
  username: string
  first_name: string
  last_name: string
  email: string
  password: string
  is_active: boolean
}

// ==========================================
// VARIABLES
// ==========================================

const clients = ref<Utilisateur[]>([])

const recherche = ref('')
const filtreStatut = ref('tous')

const chargement = ref(false)
const enregistrement = ref(false)

const erreur = ref('')
const succes = ref('')

const afficherModal = ref(false)
const modeModification = ref(false)
const clientSelectionne = ref<number | null>(null)

const formulaire = ref<FormulaireClient>({
  username: '',
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  is_active: true
})

// ==========================================
// GESTION DES ERREURS
// ==========================================

function afficherErreur(error: unknown, messageDefaut: string): void {
  if (error instanceof ApiError) {
    erreur.value = error.message
  } else if (error instanceof Error) {
    erreur.value = error.message
  } else {
    erreur.value = messageDefaut
  }
}

// ==========================================
// RÉINITIALISER LE FORMULAIRE
// ==========================================

function reinitialiserFormulaire(): void {
  formulaire.value = {
    username: '',
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    is_active: true
  }

  clientSelectionne.value = null
  modeModification.value = false
}

// ==========================================
// CHARGER LES CLIENTS
// ==========================================

async function chargerClients(): Promise<void> {
  chargement.value = true
  erreur.value = ''

  try {
    const reponse = await apiGet<Utilisateur[]>('/clients/')

    clients.value = reponse.filter(
      utilisateur => !utilisateur.is_superuser
    )
  } catch (error: unknown) {
    afficherErreur(error, 'Impossible de charger les clients.')
  } finally {
    chargement.value = false
  }
}

// ==========================================
// OUVRIR LE FORMULAIRE D'AJOUT
// ==========================================

function ouvrirAjout(): void {
  erreur.value = ''
  succes.value = ''

  reinitialiserFormulaire()
  afficherModal.value = true
}

// ==========================================
// OUVRIR LE FORMULAIRE DE MODIFICATION
// ==========================================

function ouvrirModification(client: Utilisateur): void {
  erreur.value = ''
  succes.value = ''

  modeModification.value = true
  clientSelectionne.value = client.id

  formulaire.value = {
    username: client.username,
    first_name: client.first_name,
    last_name: client.last_name,
    email: client.email,
    password: '',
    is_active: client.is_active
  }

  afficherModal.value = true
}

// ==========================================
// FERMER LE FORMULAIRE
// ==========================================

function fermerModal(): void {
  afficherModal.value = false
  reinitialiserFormulaire()
  erreur.value = ''
}

// ==========================================
// AJOUTER OU MODIFIER UN CLIENT
// ==========================================

async function enregistrerClient(): Promise<void> {
  erreur.value = ''
  succes.value = ''

  const donnees = {
    username: formulaire.value.username.trim(),
    first_name: formulaire.value.first_name.trim(),
    last_name: formulaire.value.last_name.trim(),
    email: formulaire.value.email.trim(),
    password: formulaire.value.password,
    is_active: formulaire.value.is_active
  }

  if (
    !donnees.username ||
    !donnees.first_name ||
    !donnees.last_name ||
    !donnees.email
  ) {
    erreur.value = 'Veuillez remplir tous les champs obligatoires.'
    return
  }

  if (!modeModification.value && donnees.password.length < 8) {
    erreur.value = 'Le mot de passe doit contenir au moins 8 caractères.'
    return
  }

  if (
    modeModification.value &&
    donnees.password.trim() !== '' &&
    donnees.password.length < 8
  ) {
    erreur.value = 'Le nouveau mot de passe doit contenir au moins 8 caractères.'
    return
  }

  enregistrement.value = true

  try {
    if (modeModification.value && clientSelectionne.value !== null) {
      const donneesModification: Record<string, unknown> = {
        username: donnees.username,
        first_name: donnees.first_name,
        last_name: donnees.last_name,
        email: donnees.email,
        is_active: donnees.is_active
      }

      // Envoyer le mot de passe uniquement s'il est renseigné.
      if (donnees.password.trim()) {
        donneesModification.password = donnees.password
      }

      await apiPut(
        `/modifier_client/${clientSelectionne.value}/`,
        donneesModification
      )

      succes.value = 'Client modifié avec succès.'
    } else {
      await apiPost('/ajouter_client/', donnees)

      succes.value = 'Client ajouté avec succès.'
    }

    afficherModal.value = false
    reinitialiserFormulaire()

    await chargerClients()
  } catch (error: unknown) {
    afficherErreur(
      error,
      'Une erreur est survenue pendant l’enregistrement.'
    )
  } finally {
    enregistrement.value = false
  }
}

// ==========================================
// SUPPRIMER UN CLIENT
// ==========================================

async function supprimerClient(client: Utilisateur): Promise<void> {
  const confirmation = window.confirm(
    `Voulez-vous vraiment supprimer le client ${client.username} ?`
  )

  if (!confirmation) return

  erreur.value = ''
  succes.value = ''

  try {
    await apiDelete(`/supprimer_client/${client.id}/`)

    succes.value = 'Client supprimé avec succès.'

    await chargerClients()
  } catch (error: unknown) {
    afficherErreur(
      error,
      'Impossible de supprimer ce client. Il possède peut-être déjà des ventes.'
    )
  }
}

// ==========================================
// STATISTIQUES
// ==========================================

const totalClients = computed(() => clients.value.length)

const clientsActifs = computed(() =>
  clients.value.filter(client => client.is_active).length
)

const clientsInactifs = computed(() =>
  clients.value.filter(client => !client.is_active).length
)

// ==========================================
// RECHERCHE ET FILTRAGE
// ==========================================

const clientsFiltres = computed(() => {
  const terme = recherche.value.toLowerCase().trim()

  return clients.value.filter(client => {
    const nomComplet =
      `${client.first_name} ${client.last_name}`.toLowerCase()

    const correspondRecherche =
      client.username.toLowerCase().includes(terme) ||
      client.first_name.toLowerCase().includes(terme) ||
      client.last_name.toLowerCase().includes(terme) ||
      client.email.toLowerCase().includes(terme) ||
      nomComplet.includes(terme)

    const correspondStatut =
      filtreStatut.value === 'tous' ||
      (filtreStatut.value === 'actif' && client.is_active) ||
      (filtreStatut.value === 'inactif' && !client.is_active)

    return correspondRecherche && correspondStatut
  })
})

// ==========================================
// INITIALISER LA PAGE
// ==========================================

onMounted(() => {
  chargerClients()
})
</script>

<template>
  <main class="clients-page">

    <!-- EN-TÊTE -->
    <header class="page-header">
      <div>
        <span class="surtitle">GESTION COMMERCIALE</span>
        <h1>Gestion des clients</h1>
        <p>Consultez et suivez les comptes de vos clients.</p>
      </div>

      <div class="header-actions">
        <button class="btn-add" @click="ouvrirAjout">
          <span>＋</span>
          Ajouter un client
        </button>

        <button
          class="btn-refresh"
          @click="chargerClients"
          :disabled="chargement"
        >
          <span>↻</span>
          {{ chargement ? 'Chargement...' : 'Actualiser' }}
        </button>
      </div>
    </header>

    <!-- MESSAGES -->
    <div v-if="erreur && !afficherModal" class="message erreur">
      {{ erreur }}
    </div>

    <div v-if="succes" class="message succes">
      {{ succes }}
    </div>

    <!-- STATISTIQUES -->
    <section class="stats-grid">

      <article class="stat-card">
        <div class="stat-icon total-icon">♙</div>
        <div>
          <span class="stat-label">Total clients</span>
          <h2>{{ totalClients }}</h2>
          <p>Comptes enregistrés</p>
        </div>
      </article>

      <article class="stat-card">
        <div class="stat-icon actif-icon">✓</div>
        <div>
          <span class="stat-label">Clients actifs</span>
          <h2>{{ clientsActifs }}</h2>
          <p>Comptes disponibles</p>
        </div>
      </article>

      <article class="stat-card">
        <div class="stat-icon inactif-icon">!</div>
        <div>
          <span class="stat-label">Clients inactifs</span>
          <h2>{{ clientsInactifs }}</h2>
          <p>Comptes désactivés</p>
        </div>
      </article>

    </section>

    <!-- LISTE DES CLIENTS -->
    <section class="clients-container">

      <div class="section-header">
        <div>
          <h2>Liste des clients</h2>
          <p>Retrouvez les informations de vos clients.</p>
        </div>

        <span class="result-count">
          {{ clientsFiltres.length }} résultat(s)
        </span>
      </div>

      <!-- RECHERCHE ET FILTRE -->
      <div class="toolbar">

        <div class="search-box">
          <span class="search-icon">⌕</span>

          <input
            v-model="recherche"
            type="text"
            placeholder="Rechercher un client..."
          />

          <button
            v-if="recherche"
            class="clear-search"
            @click="recherche = ''"
            aria-label="Effacer la recherche"
          >
            ×
          </button>
        </div>

        <select v-model="filtreStatut" class="filter-select">
          <option value="tous">Tous les clients</option>
          <option value="actif">Clients actifs</option>
          <option value="inactif">Clients inactifs</option>
        </select>

      </div>

      <!-- CHARGEMENT -->
      <div v-if="chargement" class="loading-state">
        <div class="loader"></div>
        <p>Chargement des clients...</p>
      </div>

      <!-- TABLEAU -->
      <div v-else-if="clientsFiltres.length > 0" class="table-wrapper">

        <table>
          <thead>
            <tr>
              <th>CLIENT</th>
              <th>IDENTIFIANT</th>
              <th>ADRESSE E-MAIL</th>
              <th>STATUT</th>
              <th>ACTIONS</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="client in clientsFiltres"
              :key="client.id"
            >

              <td>
                <div class="client-info">

                  <div class="avatar">
                    {{
                      (client.first_name || client.username)
                        .charAt(0)
                        .toUpperCase()
                    }}
                  </div>

                  <div class="client-name">
                    <strong>
                      {{
                        `${client.first_name} ${client.last_name}`.trim()
                        || client.username
                      }}
                    </strong>

                    <span>Client #{{ client.id }}</span>
                  </div>

                </div>
              </td>

              <td>
                <span class="username">
                  @{{ client.username }}
                </span>
              </td>

              <td>
                <span class="email">
                  {{ client.email || 'Non renseigné' }}
                </span>
              </td>

              <td>
                <span
                  class="status-badge"
                  :class="client.is_active ? 'status-active' : 'status-inactive'"
                >
                  <span class="status-dot"></span>
                  {{ client.is_active ? 'Actif' : 'Inactif' }}
                </span>
              </td>

              <td>
                <div class="actions-cell">

                  <button
                    class="btn-edit"
                    @click="ouvrirModification(client)"
                    title="Modifier ce client"
                  >
                    ✎ Modifier
                  </button>

                  <button
                    class="btn-delete"
                    @click="supprimerClient(client)"
                    title="Supprimer ce client"
                  >
                    🗑 Supprimer
                  </button>

                </div>
              </td>

            </tr>
          </tbody>
        </table>

      </div>

      <!-- AUCUN CLIENT -->
      <div v-else-if="!chargement" class="empty-state">
        <div class="empty-icon">♙</div>

        <h3>Aucun client trouvé</h3>

        <p>
          {{
            recherche || filtreStatut !== 'tous'
              ? 'Aucun client ne correspond à votre recherche.'
              : 'Aucun client n’est enregistré pour le moment.'
          }}
        </p>

        <button
          v-if="recherche || filtreStatut !== 'tous'"
          class="btn-reset"
          @click="recherche = ''; filtreStatut = 'tous'"
        >
          Réinitialiser les filtres
        </button>

        <button
          v-else
          class="btn-reset"
          @click="ouvrirAjout"
        >
          Ajouter le premier client
        </button>
      </div>

    </section>

    <!-- FENÊTRE AJOUT / MODIFICATION -->
    <div
      v-if="afficherModal"
      class="modal-overlay"
      @click.self="fermerModal"
    >
      <div class="modal-content">

        <div class="modal-header">
          <div>
            <span class="surtitle">GESTION DES CLIENTS</span>

            <h2>
              {{ modeModification ? 'Modifier un client' : 'Ajouter un client' }}
            </h2>

            <p>
              {{
                modeModification
                  ? 'Modifiez les informations du client.'
                  : 'Renseignez les informations du nouveau client.'
              }}
            </p>
          </div>

          <button
            class="modal-close"
            type="button"
            @click="fermerModal"
          >
            ×
          </button>
        </div>

        <form @submit.prevent="enregistrerClient">

          <div class="form-grid">

            <div class="form-group">
              <label>Nom *</label>
              <input
                v-model="formulaire.last_name"
                type="text"
                placeholder="Nom du client"
                required
              />
            </div>

            <div class="form-group">
              <label>Prénom *</label>
              <input
                v-model="formulaire.first_name"
                type="text"
                placeholder="Prénom du client"
                required
              />
            </div>

            <div class="form-group">
              <label>Nom d'utilisateur *</label>
              <input
                v-model="formulaire.username"
                type="text"
                placeholder="Identifiant"
                required
              />
            </div>

            <div class="form-group">
              <label>Adresse e-mail *</label>
              <input
                v-model="formulaire.email"
                type="email"
                placeholder="exemple@email.com"
                required
              />
            </div>

            <div class="form-group full-width">
              <label>
                Mot de passe
                {{
                  modeModification
                    ? '(laisser vide pour conserver l’ancien)'
                    : '*'
                }}
              </label>

              <input
                v-model="formulaire.password"
                type="password"
                :placeholder="
                  modeModification
                    ? 'Nouveau mot de passe (facultatif)'
                    : 'Mot de passe (8 caractères minimum)'
                "
                :required="!modeModification"
                minlength="8"
              />
            </div>

            <div class="form-group full-width">
              <label>Statut du compte</label>

              <select v-model="formulaire.is_active">
                <option :value="true">Actif</option>
                <option :value="false">Inactif</option>
              </select>
            </div>

          </div>

          <div v-if="erreur" class="message erreur modal-error">
            {{ erreur }}
          </div>

          <div class="modal-actions">
            <button
              type="button"
              class="btn-cancel"
              @click="fermerModal"
              :disabled="enregistrement"
            >
              Annuler
            </button>

            <button
              type="submit"
              class="btn-submit"
              :disabled="enregistrement"
            >
              {{
                enregistrement
                  ? 'Enregistrement...'
                  : modeModification
                    ? 'Enregistrer les modifications'
                    : 'Ajouter le client'
              }}
            </button>
          </div>

        </form>
      </div>
    </div>

  </main>
</template>

<style scoped>
/* ==========================================
   PAGE PRINCIPALE
========================================== */

.clients-page {
  min-height: 100vh;
  padding: 30px;
  background: #f5f6fa;
  color: #202333;
  font-family: 'Poppins', sans-serif;
}

/* ==========================================
   EN-TÊTE
========================================== */

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.surtitle {
  color: #e52b3c;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2px;
}

.page-header h1 {
  margin: 8px 0;
  font-size: 28px;
  font-weight: 700;
  color: #171a29;
}

.page-header p {
  margin: 0;
  color: #85899b;
  font-size: 14px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-refresh,
.btn-add {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  padding: 12px 18px;
  border: none;
  border-radius: 9px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
}

.btn-refresh {
  background: #e52b3c;
}

.btn-refresh:hover {
  background: #c91e30;
}

.btn-add {
  background: #202333;
}

.btn-add:hover {
  background: #34384d;
}

.btn-refresh:disabled,
.btn-add:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-refresh span,
.btn-add span {
  font-size: 20px;
}

/* ==========================================
   MESSAGES
========================================== */

.message {
  padding: 13px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 13px;
}

.erreur {
  background: #fee2e2;
  color: #b91c1c;
}

.succes {
  background: #dcfce7;
  color: #166534;
}

/* ==========================================
   STATISTIQUES
========================================== */

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 17px;
  padding: 23px;
  background: white;
  border-radius: 13px;
  border: 1px solid #eceef3;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.025);
}

.stat-icon {
  width: 52px;
  height: 52px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 12px;
  font-size: 24px;
  font-weight: 700;
}

.total-icon {
  background: #e9edff;
  color: #5368d5;
}

.actif-icon {
  background: #dcfce7;
  color: #16a34a;
}

.inactif-icon {
  background: #fee2e2;
  color: #dc2626;
}

.stat-label {
  color: #85899b;
  font-size: 12px;
  font-weight: 500;
}

.stat-card h2 {
  margin: 5px 0;
  color: #202333;
  font-size: 25px;
}

.stat-card p {
  margin: 0;
  color: #a1a5b3;
  font-size: 11px;
}

/* ==========================================
   CONTENEUR CLIENTS
========================================== */

.clients-container {
  padding: 25px;
  background: white;
  border: 1px solid #eceef3;
  border-radius: 13px;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.025);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  margin-bottom: 22px;
}

.section-header h2 {
  margin: 0 0 6px;
  color: #202333;
  font-size: 18px;
}

.section-header p {
  margin: 0;
  color: #9296a5;
  font-size: 12px;
}

.result-count {
  padding: 7px 12px;
  background: #f1f2f7;
  color: #62677b;
  border-radius: 20px;
  font-size: 12px;
}

/* ==========================================
   RECHERCHE ET FILTRE
========================================== */

.toolbar {
  display: flex;
  justify-content: space-between;
  gap: 15px;
  margin-bottom: 23px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  max-width: 420px;
  padding: 0 14px;
  border: 1px solid #e7e9ef;
  border-radius: 9px;
  background: #fafbfc;
}

.search-icon {
  color: #9296a5;
  font-size: 22px;
}

.search-box input {
  width: 100%;
  height: 43px;
  border: none;
  outline: none;
  background: transparent;
  color: #202333;
  font-size: 13px;
}

.search-box input::placeholder {
  color: #a8acb8;
}

.clear-search {
  border: none;
  background: transparent;
  color: #9296a5;
  font-size: 21px;
  cursor: pointer;
}

.filter-select {
  min-width: 180px;
  padding: 0 13px;
  border: 1px solid #e7e9ef;
  border-radius: 9px;
  background: #fafbfc;
  color: #555b6e;
  font-size: 13px;
  outline: none;
}

/* ==========================================
   TABLEAU
========================================== */

.table-wrapper {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  white-space: nowrap;
}

thead {
  background: #f8f9fc;
}

th {
  padding: 15px;
  color: #85899b;
  font-size: 10px;
  font-weight: 700;
  text-align: left;
  letter-spacing: 0.7px;
}

td {
  padding: 16px 15px;
  border-bottom: 1px solid #f0f1f5;
  font-size: 13px;
}

tbody tr:hover {
  background: #fafbff;
}

tbody tr:last-child td {
  border-bottom: none;
}

/* ==========================================
   INFORMATIONS CLIENT
========================================== */

.client-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 39px;
  height: 39px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #ffedf0;
  color: #e52b3c;
  font-weight: 700;
  font-size: 15px;
}

.client-name {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.client-name strong {
  color: #303447;
  font-size: 12px;
}

.client-name span {
  color: #a1a5b3;
  font-size: 10px;
}

.username,
.email {
  color: #62677b;
  font-size: 12px;
}

/* ==========================================
   STATUT
========================================== */

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 6px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.status-active {
  background: #e8f8ee;
  color: #168344;
}

.status-inactive {
  background: #feecec;
  color: #cc3030;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
}

/* ==========================================
   ACTIONS DU TABLEAU
========================================== */

.actions-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-edit,
.btn-delete {
  padding: 8px 10px;
  border: none;
  border-radius: 7px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
}

.btn-edit {
  background: #fff0f1;
  color: #e52b3c;
}

.btn-edit:hover {
  background: #e52b3c;
  color: white;
}

.btn-delete {
  background: #f1f2f5;
  color: #555b6e;
}

.btn-delete:hover {
  background: #dc2626;
  color: white;
}

/* ==========================================
   CHARGEMENT
========================================== */

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #9296a5;
  font-size: 13px;
}

.loader {
  width: 35px;
  height: 35px;
  margin-bottom: 15px;
  border: 3px solid #f0dadd;
  border-top-color: #e52b3c;
  border-radius: 50%;
  animation: tourner 0.8s linear infinite;
}

@keyframes tourner {
  to {
    transform: rotate(360deg);
  }
}

/* ==========================================
   ÉTAT VIDE
========================================== */

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 55px 20px;
  text-align: center;
}

.empty-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 65px;
  height: 65px;
  margin-bottom: 15px;
  border-radius: 50%;
  background: #f2f3f8;
  color: #a0a5b4;
  font-size: 30px;
}

.empty-state h3 {
  margin: 0 0 8px;
  color: #303447;
  font-size: 16px;
}

.empty-state p {
  margin: 0;
  color: #9296a5;
  font-size: 12px;
}

.btn-reset {
  margin-top: 18px;
  padding: 10px 15px;
  border: none;
  border-radius: 7px;
  background: #e52b3c;
  color: white;
  font-size: 12px;
  cursor: pointer;
}

/* ==========================================
   FENÊTRE MODALE
========================================== */

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(20, 23, 35, 0.65);
  overflow-y: auto;
}

.modal-content {
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 28px;
  border-radius: 15px;
  background: white;
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 15px;
  margin-bottom: 25px;
}

.modal-header h2 {
  margin: 8px 0;
  color: #202333;
  font-size: 22px;
}

.modal-header p {
  margin: 0;
  color: #9296a5;
  font-size: 12px;
}

.modal-close {
  width: 35px;
  height: 35px;
  border: none;
  border-radius: 8px;
  background: #f1f2f5;
  color: #555b6e;
  font-size: 25px;
  cursor: pointer;
}

.modal-close:hover {
  background: #fee2e2;
  color: #e52b3c;
}

/* ==========================================
   FORMULAIRE
========================================== */

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  color: #45495b;
  font-size: 12px;
  font-weight: 600;
}

.form-group input,
.form-group select {
  width: 100%;
  height: 43px;
  box-sizing: border-box;
  padding: 0 12px;
  border: 1px solid #e5e7ed;
  border-radius: 8px;
  outline: none;
  background: #fafbfc;
  color: #202333;
  font-family: inherit;
  font-size: 13px;
  transition: 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  border-color: #e52b3c;
  background: white;
  box-shadow: 0 0 0 3px rgba(229, 43, 60, 0.08);
}

/* ==========================================
   BOUTONS DU FORMULAIRE
========================================== */

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 25px;
}

.btn-cancel,
.btn-submit {
  padding: 12px 17px;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
}

.btn-cancel {
  background: #f1f2f5;
  color: #555b6e;
}

.btn-cancel:hover {
  background: #e3e5eb;
}

.btn-submit {
  background: #e52b3c;
  color: white;
}

.btn-submit:hover {
  background: #c91e30;
}

.btn-submit:disabled,
.btn-cancel:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.modal-error {
  margin-top: 18px;
}

/* ==========================================
   RESPONSIVE
========================================== */

@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 650px) {
  .clients-page {
    padding: 18px;
  }

  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .page-header h1 {
    font-size: 23px;
  }

  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .header-actions button {
    flex: 1;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .clients-container {
    padding: 17px;
  }

  .section-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .toolbar {
    flex-direction: column;
  }

  .search-box {
    max-width: none;
    box-sizing: border-box;
  }

  .filter-select {
    height: 43px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .full-width {
    grid-column: auto;
  }

  .modal-content {
    padding: 20px;
  }

  .modal-actions {
    flex-direction: column-reverse;
  }

  .modal-actions button {
    width: 100%;
  }
}
</style>
