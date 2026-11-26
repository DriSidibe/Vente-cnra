
<template>
  <main class="produit-page">

    <!-- EN-TÊTE -->
    <header class="page-header">
      <div>
        <h1>Gestion des produits</h1>
        <p>Gérez votre catalogue et suivez votre stock.</p>
      </div>

      <button class="btn-primary" @click="ouvrirAjout">
        <span>＋</span> Ajouter un produit
      </button>
    </header>

    <!-- STATISTIQUES -->
    <section class="stats-grid">
      <article class="stat-card">
        <div class="stat-icon blue">▣</div>
        <div>
          <p>Total produits</p>
          <h2>{{ produits.length }}</h2>
        </div>
      </article>

      <article class="stat-card">
        <div class="stat-icon green">✓</div>
        <div>
          <p>Produits actifs</p>
          <h2>{{ produits.filter(p => p.actif).length }}</h2>
        </div>
      </article>

      <article class="stat-card">
        <div class="stat-icon orange">!</div>
        <div>
          <p>Stock faible</p>
          <h2>{{ produits.filter(p => p.quantite <= p.seuil_alerte).length }}</h2>
        </div>
      </article>

      <article class="stat-card">
        <div class="stat-icon purple">▤</div>
        <div>
          <p>Quantité en stock</p>
          <h2>{{ totalStock }}</h2>
        </div>
      </article>
    </section>

    <!-- BARRE DE RECHERCHE -->
    <section class="products-container">

      <div class="toolbar">
        <div class="search-box">
          <span>⌕</span>
          <input
            v-model="recherche"
            type="search"
            placeholder="Rechercher un produit..."
          />
        </div>

        <select v-model="categorieFiltre" class="filter-select">
          <option value="">Toutes les catégories</option>
          <option
            v-for="categorie in categories"
            :key="categorie"
            :value="categorie"
          >
            {{ categorie }}
          </option>
        </select>

        <button class="btn-refresh" @click="chargerProduits">
          ↻ Actualiser
        </button>
      </div>

      <!-- MESSAGE -->
      <div v-if="erreur" class="message error-message">
        {{ erreur }}
      </div>

      <div v-if="succes" class="message success-message">
        {{ succes }}
      </div>

      <!-- CHARGEMENT -->
      <div v-if="chargement" class="loading">
        Chargement des produits...
      </div>

      <!-- TABLEAU DESKTOP / TABLETTE -->
      <div v-else-if="produitsFiltres.length" class="table-wrapper">
        <table class="products-table">
          <thead>
            <tr>
              <th>Produit</th>
              <th>Référence</th>
              <th>Catégorie</th>
              <th>Prix vente</th>
              <th>Quantité</th>
              <th>Statut</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="produit in produitsFiltres" :key="produit.id">
              <td>
                <div class="product-info">
                  <img
                    v-if="produit.image"
                    :src="imageUrl(produit.image)"
                    alt="Produit"
                    class="product-image"
                  />
                  <div v-else class="no-image">IMG</div>

                  <div>
                    <strong>{{ produit.nom }}</strong>
                    <small>{{ produit.description || 'Aucune description' }}</small>
                  </div>
                </div>
              </td>

              <td>{{ produit.reference }}</td>
              <td>{{ produit.categorie }}</td>
              <td class="price">
                {{ formaterPrix(produit.prix_vente) }}
              </td>

              <td>
                <span
                  class="stock-badge"
                  :class="produit.quantite <= produit.seuil_alerte ? 'low-stock' : 'good-stock'"
                >
                  {{ produit.quantite }}
                </span>
              </td>

              <td>
                <span
                  class="status-badge"
                  :class="produit.actif ? 'active' : 'inactive'"
                >
                  {{ produit.actif ? 'Actif' : 'Inactif' }}
                </span>
              </td>

              <td>
                <div class="actions">
                  <button
                    class="action-btn edit"
                    title="Modifier"
                    @click="ouvrirModification(produit)"
                  >
                    ✎
                  </button>

                  <button
                    class="action-btn delete"
                    title="Supprimer"
                    @click="supprimerProduit(produit)"
                  >
                    🗑
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- CARTES MOBILE -->
      <div v-if="!chargement && produitsFiltres.length" class="mobile-products">
        <article
          v-for="produit in produitsFiltres"
          :key="produit.id"
          class="mobile-product-card"
        >
          <div class="mobile-card-header">
            <img
              v-if="produit.image"
              :src="imageUrl(produit.image)"
              alt="Produit"
            />
            <div v-else class="no-image mobile-no-image">IMG</div>

            <div class="mobile-product-title">
              <h3>{{ produit.nom }}</h3>
              <small>{{ produit.reference }}</small>
              <span
                class="status-badge"
                :class="produit.actif ? 'active' : 'inactive'"
              >
                {{ produit.actif ? 'Actif' : 'Inactif' }}
              </span>
            </div>
          </div>

          <div class="mobile-product-details">
            <div>
              <span>Catégorie</span>
              <strong>{{ produit.categorie }}</strong>
            </div>

            <div>
              <span>Prix de vente</span>
              <strong class="price">{{ formaterPrix(produit.prix_vente) }}</strong>
            </div>

            <div>
              <span>Stock</span>
              <strong
                :class="produit.quantite <= produit.seuil_alerte ? 'text-danger' : ''"
              >
                {{ produit.quantite }}
              </strong>
            </div>
          </div>

          <div class="mobile-card-actions">
            <button
              class="btn-edit"
              @click="ouvrirModification(produit)"
            >
              ✎ Modifier
            </button>

            <button
              class="btn-delete"
              @click="supprimerProduit(produit)"
            >
              🗑 Supprimer
            </button>
          </div>
        </article>
      </div>

      <!-- AUCUN PRODUIT -->
      <div
        v-if="!chargement && produitsFiltres.length === 0"
        class="empty-state"
      >
        <div class="empty-icon">▣</div>
        <h3>Aucun produit trouvé</h3>
        <p>Essayez une autre recherche ou ajoutez un nouveau produit.</p>
      </div>

    </section>

    <!-- MODAL AJOUT / MODIFICATION -->
    <div
      v-if="modalOuverte"
      class="modal-overlay"
      @click.self="fermerModal"
    >
      <section class="product-modal">

        <header class="modal-header">
          <div>
            <h2>{{ modeEdition ? 'Modifier le produit' : 'Ajouter un produit' }}</h2>
            <p>Renseignez les informations du produit.</p>
          </div>

          <button class="close-btn" @click="fermerModal">×</button>
        </header>

        <form @submit.prevent="enregistrerProduit">

          <div class="form-grid">

            <div class="form-group full">
              <label>Nom du produit *</label>
              <input
                v-model="form.nom"
                type="text"
                required
                placeholder="Nom du produit"
              />
            </div>

            <div class="form-group">
              <label>Référence *</label>
              <input
                v-model="form.reference"
                type="text"
                required
                placeholder="Ex : PROD001"
              />
            </div>

            <div class="form-group">
              <label>Catégorie *</label>
              <input
                v-model="form.categorie"
                type="text"
                required
                placeholder="Ex : Informatique"
              />
            </div>

            <div class="form-group full">
              <label>Description</label>
              <textarea
                v-model="form.description"
                rows="3"
                placeholder="Description du produit"
              ></textarea>
            </div>

            <div class="form-group">
              <label>Prix d'achat *</label>
              <input
                v-model.number="form.prix_achat"
                type="number"
                min="0"
                step="0.01"
                required
              />
            </div>

            <div class="form-group">
              <label>Prix de vente *</label>
              <input
                v-model.number="form.prix_vente"
                type="number"
                min="0"
                step="0.01"
                required
              />
            </div>

            <div class="form-group">
              <label>Quantité *</label>
              <input
                v-model.number="form.quantite"
                type="number"
                min="0"
                required
              />
            </div>

            <div class="form-group">
              <label>Seuil d'alerte *</label>
              <input
                v-model.number="form.seuil_alerte"
                type="number"
                min="0"
                required
              />
            </div>

            <div class="form-group full">
              <label>Image du produit</label>
              <input
                type="file"
                accept="image/*"
                @change="selectionnerImage"
              />

              <div v-if="imageApercu" class="image-preview">
                <img :src="imageApercu" alt="Aperçu du produit" />
                <button type="button" @click="retirerImage">
                  Retirer l'image
                </button>
              </div>
            </div>

            <div class="form-group full checkbox-group">
              <label>
                <input v-model="form.actif" type="checkbox" />
                Produit actif
              </label>
            </div>

          </div>

          <div class="modal-actions">
            <button
              type="button"
              class="btn-cancel"
              @click="fermerModal"
            >
              Annuler
            </button>

            <button
              type="submit"
              class="btn-primary"
              :disabled="enregistrement"
            >
              {{ enregistrement ? 'Enregistrement...' : (modeEdition ? 'Enregistrer les modifications' : 'Ajouter le produit') }}
            </button>
          </div>

        </form>
      </section>
    </div>

  </main>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import {
  apiGet,
  apiPostForm,
  apiPatch,
  apiDelete,
} from "@/utils/scripts/api";

