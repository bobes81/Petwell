from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from .forms import PetProfileForm
from .models import PetProfile


@login_required
@require_GET
def pet_list(request):
    pets = PetProfile.objects.filter(owner=request.user)
    return render(request, "accounts/pet_list.html", {"pets": pets})


@login_required
@require_http_methods(["GET", "POST"])
def pet_create(request):
    form = PetProfileForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        pet = form.save(commit=False)
        pet.owner = request.user
        pet.save()
        messages.success(request, "Your pet profile was added.")
        return redirect("pets:list")
    return render(request, "accounts/pet_form.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def pet_edit(request, pk):
    pet = get_object_or_404(PetProfile, pk=pk, owner=request.user)
    form = PetProfileForm(
        request.POST if request.method == "POST" else None, instance=pet
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your pet profile was updated.")
        return redirect("pets:list")
    return render(
        request,
        "accounts/pet_form.html",
        {"form": form, "pet": pet},
    )


@login_required
@require_http_methods(["GET", "POST"])
def pet_delete(request, pk):
    pet = get_object_or_404(PetProfile, pk=pk, owner=request.user)
    if request.method == "POST":
        pet.delete()
        messages.success(request, "Your pet profile was deleted.")
        return redirect("pets:list")
    return render(request, "accounts/pet_confirm_delete.html", {"pet": pet})
