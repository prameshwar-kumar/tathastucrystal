class SaveGuestSessionMiddleware:
    """
    Preserves guest session key before login rotation.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_anonymous:
            if not request.session.session_key:
                request.session.create()
            if "guest_session_key" not in request.session:
                request.session["guest_session_key"] = request.session.session_key

        response = self.get_response(request)
        return response
