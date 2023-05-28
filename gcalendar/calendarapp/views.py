from django.shortcuts import render

# Create your views here.
# views.py
import os
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
from django.views import View
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build


class GoogleCalendarInitView(View):
    """
    View for initiating the OAuth flow

    """
    def get(self, request):

        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENT_SECRETS_FILE,
            scopes=['https://www.googleapis.com/auth/calendar.readonly']
        )
        flow.redirect_uri = request.build_absolute_uri(reverse('calendar-redirect'))
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            prompt='consent',
        )
        request.session['oauth_state'] = state
        return redirect(authorization_url)


class GoogleCalendarRedirectView(View):
    """
    View for handling the redirect request from Google

    """
    def get(self, request):
        state = request.session.pop('oauth_state', '')
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENT_SECRETS_FILE,
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            state=state
        )
        flow.redirect_uri = request.build_absolute_uri(reverse('calendar-redirect'))
        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)

        credentials = flow.credentials
        request.session['google_credentials'] = credentials_to_dict(credentials)


        events = get_calendar_events(credentials)
        return JsonResponse({'events': events})



def credentials_to_dict(credentials):
    """
    Converts credentials to dict

    """
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
    }

def get_calendar_events(credentials):
    """
    Gets calendar events details

    """
    service = build('calendar', 'v3', credentials=credentials)
    events_result = service.events().list(calendarId='primary', maxResults=10).execute()
    events = events_result.get('items', [])
    return events