interface Produit {
  id: number;
  nom: string;
  reference: string;
  description: string;
  categorie: string;
  prix_achat: string | number;
  prix_vente: string | number;
  quantite: number;
  seuil_alerte: number;
  image: string | null;
  date_ajout?: string;
  date_modification?: string;
  actif: boolean;
}

interface ProduitForm {
  nom: string;
  reference: string;
  description: string;
  categorie: string;
  prix_achat: number;
  prix_vente: number;
  quantite: number;
  seuil_alerte: number;
  actif: boolean;
}

const produits = ref<Produit[]>([]);
const chargement = ref(false);
const enregistrement = ref(false);
const modalOuverte = ref(false);
const modeEdition = ref(false);

const recherche = ref("");
const categorieFiltre = ref("");

const erreur = ref("");
const succes = ref("");

const produitId = ref<number | null>(null);
const fichierImage = ref<File | null>(null);
const imageApercu = ref("");

const BACKEND_URL = "http://127.0.0.1:8000";

const formulaireInitial = (): ProduitForm => ({
  nom: "",
  reference: "",
  description: "",
  categorie: "",
  prix_achat: 0,
  prix_vente: 0,
  quantite: 0,
  seuil_alerte: 5,
  actif: true,
});

const form = ref<ProduitForm>(formulaireInitial());

