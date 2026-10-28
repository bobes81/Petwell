from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import PetProfile


class PetProfileTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user("petowner")
        self.other = User.objects.create_user("otherpetowner")
        self.staff = User.objects.create_user("petstaff", is_staff=True)
        self.pet = PetProfile.objects.create(
            owner=self.owner,
            name="Milo",
            species=PetProfile.Species.DOG,
            care_focus=PetProfile.CareFocus.CALM,
            notes="Likes a quiet reading corner.",
        )
        self.other_pet = PetProfile.objects.create(
            owner=self.other,
            name="Other owner's cat",
            species=PetProfile.Species.CAT,
            notes="Private notes for another account.",
        )
        self.list_url = reverse("pets:list")
        self.create_url = reverse("pets:create")
        self.edit_url = reverse("pets:edit", args=[self.pet.pk])
        self.delete_url = reverse("pets:delete", args=[self.pet.pk])
        self.valid = {
            "name": "Luna",
            "species": "cat",
            "care_focus": "nutrition",
            "notes": "Meals at the same time each day.",
        }

    def test_all_profile_routes_require_login(self):
        for url in (
            self.list_url,
            self.create_url,
            self.edit_url,
            self.delete_url,
        ):
            with self.subTest(url=url):
                for method in (self.client.get, self.client.post):
                    response = method(url)
                    self.assertEqual(response.status_code, 302)
                    self.assertTrue(
                        response.url.startswith(reverse("account_login"))
                    )
        self.assertEqual(PetProfile.objects.count(), 2)

    def test_list_only_shows_own_profiles_and_focus_reminder(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.list_url)
        self.assertContains(response, "Milo")
        self.assertContains(response, self.pet.routine_reminder)
        self.assertContains(response, self.pet.notes)
        self.assertNotContains(response, self.other_pet.name)
        self.assertNotContains(response, self.other_pet.notes)
        self.assertContains(response, self.create_url)
        self.assertContains(response, self.edit_url)
        self.assertContains(response, self.delete_url)

    def test_empty_list_explains_how_to_add_first_pet(self):
        self.client.force_login(self.staff)
        self.assertContains(
            self.client.get(self.list_url), "You have not added any pets yet"
        )

    def test_create_uses_authenticated_owner_and_shows_saved_frontend_data(
        self,
    ):
        self.client.force_login(self.owner)
        response = self.client.post(
            self.create_url, {**self.valid, "owner": self.other.pk}
        )
        self.assertRedirects(response, self.list_url)
        pet = PetProfile.objects.get(name="Luna")
        self.assertEqual(pet.owner, self.owner)
        self.assertEqual(pet.care_focus, "nutrition")
        response = self.client.get(self.list_url)
        self.assertContains(response, pet.name)
        self.assertContains(response, pet.notes)
        self.assertContains(response, pet.routine_reminder)

    def test_owner_can_edit_without_reassigning_profile(self):
        self.client.force_login(self.owner)
        self.assertContains(self.client.get(self.edit_url), "Milo")
        response = self.client.post(
            self.edit_url, {**self.valid, "owner": self.other.pk}
        )
        self.assertRedirects(response, self.list_url)
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.name, "Luna")
        self.assertEqual(self.pet.owner, self.owner)
        self.assertEqual(self.pet.notes, self.valid["notes"])
        self.assertEqual(self.pet.species, "cat")

    def test_other_users_and_staff_cannot_access_or_change_owner_profile(
        self,
    ):
        for user in (self.other, self.staff):
            self.client.force_login(user)
            for url in (self.edit_url, self.delete_url):
                with self.subTest(user=user.username, url=url):
                    self.assertEqual(self.client.get(url).status_code, 404)
                    self.assertEqual(
                        self.client.post(url, self.valid).status_code, 404
                    )
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.name, "Milo")
        self.assertEqual(self.pet.owner, self.owner)

    def test_delete_get_is_confirmation_only_and_owner_post_deletes(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.delete_url)
        self.assertContains(response, "Milo")
        self.assertContains(response, "Delete profile")
        self.assertContains(response, "Cancel")
        self.assertTrue(PetProfile.objects.filter(pk=self.pet.pk).exists())
        self.assertRedirects(self.client.post(self.delete_url), self.list_url)
        self.assertFalse(PetProfile.objects.filter(pk=self.pet.pk).exists())
        self.assertTrue(
            PetProfile.objects.filter(pk=self.other_pet.pk).exists()
        )

    def test_invalid_create_and_edit_inputs_do_not_persist(self):
        self.client.force_login(self.owner)
        for invalid in (
            {"name": ""},
            {"name": " "},
            {"name": "x" * 81},
            {"species": "unsupported"},
            {"care_focus": "unsupported"},
            {"notes": "x" * 501},
        ):
            for url in (self.create_url, self.edit_url):
                with self.subTest(url=url, invalid=invalid):
                    response = self.client.post(url, {**self.valid, **invalid})
                    self.assertEqual(response.status_code, 200)
                    self.assertTrue(response.context["form"].errors)
                    self.assertEqual(PetProfile.objects.count(), 2)
                    self.pet.refresh_from_db()
                    self.assertEqual(self.pet.name, "Milo")
                    self.assertEqual(
                        self.pet.notes, "Likes a quiet reading corner."
                    )

    def test_notes_are_optional_and_all_supported_focuses_have_reminders(self):
        self.client.force_login(self.owner)
        for focus in PetProfile.CareFocus.values:
            with self.subTest(focus=focus):
                response = self.client.post(
                    self.create_url,
                    {**self.valid, "care_focus": focus, "notes": ""},
                )
                self.assertRedirects(response, self.list_url)
                pet = PetProfile.objects.filter(
                    owner=self.owner, care_focus=focus, name="Luna"
                ).latest("pk")
                self.assertEqual(pet.notes, "")
                self.assertTrue(pet.routine_reminder)
                self.assertContains(
                    self.client.get(self.list_url), pet.routine_reminder
                )

    def test_profile_text_is_escaped_in_frontend(self):
        self.client.force_login(self.owner)
        self.client.post(
            self.create_url,
            {
                **self.valid,
                "name": '<script>alert("name")</script>',
                "notes": '<script>alert("notes")</script>',
            },
        )
        response = self.client.get(self.list_url)
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, '<script>alert("name")</script>')
        self.assertNotContains(response, '<script>alert("notes")</script>')

    def test_mutations_require_csrf_and_valid_form_token_works(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        for url in (self.create_url, self.edit_url, self.delete_url):
            with self.subTest(url=url):
                self.assertEqual(client.post(url, self.valid).status_code, 403)
        self.assertEqual(PetProfile.objects.count(), 2)
        client.get(self.create_url)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.create_url, self.valid, HTTP_X_CSRFTOKEN=token
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            PetProfile.objects.filter(owner=self.owner, name="Luna").exists()
        )
