const API_URL = "/vente";

function getCookie(nom: string): string {
	const cookies = document.cookie.split("; ");
	for (const cookie of cookies) {
		const [cle, valeur] = cookie.split("=");
		if (cle === nom && valeur) {
			return decodeURIComponent(valeur);
		}
	}
	return "";
}

export async function apiGet(chemin: string) {
	const reponse = await fetch(API_URL + chemin);

	if (!reponse.ok) {
		throw new Error("Erreur API : " + reponse.status);
	}
	return reponse.json();
}

export async function apiPost(chemin: string, donnees: object) {
	const reponse = await fetch(API_URL + chemin, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": getCookie("csrftoken"),
		},
		body: JSON.stringify(donnees),
	});

	if (!reponse.ok) {
		throw new Error("Erreur API : " + reponse.status);
	}
	return reponse.json();
}
