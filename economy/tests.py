from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from economy.models import Item


# Create your tests here.
class ItemAPITests(APITestCase):
    def setUp(self) -> None:
        self.item = Item.objects.create(id="123456789")

        self.list_url = reverse("item-list")
        self.detail_url = reverse("item-detail", kwargs={"pk": self.item.pk})

    def test_create_item(self):
        payload = {"id": "219866"}

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["id"], payload["id"])
        self.assertEqual(Item.objects.count(), 2)
        self.assertTrue(Item.objects.filter(id=payload["id"]).exists())

    def test_retrieve_single_item(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], self.item.id)

    def test_list_items(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], self.item.id)

    def test_delete_item(self):
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Item.objects.count(), 0)

    def test_update_item_not_allowed(self):
        payload = {"name": "Updated Name"}

        response = self.client.patch(self.detail_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