const categories = computed(() => {
  return [...new Set(
    produits.value
      .map(p => p.categorie)
      .filter(Boolean)
  )].sort();
});

const totalStock = computed(() => {
  return produits.value.reduce(
    (total, produit) => total + Number(produit.quantite || 0),
    0
  );
});

const produitsFiltres = computed(() => {
  const rechercheMin = recherche.value.toLowerCase().trim();

  return produits.value.filter(produit => {
    const correspondRecherche =
      produit.nom.toLowerCase().includes(rechercheMin) ||
      produit.reference.toLowerCase().includes(rechercheMin) ||
      produit.categorie.toLowerCase().includes(rechercheMin);

    const correspondCategorie =
      !categorieFiltre.value ||
      produit.categorie === categorieFiltre.value;

    return correspondRecherche && correspondCategorie;
  });
});

function imageUrl(image: string | null) {
  if (!image) return "";

  if (image.startsWith("http://") || image.startsWith("https://")) {
    return image;
  }

  return `${BACKEND_URL}${image.startsWith("/") ? "" : "/"}${image}`;
}

function formaterPrix(prix: string | number) {
  return Number(prix).toLocaleString("fr-FR", {
    style: "currency",
    currency: "XOF",
    maximumFractionDigits: 0,
  });
}

function afficherSucces(message: string) {
  succes.value = message;
  erreur.value = "";

  window.setTimeout(() => {
    succes.value = "";
  }, 3500);
}

async function chargerProduits() {
  chargement.value = true;
  erreur.value = "";

  try {
    const resultat = await apiGet<Produit[]>("/produits/");
    produits.value = resultat;
  } catch (e) {
    erreur.value = e instanceof Error
      ? e.message
      : "Impossible de charger les produits.";
  } finally {
    chargement.value = false;
  }
}

function ouvrirAjout() {
  modeEdition.value = false;
  produitId.value = null;
  form.value = formulaireInitial();
  fichierImage.value = null;
  imageApercu.value = "";
  erreur.value = "";
  modalOuverte.value = true;
}

function ouvrirModification(produit: Produit) {
  modeEdition.value = true;
  produitId.value = produit.id;

  form.value = {
    nom: produit.nom,
    reference: produit.reference,
    description: produit.description || "",
    categorie: produit.categorie,
    prix_achat: Number(produit.prix_achat),
    prix_vente: Number(produit.prix_vente),
    quantite: Number(produit.quantite),
    seuil_alerte: Number(produit.seuil_alerte),
    actif: produit.actif,
  };

  fichierImage.value = null;
  imageApercu.value = produit.image ? imageUrl(produit.image) : "";
  erreur.value = "";
  modalOuverte.value = true;
}

