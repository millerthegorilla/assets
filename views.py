from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import TrigramSimilarity
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from django.views.generic import View

from .forms import AssetTransferForm
from .models import Asset
from .models import AssetTransfer


# Create your views here.
@method_decorator(login_required, name="dispatch")
class AssetTransferView(FormView):
    model = AssetTransfer
    form_class = AssetTransferForm
    template_name = "asset_transfer.html"
    success_url = "asset_transfer_success.html"

    def get(self, request, uuid, *args, **kwargs):
        super().get(request, *args, **kwargs)
        asset = Asset.objects.get(unique_id=uuid)
        asset_transfers = AssetTransfer.objects.filter(asset=asset).order_by("-created")
        asset_transfer = asset_transfers.first() if asset_transfers.exists() else None
        if (
            asset_transfer
            and asset_transfer.to_user == request.user
            and asset_transfer.was_transferred_recently()
        ):
            messages.warning(
                request,
                "This asset has been transferred to you recently. \
                 Do you want to cancel the transfer?",
            )
        else:
            asset_transfer = AssetTransfer.objects.create(
                asset=asset,
                from_user=asset.current_holder,
                to_user=request.user,
            )
        context_data = self.get_context_data(**kwargs)
        context_data["transfer_id"] = asset_transfer.id
        context_data["transfer_date"] = asset_transfer.created.strftime(
            "%d-%m-%Y at %H:%M:%S",
        )
        return self.render_to_response(context_data)

    def get_context_data(self, **kwargs):
        super().get_context_data(**kwargs)
        asset = Asset.objects.get(unique_id=self.kwargs["uuid"])
        context = super().get_context_data(**kwargs)
        context["asset_name"] = asset.name
        context["asset_location"] = asset.location.name
        context["asset_id"] = str(self.kwargs["uuid"])
        return context

    def post(self, request, uuid):
        form = AssetTransferForm(request.POST)
        asset_transfer = AssetTransfer.objects.get(id=request.POST.get("transfer_id"))
        asset_transfer.notes = form.data.get("notes", "")
        asset_transfer.save()
        return redirect("assets:asset_transfer_notes_added")


@method_decorator(login_required, name="dispatch")
class AssetTransferCancelView(View):
    template_name = "asset_transfer_cancel.html"

    def get(self, request, uuid, *args, **kwargs):
        asset = Asset.objects.get(unique_id=uuid)
        asset_transfer = AssetTransfer.objects.filter(asset=asset).last()
        context = {
            "transfer_id": asset_transfer.id,
        }
        asset_transfer.delete()
        return render(request, "asset_transfer_cancel_success.html", context)

# a view to choose an asset and view its asset_transfer history
@method_decorator(login_required, name="dispatch")
@method_decorator(staff_member_required, name="dispatch")
class AssetTransferHistoryView(View):
    template_name = "asset_transfer_history.html"

    def get(self, request, *args, **kwargs):
        context = {}
        search = request.GET.get("search", "")
        if not search:
            messages.info(request, "Please enter an asset name to search.")
            return render(request, self.template_name, context)
        assets = (
            Asset.objects.annotate(similarity=TrigramSimilarity("name", search))
            .filter(
                similarity__gt=0.2,
            )
            .order_by("-similarity")
        )
        if not assets:
            messages.info(request, "No assets found.")
        else:
            context = {"assets": assets}
            transfers = AssetTransfer.objects.filter(
                asset=assets.first(),
            ).order_by("-created")
            if not transfers:
                messages.info(request, "Asset has no asset transfer history.")
            else:
                context.update(
                    {
                        "transfers": transfers,
                    },
                )
        return render(request, self.template_name, context)
