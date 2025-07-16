#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import urllib3

# Désactive les warnings SSL (self‑signed)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MOODLE_URL = 'https://moodle.caplogy.com/webservice/rest/server.php'
TOKEN      = 'VOTRE_TOKEN_ICI'   # remplacez par votre token généré
FORMAT     = 'json'

def call_moodle(wsfunction: str, params: dict):
    """Envoie une requête POST à Moodle et retourne le JSON."""
    payload = {
        'wstoken': TOKEN,
        'moodlewsrestformat': FORMAT,
        'wsfunction': wsfunction,
        **params
    }
    r = requests.post(MOODLE_URL, data=payload, verify=False, timeout=10)
    r.raise_for_status()
    return r.json()

def get_user_id_by_email(email: str) -> int:
    data = call_moodle('core_user_get_users', {
        'criteria[0][key]':   'email',
        'criteria[0][value]': email
    })
    users = data.get('users', [])
    if not users:
        raise ValueError(f"Utilisateur non trouvé pour {email}")
    return users[0]['id']

def enrol_users(courseid: int, emails: list[str], roleid: int):
    """Enrol each user as teacher in the course."""
    user_ids = [get_user_id_by_email(e) for e in emails]
    params = {}
    for i, uid in enumerate(user_ids):
        params[f'enrolments[{i}][roleid]']   = roleid
        params[f'enrolments[{i}][userid]']   = uid
        params[f'enrolments[{i}][courseid]'] = courseid
    call_moodle('enrol_manual_enrol_users', params)

if __name__ == '__main__':
    # === CONFIGURATION ===
    COURSE_ID = 42                     # ID du cours Moodle
    EMAILS    = ['alice@ex.com','bob@ex.com']
    ROLE_ID   = 3                      # 3 = teacher, 4 = editingteacher
    # =====================

    try:
        enrol_users(COURSE_ID, EMAILS, ROLE_ID)
        print("✅ Les utilisateurs ont bien été ajoutés comme profs !")
    except Exception as e:
        print("❌ Erreur :", e)