function selectionnerImage(event: Event) {
  const cible = event.target as HTMLInputElement;
  const fichier = cible.files?.[0];

  if (!fichier) return;

  if (!fichier.type.startsWith("image/")) {
    erreur.value = "Veuillez sélectionner un fichier image valide.";
    cible.value = "";
    return;
  }

  if (imageApercu.value.startsWith("blob:")) {
    URL.revokeObjectURL(imageApercu.value);
  }

  fichierImage.value = fichier;
  imageApercu.value = URL.createObjectURL(fichier);
  erreur.value = "";
}

function retirerImage() {
  if (imageApercu.value.startsWith("blob:")) {
    URL.revokeObjectURL(imageApercu.value);
  }

  fichierImage.value = null;
  imageApercu.value = "";
}

function fermerModal() {
  modalOuverte.value = false;

  if (imageApercu.value.startsWith("blob:")) {
    URL.revokeObjectURL(imageApercu.value);
  }

  fichierImage.value = null;
  imageApercu.value = "";
}

async function enregistrerProduit() {
  if (enregistrement.value) return;

  erreur.value = "";

  const donnees = new FormData();

  donnees.append("nom", form.value.nom);
  donnees.append("reference", form.value.reference);
  donnees.append("description", form.value.description);
  donnees.append("categorie", form.value.categorie);
  donnees.append("prix_achat", String(form.value.prix_achat));
  donnees.append("prix_vente", String(form.value.prix_vente));
  donnees.append("quantite", String(form.value.quantite));
  donnees.append("seuil_alerte", String(form.value.seuil_alerte));
  donnees.append("actif", String(form.value.actif));

  if (fichierImage.value) {
    donnees.append("image", fichierImage.value);
  }

  enregistrement.value = true;

  try {
    if (modeEdition.value && produitId.value !== null) {
      await apiPatch(
        `/produits/${produitId.value}/`,
        donnees
      );

      afficherSucces("Produit modifié avec succès.");
    } else {
      await apiPostForm(
        "/produits/",
        donnees
      );

      afficherSucces("Produit ajouté avec succès.");
    }

    fermerModal();
    await chargerProduits();

  } catch (e) {
    erreur.value = e instanceof Error
      ? e.message
      : "Une erreur est survenue lors de l'enregistrement.";
  } finally {
    enregistrement.value = false;
  }
}

async function supprimerProduit(produit: Produit) {
  const confirmation = window.confirm(
    `Voulez-vous vraiment supprimer le produit "${produit.nom}" ?`
  );

  if (!confirmation) return;

  erreur.value = "";

  try {
    await apiDelete(`/produits/${produit.id}/`);

    produits.value = produits.value.filter(
      p => p.id !== produit.id
    );

    afficherSucces("Produit supprimé avec succès.");

  } catch (e) {
    erreur.value = e instanceof Error
      ? e.message
      : "Impossible de supprimer ce produit.";
  }
}

onMounted(chargerProduits);

onBeforeUnmount(() => {
  if (imageApercu.value.startsWith("blob:")) {
    URL.revokeObjectURL(imageApercu.value);
  }
});
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.produit-page {
  width: 100%;
  min-width: 0;
  padding: 25px;
  color: #202938;
  background: #f5f7fb;
  min-height: 100vh;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 25px;
}

.page-header h1 {
  font-size: 25px;
  margin: 0 0 7px;
  font-weight: 700;
}

.page-header p {
  margin: 0;
  color: #87909e;
  font-size: 14px;
}

.btn-primary {
  border: none;
  background: #168b55;
  color: white;
  padding: 12px 18px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: 0.2s;
}

.btn-primary:hover {
  background: #107246;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary span {
  font-size: 19px;
  margin-right: 5px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
  margin-bottom: 25px;
}

.stat-card {
  background: white;
  border: 1px solid #edf0f5;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  min-width: 0;
}

.stat-icon {
  width: 45px;
  height: 45px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  font-size: 21px;
  font-weight: bold;
  flex-shrink: 0;
}

