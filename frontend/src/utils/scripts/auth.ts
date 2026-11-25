import { ref } from 'vue';
import { apiGet, apiPost, ApiError, enregistrerCle, lireCle, supprimerCle, type Session, type Utilisateur } from './api';

export const utilisateur = ref<Utilisateur | null>(null);

function ouvrirSession(session: Session) {
	enregistrerCle(session.api_key, session.api_key_expiration_datetime);
	utilisateur.value = session.user;
}

export function fermerSession() {
	supprimerCle();
	utilisateur.value = null;
}

export async function connecter(donnees: { username: string; password: string }) {
	ouvrirSession(await apiPost<Session>("/connexion/", donnees));
}

export async function inscrire(donnees: { username: string; first_name: string; last_name: string; password: string }) {
	ouvrirSession(await apiPost<Session>("/inscription/", donnees));
}

export async function deconnecter() {
	try {
		await apiPost("/deconnexion/");
	} finally {
		fermerSession();
	}
}

export async function verifierSession(): Promise<boolean> {
	if (!lireCle()) {
		utilisateur.value = null;
		return false;
	}
	if (!utilisateur.value) {
		try {
			utilisateur.value = await apiGet<Utilisateur>("/moi/");
		} catch (erreur) {
			if (erreur instanceof ApiError && erreur.status === 401) {
				fermerSession();
			}
			return false;
		}
	}
	return true;
}
