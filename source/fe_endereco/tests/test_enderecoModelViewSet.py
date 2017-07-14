from django.core.urlresolvers import reverse
from django.test import TestCase
from fe_core.tests.factories import AccessTokenFactory, UserFactory, EntityFactory
from rest_framework import status
from rest_framework.test import APIClient

from fe_endereco.models import Endereco
from fe_endereco.tests.factories import EnderecoFactory


class TestEnderecoModelViewSet(TestCase):
    def setUp(self):
        self.user = UserFactory(entity=None)
        access_token = AccessTokenFactory(user=self.user)

        self.entity = EntityFactory()
        self.user_with_entity = UserFactory(entity=self.entity)
        self.access_token_entity = AccessTokenFactory(user=self.user_with_entity)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(access_token.token))

    def test_create_with_only_user(self):
        response = self.client.post(reverse('enderecos-list'), {
            'logradouro': 'a',
            'numero': 1,
            'estado': 'RS',
            'cidade': 'Porto Alegre',
            'bairro': 'b',
            'cep': '91060280'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        endereco = Endereco.objects.get(uuid=response.data['uuid'])
        self.assertIsNone(endereco.entidade)
        self.assertEqual(endereco.usuario, self.user)

    def test_create_with_entity(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.access_token_entity.token))
        response = self.client.post(reverse('enderecos-list'), {
            'logradouro': 'a',
            'numero': 1,
            'estado': 'RS',
            'cidade': 'Porto Alegre',
            'bairro': 'b',
            'cep': '91060280'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        endereco = Endereco.objects.get(uuid=response.data['uuid'])
        self.assertEqual(endereco.entidade, self.entity)
        self.assertEqual(endereco.usuario, self.user_with_entity)

    def test_get_with_user(self):
        endereco = EnderecoFactory(usuario=self.user)
        response = self.client.get(reverse('enderecos-detail', kwargs={'pk': str(endereco.uuid)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        entidade = response.data
        self.assertTrue('uuid' in entidade)
        self.assertTrue('created_at' in entidade)
        self.assertTrue('updated_at' in entidade)
        self.assertTrue('cep' in entidade)
        self.assertTrue('logradouro' in entidade)
        self.assertTrue('numero' in entidade)
        self.assertTrue('complemento' in entidade)
        self.assertTrue('bairro' in entidade)
        self.assertTrue('cidade' in entidade)
        self.assertTrue('estado' in entidade)
        self.assertEqual(10, len(entidade))

    def test_get_with_entity(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.access_token_entity.token))
        endereco = EnderecoFactory(usuario=self.user, entidade=self.entity)
        response = self.client.get(reverse('enderecos-detail', kwargs={'pk': str(endereco.uuid)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        entidade = response.data
        self.assertTrue('uuid' in entidade)
        self.assertTrue('created_at' in entidade)
        self.assertTrue('updated_at' in entidade)
        self.assertTrue('cep' in entidade)
        self.assertTrue('logradouro' in entidade)
        self.assertTrue('numero' in entidade)
        self.assertTrue('complemento' in entidade)
        self.assertTrue('bairro' in entidade)
        self.assertTrue('cidade' in entidade)
        self.assertTrue('estado' in entidade)
        self.assertEqual(10, len(entidade))

    def test_update_with_user(self):
        endereco = EnderecoFactory(usuario=self.user)
        response = self.client.patch(reverse('enderecos-detail', kwargs={'pk': str(endereco.uuid)}), {
            'cidade': 'ABC'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        endereco.refresh_from_db()
        self.assertEqual(endereco.cidade, 'ABC')

    def test_delete_with_user(self):
        endereco = EnderecoFactory(usuario=self.user)
        self.assertEqual(1, Endereco.objects.filter(uuid=endereco.uuid).count())
        response = self.client.delete(reverse('enderecos-detail', kwargs={'pk': str(endereco.uuid)}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(0, Endereco.objects.filter(uuid=endereco.uuid).count())