.blue {
  background: #e9f1ff;
  color: #3278d5;
}

.green {
  background: #e4f8ee;
  color: #168b55;
}

.orange {
  background: #fff2df;
  color: #e69a27;
}

.purple {
  background: #f0eaff;
  color: #8457d6;
}

.stat-card p {
  color: #87909e;
  font-size: 13px;
  margin: 0 0 7px;
}

.stat-card h2 {
  font-size: 23px;
  margin: 0;
}

.products-container {
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #edf0f5;
  min-width: 0;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid #e4e8ef;
  border-radius: 8px;
  padding: 0 13px;
  flex: 1;
  min-width: 150px;
}

.search-box span {
  color: #8993a3;
  font-size: 22px;
}

.search-box input {
  width: 100%;
  border: none;
  outline: none;
  padding: 12px 0;
  font-size: 14px;
  background: transparent;
}

.filter-select {
  min-width: 190px;
  border: 1px solid #e4e8ef;
  border-radius: 8px;
  padding: 0 12px;
  outline: none;
  background: white;
  color: #384354;
}

.btn-refresh {
  padding: 10px 15px;
  border: 1px solid #e4e8ef;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  color: #475467;
}

.btn-refresh:hover {
  background: #f5f7fb;
}

.table-wrapper {
  width: 100%;
  overflow-x: auto;
}

.products-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 850px;
}

.products-table th {
  background: #f8fafc;
  color: #7b8493;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  padding: 15px 12px;
  white-space: nowrap;
}

.products-table td {
  border-bottom: 1px solid #edf0f5;
  padding: 13px 12px;
  font-size: 13px;
  color: #465163;
}

.product-info {
  display: flex;
  align-items: center;
  gap: 11px;
  min-width: 190px;
}

.product-image,
.no-image {
  width: 43px;
  height: 43px;
  border-radius: 7px;
  object-fit: cover;
  flex-shrink: 0;
}

.no-image {
  display: grid;
  place-items: center;
  background: #edf1f5;
  color: #8b95a3;
  font-size: 10px;
  font-weight: bold;
}

