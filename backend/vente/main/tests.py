from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase

from main.models import UserProfile


class AuthentificationTests(APITestCase):
    def setUp(self):
        # Pas de UserProfile : il doit être créé à la connexion
        self.user = User.objects.create_user('awa', password='Motdepasse-42')

    def connecter(self, password='Motdepasse-42'):
        return self.client.post('/vente/connexion/', {'username': 'awa', 'password': password}, format='json')

    def test_connexion_puis_acces(self):
        reponse = self.connecter()
        self.assertEqual(reponse.status_code, 200)
        reponse = self.client.get('/vente/moi/', headers={'X-API-Key': reponse.data['api_key']})
        self.assertEqual(reponse.data['username'], 'awa')

    def test_identifiants_invalides(self):
        self.assertEqual(self.connecter('faux').status_code, 401)
        self.assertEqual(self.client.post('/vente/connexion/', {}, format='json').status_code, 400)

    def test_acces_refuse_sans_cle_valide(self):
        for url in ('/vente/moi/', '/vente/users/'):
            self.assertEqual(self.client.get(url).status_code, 401)
            self.assertEqual(self.client.get(url, headers={'X-API-Key': 'x'}).status_code, 401)

    def test_cle_expiree(self):
        cle = self.connecter().data['api_key']
        UserProfile.objects.update(api_key_expiration_datetime=timezone.now() - timedelta(seconds=1))
        self.assertEqual(self.client.get('/vente/moi/', headers={'X-API-Key': cle}).status_code, 401)
        self.assertNotEqual(self.connecter().data['api_key'], cle)

    def test_deconnexion(self):
        entetes = {'X-API-Key': self.connecter().data['api_key']}
        self.assertEqual(self.client.post('/vente/deconnexion/', headers=entetes).status_code, 200)
        self.assertEqual(self.client.get('/vente/moi/', headers=entetes).status_code, 401)

    def test_users_n_expose_pas_les_cles(self):
        cle = self.connecter().data['api_key']
        self.assertNotContains(self.client.get('/vente/users/', headers={'X-API-Key': cle}), cle)

    def test_inscription(self):
        donnees = {'username': 'ali', 'first_name': 'Ali', 'last_name': 'Koné', 'password': 'Motdepasse-42',
                   'is_superuser': True}
        self.assertEqual(self.client.post('/vente/inscription/', donnees, format='json').status_code, 201)
        self.assertFalse(User.objects.get(username='ali').is_superuser)
        self.assertEqual(self.client.post('/vente/inscription/', donnees, format='json').status_code, 400)

    def test_inscription_mot_de_passe_faible(self):
        donnees = {'username': 'ali', 'first_name': 'Ali', 'last_name': 'Koné', 'password': '1234'}
        self.assertEqual(self.client.post('/vente/inscription/', donnees, format='json').status_code, 400)
