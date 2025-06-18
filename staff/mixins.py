from django.shortcuts import redirect


class StaffMixins(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)