.product-info strong {
  display: block;
  color: #263244;
  font-size: 13px;
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-info small {
  display: block;
  color: #9aa2af;
  margin-top: 5px;
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.price {
  color: #168b55;
  font-weight: 700;
  white-space: nowrap;
}

.stock-badge,
.status-badge {
  display: inline-block;
  padding: 5px 9px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.good-stock,
.active {
  background: #e5f8ed;
  color: #168b55;
}

.low-stock {
  background: #fff0e8;
  color: #d65b2b;
}

.inactive {
  background: #eef0f3;
  color: #687386;
}

.actions {
  display: flex;
  gap: 7px;
}

.action-btn {
  width: 31px;
  height: 31px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 15px;
}

.edit {
  color: #2878d0;
  background: #eaf2ff;
}

.delete {
  color: #d84d4d;
  background: #ffeded;
}

.action-btn:hover {
  filter: brightness(0.95);
}

.mobile-products {
  display: none;
}

.empty-state {
  text-align: center;
  padding: 55px 15px;
  color: #8b95a3;
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.empty-state h3 {
  color: #344054;
  margin: 0 0 8px;
}

.empty-state p {
  font-size: 13px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #7b8493;
}

.message {
  padding: 12px 15px;
  border-radius: 7px;
  margin-bottom: 15px;
  font-size: 13px;
}

.error-message {
  background: #fff0f0;
  color: #c83d3d;
}

.success-message {
  background: #e8f8ef;
  color: #168b55;
}

/* MODAL */

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(119, 132, 155, 0.58);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  overflow-y: auto;
}

.product-modal {
  background: white;
  width: 100%;
  max-width: 680px;
  max-height: calc(100vh - 40px);
  overflow-y: auto;
  border-radius: 13px;
  padding: 25px;
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.18);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 22px;
  gap: 15px;
}

.modal-header h2 {
  margin: 0 0 6px;
  font-size: 20px;
}

.modal-header p {
  margin: 0;
  color: #8b95a3;
  font-size: 13px;
}

.close-btn {
  border: none;
  background: #f0f2f5;
  color: #526071;
  width: 32px;
  height: 32px;
  border-radius: 7px;
  font-size: 22px;
  cursor: pointer;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 17px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 7px;
  min-width: 0;
}

.form-group.full {
  grid-column: 1 / -1;
}

.form-group label {
  color: #465163;
  font-size: 13px;
  font-weight: 600;
}

.form-group input:not([type="checkbox"]):not([type="file"]),
.form-group textarea {
  width: 100%;
  padding: 11px 12px;
  border: 1px solid #dfe4eb;
  border-radius: 7px;
  outline: none;
  font-size: 13px;
  font-family: inherit;
  color: #344054;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #168b55;
}

.form-group input[type="file"] {
  font-size: 13px;
  max-width: 100%;
}

.form-group textarea {
  resize: vertical;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 9px;
  cursor: pointer;
}

.image-preview {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.image-preview img {
  width: 85px;
  height: 85px;
  border-radius: 8px;
  object-fit: cover;
}

.image-preview button {
  border: none;
  background: #fff0f0;
  color: #c83d3d;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 25px;
  flex-wrap: wrap;
}

.btn-cancel {
  background: #eef0f3;
  color: #475467;
  border: none;
  border-radius: 7px;
  padding: 11px 17px;
  cursor: pointer;
}

/* TABLETTE */

@media (max-width: 1050px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .produit-page {
    padding: 20px;
  }
}

/* MOBILE */

@media (max-width: 650px) {
  .produit-page {
    padding: 14px;
  }

  .page-header {
    align-items: flex-start;
    flex-direction: column;
    gap: 15px;
  }

  .page-header h1 {
    font-size: 21px;
  }

  .page-header .btn-primary {
    width: 100%;
  }

  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
  }

  .stat-card {
    padding: 13px 10px;
    gap: 9px;
  }

  .stat-icon {
    width: 36px;
    height: 36px;
    font-size: 17px;
  }

  .stat-card p {
    font-size: 11px;
  }

  .stat-card h2 {
    font-size: 19px;
  }

  .products-container {
    padding: 13px;
  }

  .toolbar {
    flex-direction: column;
  }

  .search-box {
    min-height: 43px;
    flex: auto;
  }

  .filter-select,
  .btn-refresh {
    width: 100%;
    min-height: 42px;
  }

  .table-wrapper {
    display: none;
  }

  .mobile-products {
    display: grid;
    gap: 13px;
  }

  .mobile-product-card {
    border: 1px solid #edf0f5;
    border-radius: 10px;
    padding: 14px;
    background: white;
  }

  .mobile-card-header {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .mobile-card-header img,
  .mobile-no-image {
    width: 58px;
    height: 58px;
    object-fit: cover;
    border-radius: 8px;
    flex-shrink: 0;
  }

  .mobile-product-title {
    min-width: 0;
  }

  .mobile-product-title h3 {
    font-size: 14px;
    color: #263244;
    margin: 0 0 5px;
    overflow-wrap: anywhere;
  }

  .mobile-product-title small {
    display: block;
    color: #8993a3;
    margin-bottom: 7px;
  }

  .mobile-product-details {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 13px;
    padding: 14px 0;
    margin-top: 12px;
    border-top: 1px solid #edf0f5;
    border-bottom: 1px solid #edf0f5;
  }

  .mobile-product-details div {
    display: flex;
    flex-direction: column;
    gap: 5px;
    min-width: 0;
  }

  .mobile-product-details span {
    font-size: 11px;
    color: #8993a3;
  }

  .mobile-product-details strong {
    font-size: 13px;
    overflow-wrap: anywhere;
  }

  .mobile-card-actions {
    display: flex;
    gap: 9px;
    margin-top: 13px;
  }

  .mobile-card-actions button {
    flex: 1;
    padding: 10px 5px;
    border: none;
    border-radius: 6px;
    font-size: 12px;
    cursor: pointer;
  }

  .btn-edit {
    background: #eaf2ff;
    color: #2878d0;
  }

  .btn-delete {
    background: #ffeded;
    color: #b60000;
  }

  .product-modal {
    padding: 18px;
  }

  .form-grid {
    grid-template-columns: 1fr;
    gap: 13px;
  }

  .form-group.full {
    grid-column: auto;
  }

  .modal-actions {
    flex-direction: column-reverse;
  }

  .modal-actions button {
    width: 100%;
  }
}

@media (max-width: 380px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .mobile-card-actions {
    flex-direction: column;
  }
}
</style>
