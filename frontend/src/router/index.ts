import { createRouter, createWebHistory } from 'vue-router'
import { definirSurSessionExpiree } from '@/utils/scripts/api'
import { fermerSession, verifierSession } from '@/utils/scripts/auth'
import Connexion from '@/components/Connexion.vue'

declare module 'vue-router' {
  interface RouteMeta {
    titre?: string
    requiertAuth?: boolean
    visiteurSeulement?: boolean
  }
}

const enConstruction = () => import('@/views/EnConstruction.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/connexion', name: 'connexion', component: Connexion, meta: { titre: 'Connexion', visiteurSeulement: true } },
    { path: '/inscription', name: 'inscription', component: Connexion, meta: { titre: 'Créer un compte', visiteurSeulement: true } },
    {
      path: '/',
      component: () => import('@/components/AppliVente.vue'),
      meta: { requiertAuth: true },
      children: [
        { path: '', name: 'tableau-de-bord', component: () => import('@/views/TableauDeBord.vue'), meta: { titre: 'Tableau de bord' } },
        // @ts-ignore Vue component declaration is missing for this module.
        { path: 'ventes', name: 'ventes', component: () => import('@/views/Ventes.vue'), meta: { titre: 'Ventes' } },
        { path: 'produits', name: 'produits', component: () => import('@/views/Produits.vue'), meta: { titre: 'Produits' } },
        { path: 'categories', name: 'categories', component: enConstruction, meta: { titre: 'Catégories' } },
        { path: 'clients', name: 'clients', component: () => import('@/views/Clients.vue'), meta: { titre: 'Clients' } },
        { path: 'stock', name: 'stock', component: enConstruction, meta: { titre: 'Stock' } },
        { path: 'rapports', name: 'rapports', component: enConstruction, meta: { titre: 'Rapports' } },
        { path: 'utilisateurs', name: 'utilisateurs', component: enConstruction, meta: { titre: 'Utilisateurs' } },
        { path: 'parametres', name: 'parametres', component: enConstruction, meta: { titre: 'Paramètres' } },
      ],
    },
    { path: '/:chemin(.*)*', name: 'introuvable', component: () => import('@/views/PageIntrouvable.vue'), meta: { titre: 'Page introuvable' } },
  ],
})

router.beforeEach(async (to) => {
  if (!to.meta.requiertAuth && !to.meta.visiteurSeulement) return

  const connecte = await verifierSession()
  if (to.meta.requiertAuth && !connecte) {
    return { name: 'connexion', query: { redirect: to.fullPath } }
  }
  if (to.meta.visiteurSeulement && connecte) {
    return { name: 'tableau-de-bord' }
  }
})

router.afterEach((to) => {
  document.title = to.meta.titre ? `${to.meta.titre} - Boutique Plus` : 'Boutique Plus'
})

definirSurSessionExpiree(() => {
  fermerSession()
  const route = router.currentRoute.value
  if (route.meta.requiertAuth) {
    router.push({ name: 'connexion', query: { redirect: route.fullPath } })
  }
})

export default router
