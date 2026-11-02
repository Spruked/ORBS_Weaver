"""Read-only, owner-requested evidence retrieval from VIV and Prime Mail."""
from __future__ import annotations

import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote
from urllib.request import HTTPRedirectHandler, Request, build_opener


class _DenyRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, new_url):
        return None


_NO_REDIRECTS = build_opener(_DenyRedirect())
_MAIL_QUERY = re.compile(
    r"\b(?:search|find|look up|check)\s+(?:my\s+)?(?:prime\s+)?(?:mail|email|inbox)\s+(?:for|about|regarding)\s+(.+?)\s*[?.!]*$",
    re.IGNORECASE,
)
_VIV_QUERY = re.compile(
    r"\b(?:search|find|look up|check)\s+(?:viv|my\s+(?:viv\s+)?(?:contacts|dossiers|research))\s+(?:for|about|regarding)\s+(.+?)\s*[?.!]*$",
    re.IGNORECASE,
)


def _get_json(base: str, path: str, token: str, params: dict | None = None) -> dict:
    url = base.rstrip("/") + path
    if params:
        url += "?" + urlencode(params)
    request = Request(url, headers={"Authorization": "Bearer " + token, "Accept": "application/json"})
    try:
        with _NO_REDIRECTS.open(request, timeout=8) as response:
            payload = json.load(response)
    except HTTPError as error:
        raise RuntimeError(f"upstream_http_{error.code}") from None
    except (URLError, TimeoutError, OSError, ValueError):
        raise RuntimeError("upstream_unavailable") from None
    if not isinstance(payload, dict):
        raise RuntimeError("invalid_upstream_response")
    return payload


def _viv_evidence(query: str) -> dict:
    base = os.getenv("ORBOT_VIV_API_URL", "http://127.0.0.1:21000").rstrip("/")
    token = os.getenv("CALI_ORBOT_API_TOKEN", "").strip()
    if len(token) < 32:
        return {"source_system": "VIV", "status": "not_configured", "items": []}
    try:
        result = _get_json(base, "/cali/intelligence/contacts", token, {"query": query, "business_scope": "all"})
        rows = result.get("contacts", [])
        items = []
        for contact in rows[:3] if isinstance(rows, list) else []:
            if not isinstance(contact, dict):
                continue
            item = {
                "contact_id": contact.get("id"),
                "party_id": contact.get("party_id"),
                "name": contact.get("name"),
                "email": contact.get("email"),
                "company_role": contact.get("company_role"),
                "business_roles": contact.get("business_roles", []),
                "segments": contact.get("segments", []),
                "source_system": "VIV",
                "verification_state": "VIV_record; relationship truth remains as labeled by VIV",
            }
            party_id = str(contact.get("party_id") or "").strip()
            if party_id:
                dossier = _get_json(
                    base,
                    f"/cali/intelligence/parties/{quote(party_id, safe='')}/dossier",
                    token,
                    {"business_scope": "all"},
                )
                party = dossier.get("party", {})
                identities = dossier.get("identities", {})
                item["dossier"] = {
                    "party": {key: party.get(key) for key in ("party_id", "kind", "display_name", "status") if key in party},
                    "identities": {
                        claim_type: [
                            {key: claim.get(key) for key in ("value_raw", "confidence", "verification_state", "source_type", "business_scope") if key in claim}
                            for claim in claims[:8]
                        ]
                        for claim_type, claims in identities.items()
                        if isinstance(claims, list)
                    } if isinstance(identities, dict) else {},
                    "roles": dossier.get("roles", [])[:8] if isinstance(dossier.get("roles"), list) else [],
                    "latest_message": dossier.get("latest_message"),
                }
            contact_id = str(contact.get("id") or "").strip()
            if contact_id:
                research = _get_json(base, f"/cali/intelligence/contacts/{quote(contact_id, safe='')}/research", token, {"limit": 3})
                item["research"] = [
                    {
                        key: evidence.get(key)
                        for key in ("research_id", "title", "url", "snippet", "provider", "verification_state", "published_at", "last_seen_at")
                        if key in evidence
                    }
                    for evidence in research.get("items", [])[:3]
                    if isinstance(evidence, dict)
                ]
            items.append(item)
        return {"source_system": "VIV", "status": "ok", "query": query, "items": items}
    except RuntimeError as error:
        return {"source_system": "VIV", "status": str(error), "items": []}


def _mail_evidence(query: str) -> dict:
    base = os.getenv("ORBOT_MAIL_API_URL", "http://127.0.0.1:19000").rstrip("/")
    token = os.getenv("ORBOT_MAIL_API_TOKEN", "").strip()
    if len(token) < 32:
        return {"source_system": "prime_mail", "status": "not_configured", "items": []}
    try:
        result = _get_json(base, "/api/orbot/mail/search", token, {"search": query, "limit": 6})
        return {
            "source_system": "prime_mail",
            "status": "ok",
            "query": query,
            "items": [
                {
                    key: item.get(key)
                    for key in ("id", "message_id", "sender", "recipient", "subject", "date", "folder", "text", "record_kind", "verification_state")
                }
                for item in result.get("items", [])[:6]
                if isinstance(item, dict)
            ],
        }
    except RuntimeError as error:
        return {"source_system": "prime_mail", "status": str(error), "items": []}


def retrieve_owner_requested_evidence(text: str) -> dict | None:
    """Retrieve narrowly matched records only when the owner explicitly asks to search a system."""
    match = _MAIL_QUERY.search(text)
    if match:
        query = match.group(1).strip()[:180]
        return _mail_evidence(query)
    match = _VIV_QUERY.search(text)
    if match:
        query = match.group(1).strip()[:180]
        return _viv_evidence(query)
    return None
