"""
Client Mystère à Blanc — SMIT / Loi 80-14
Application Streamlit + Supabase
"""

import streamlit as st
import pandas as pd
from PIL import Image
import datetime
import json
from supabase import create_client, Client

st.set_page_config(page_title="Client Mystère — SMIT", page_icon="🕵️", layout="wide")

SUPABASE_URL = "https://vvlrxqpcbveinzrgnhg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ2bHJ4cXBjYnZlaW5menJnbmhnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgwNjg1MTAsImV4cCI6MjA5MzY0NDUxMH0.JNY5Bzz3XpZDOkyNIU-1O_oLanobtOfVXG94lJN1eH4"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_supabase()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.dim-header { padding: 14px 20px; border-radius: 10px; margin-bottom: 12px; font-weight: 700; font-size: 16px; }
.score-box { background: #0F172A; color: white; border-radius: 14px; padding: 24px; text-align: center; margin-bottom: 16px; }
.score-pct { font-size: 48px; font-weight: 800; line-height: 1; }
.score-label { font-size: 12px; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
.grade-badge { display: inline-block; padding: 6px 18px; border-radius: 20px; font-size: 13px; font-weight: 700; margin-top: 12px; }
.critere-card { background: #F8F7F4; border-radius: 10px; padding: 14px; margin-bottom: 10px; border-left: 4px solid #E2E8F0; }
.note-label { font-size: 12px; font-weight: 600; padding: 3px 10px; border-radius: 20px; display: inline-block; margin-bottom: 6px; }
.warning-box { background: #FEF3C7; border: 1px solid #FCD34D; border-radius: 10px; padding: 14px 18px; color: #92400E; font-size: 13px; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

DIMENSIONS = [
    {
        "id": "accueil", "label": "Accueil & Réception", "icon": "🏨",
        "weight": 25, "color": "#0EA5E9", "color_bg": "#E0F2FE",
        "criteres": [
            {"id": "a1", "label": "Processus de réservation en ligne", "desc": "Délai de confirmation, clarté des informations"},
            {"id": "a2", "label": "Accueil physique à l'arrivée", "desc": "Sourire, proactivité, chaleur de l'accueil"},
            {"id": "a3", "label": "Rapidité du check-in", "desc": "Temps d'attente, efficacité de l'enregistrement"},
            {"id": "a4", "label": "Maîtrise des langues (FR/EN/AR)", "desc": "Qualité de communication multilingue"},
            {"id": "a5", "label": "Gestion des demandes spéciales", "desc": "Prise en compte et suivi des demandes"},
            {"id": "a6", "label": "Présentation & tenue du personnel", "desc": "Uniformes, hygiène, badge, posture"},
            {"id": "a7", "label": "Rapidité & qualité du check-out", "desc": "Fluidité du départ, exactitude de la facture"},
        ],
    },
    {
        "id": "chambre", "label": "Chambre & Hébergement", "icon": "🛏",
        "weight": 30, "color": "#8B5CF6", "color_bg": "#EDE9FE",
        "criteres": [
            {"id": "c1", "label": "Propreté & état général de la chambre", "desc": "Sol, surfaces, vitres, mobilier"},
            {"id": "c2", "label": "Conformité des équipements au classement", "desc": "Présence et fonctionnement selon l'étoilage"},
            {"id": "c3", "label": "Linge, dotations & minibar", "desc": "Qualité du linge, complétude des dotations"},
            {"id": "c4", "label": "Confort thermique, acoustique & lumineux", "desc": "Climatisation, isolation phonique, éclairage"},
            {"id": "c5", "label": "Room service — délai & qualité", "desc": "Temps de livraison, présentation, qualité"},
            {"id": "c6", "label": "Sécurité, confidentialité & intimité", "desc": "Serrures, coffre-fort, occultation fenêtres"},
        ],
    },
    {
        "id": "restauration", "label": "Restauration", "icon": "🍽",
        "weight": 25, "color": "#F59E0B", "color_bg": "#FEF3C7",
        "criteres": [
            {"id": "r1", "label": "Qualité gustative & présentation des plats", "desc": "Saveurs, cuisson, dressage, fraîcheur"},
            {"id": "r2", "label": "Mise en place & propreté de la salle", "desc": "Dressage des tables, propreté, ambiance"},
            {"id": "r3", "label": "Réactivité & attitude du personnel", "desc": "Disponibilité, sourire, gestion simultanée"},
            {"id": "r4", "label": "Connaissance de la carte & conseil", "desc": "Description des plats, recommandations, allergies"},
            {"id": "r5", "label": "Respect des délais de service", "desc": "Rythme entrée → plat → dessert"},
            {"id": "r6", "label": "Hygiène alimentaire & normes HACCP", "desc": "Températures, manipulation, conservation"},
        ],
    },
    {
        "id": "services", "label": "Services & Expérience globale", "icon": "✨",
        "weight": 20, "color": "#10B981", "color_bg": "#D1FAE5",
        "criteres": [
            {"id": "s1", "label": "Spa, fitness & piscine — état & service", "desc": "Propreté, équipements, accueil du personnel"},
            {"id": "s2", "label": "Équipements d'animation", "desc": "Disponibilité, état, qualité des activités"},
            {"id": "s3", "label": "Propreté & sécurité espaces communs", "desc": "Hall, couloirs, ascenseurs, jardins, parkings"},
            {"id": "s4", "label": "Gestion des réclamations", "desc": "Écoute, rapidité, suivi et compensation"},
            {"id": "s5", "label": "Cohérence de l'image de marque", "desc": "Signalétique, communication, uniformité visuelle"},
            {"id": "s6", "label": "Expérience globale & mémoire du séjour", "desc": "Impression générale, recommandation"},
        ],
    },
]

NOTE_LABELS = {
    0: ("Non évalué",  "#94A3B8", "#F1F5F9"),
    1: ("Insuffisant", "#EF4444", "#FEE2E2"),
    2: ("Faible",      "#F97316", "#FFEDD5"),
    3: ("Acceptable",  "#EAB308", "#FEF9C3"),
    4: ("Bien",        "#22C55E", "#DCFCE7"),
    5: ("Excellent",   "#0EA5E9", "#E0F2FE"),
}

NOTE_OPTIONS = ["— Non évalué —", "1 ⭐ Insuffisant", "2 ⭐⭐ Faible",
                "3 ⭐⭐⭐ Acceptable", "4 ⭐⭐⭐⭐ Bien", "5 ⭐⭐⭐⭐⭐ Excellent"]

def grade(pct):
    if pct >= 90: return ("Excellent 🏆", "#10B981", "#D1FAE5")
    if pct >= 75: return ("Bien ✅",       "#0EA5E9", "#E0F2FE")
    if pct >= 60: return ("Acceptable ⚠️", "#F59E0B", "#FEF3C7")
    if pct >= 40: return ("Insuffisant ❌", "#EF4444", "#FEE2E2")
    return         ("Critique 🚨",         "#7C3AED", "#EDE9FE")

def calc_dim_score(dim_id, notes):
    dim = next(d for d in DIMENSIONS if d["id"] == dim_id)
    vals = [notes.get(c["id"], 0) for c in dim["criteres"] if notes.get(c["id"], 0) > 0]
    if not vals: return None
    return {"score": sum(vals), "max": len(vals)*5, "count": len(vals), "total": len(dim["criteres"])}

def calc_global(notes):
    total_w, total_score = 0, 0
    for dim in DIMENSIONS:
        s = calc_dim_score(dim["id"], notes)
        if s:
            total_score += (s["score"]/s["max"])*100*dim["weight"]
            total_w += dim["weight"]
    return round(total_score/total_w) if total_w else None

def sauvegarder_visite(identity, notes, comments, obs, score_global):
    try:
        visite_data = {
            "etablissement":   identity.get("etablissement", ""),
            "categorie":       identity.get("categorie", ""),
            "ville":           identity.get("ville", ""),
            "date_visite":     str(identity.get("date", datetime.date.today())),
            "evaluateur_code": identity.get("evaluateur", ""),
            "nuitees":         int(identity.get("nuitees", 1)),
            "score_global":    score_global,
            "statut":          "en_cours",
            "updated_at":      datetime.datetime.now().isoformat(),
        }
        if st.session_state.get("visite_id"):
            supabase.table("visites").update(visite_data).eq("id", st.session_state.visite_id).execute()
            visite_id = st.session_state.visite_id
        else:
            res = supabase.table("visites").insert(visite_data).execute()
            visite_id = res.data[0]["id"]
            st.session_state.visite_id = visite_id

        supabase.table("notes").delete().eq("visite_id", visite_id).execute()
        notes_rows = []
        for dim in DIMENSIONS:
            for c in dim["criteres"]:
                val = notes.get(c["id"], 0)
                if val > 0:
                    notes_rows.append({
                        "visite_id":    visite_id,
                        "critere_id":   c["id"],
                        "dimension_id": dim["id"],
                        "note":         val,
                        "commentaire":  comments.get(c["id"], ""),
                    })
        if notes_rows:
            supabase.table("notes").insert(notes_rows).execute()

        supabase.table("observations").delete().eq("visite_id", visite_id).execute()
        obs_rows = [{"visite_id": visite_id, "dimension_id": k, "texte": v}
                    for k, v in obs.items() if v]
        if obs_rows:
            supabase.table("observations").insert(obs_rows).execute()

        return True, visite_id
    except Exception as e:
        return False, str(e)

def soumettre_visite(visite_id):
    try:
        supabase.table("visites").update({"statut": "soumis"}).eq("id", visite_id).execute()
        return True
    except:
        return False

def charger_visites():
    try:
        res = supabase.table("visites").select("*").order("created_at", desc=True).execute()
        return res.data
    except:
        return []

# ─── STATE ──────────────────────────────────────────────────────────────────
for key, default in [("notes", {}), ("comments", {}), ("obs", {}),
                     ("images", {}), ("identity", {}),
                     ("visite_id", None), ("last_save", None)]:
    if key not in st.session_state:
        st.session_state[key] = default

notes    = st.session_state.notes
comments = st.session_state.comments
obs      = st.session_state.obs
identity = st.session_state.identity

# ─── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🕵️ Client Mystère à Blanc")
    st.markdown("**Loi 80-14 — SMIT**")
    if st.session_state.visite_id:
        st.success(f"✅ Visite enregistrée\n`{str(st.session_state.visite_id)[:8]}…`")
    st.divider()

    st.markdown("### 📋 Informations de la visite")
    identity["etablissement"] = st.text_input("Nom de l'établissement", value=identity.get("etablissement", ""), placeholder="Hôtel Atlas…", key="id_etab")
    identity["categorie"]     = st.selectbox("Catégorie", ["", "3 ★★★", "4 ★★★★", "5 ★★★★★", "Riad / Maison d'hôtes", "Résidence / Kasbah"], key="id_cat")
    identity["ville"]         = st.text_input("Ville", value=identity.get("ville", ""), placeholder="Marrakech…", key="id_ville")
    identity["date"]          = st.date_input("Date de visite", value=datetime.date.today(), key="id_date")
    identity["evaluateur"]    = st.text_input("Code évaluateur", value=identity.get("evaluateur", ""), placeholder="EV-001", key="id_eval")
    identity["nuitees"]       = st.number_input("Nombre de nuit(s)", min_value=1, max_value=30, value=int(identity.get("nuitees", 1)), key="id_nuit")

    st.divider()
    global_pct = calc_global(notes)
    all_criteres = [c for d in DIMENSIONS for c in d["criteres"]]
    evaluated = sum(1 for c in all_criteres if notes.get(c["id"], 0) > 0)
    st.markdown(f"**Progression :** {evaluated}/{len(all_criteres)} critères")
    if global_pct is not None:
        st.progress(global_pct / 100)
        st.markdown(f"**Score global : {global_pct}%**")
    st.divider()

    if st.button("💾 Sauvegarder", type="primary", use_container_width=True, key="btn_save"):
        if not identity.get("etablissement"):
            st.error("Renseignez le nom de l'établissement.")
        else:
            ok, result = sauvegarder_visite(identity, notes, comments, obs, global_pct)
            if ok:
                st.success("✅ Sauvegardé !")
                st.session_state.last_save = datetime.datetime.now().strftime("%H:%M:%S")
            else:
                st.error(f"Erreur : {result}")

    if st.session_state.last_save:
        st.caption(f"Dernière sauvegarde : {st.session_state.last_save}")

    if st.button("↺ Nouvelle visite", type="secondary", use_container_width=True, key="btn_reset"):
        for k in ["notes","comments","obs","images","identity"]:
            st.session_state[k] = {}
        st.session_state.visite_id = None
        st.session_state.last_save = None
        st.rerun()

# ─── TABS ────────────────────────────────────────────────────────────────────
tab_labels = [f"{d['icon']} {d['label']}" for d in DIMENSIONS] + ["📊 Rapport", "🗂 Historique"]
tabs = st.tabs(tab_labels)

# ─── DIMENSIONS ──────────────────────────────────────────────────────────────
for i, dim in enumerate(DIMENSIONS):
    with tabs[i]:
        st.markdown(f"""
        <div class="dim-header" style="background:{dim['color_bg']};border-left:5px solid {dim['color']}">
            {dim['icon']} <span style="color:{dim['color']}">{dim['label']}</span>
            &nbsp;·&nbsp;<span style="font-weight:400;font-size:13px;color:#64748B">Pondération {dim['weight']}%</span>
        </div>
        """, unsafe_allow_html=True)

        s = calc_dim_score(dim["id"], notes)
        if s:
            pct = round((s["score"]/s["max"])*100)
            col1, col2, col3 = st.columns(3)
            col1.metric("Score dimension", f"{pct}%")
            col2.metric("Critères évalués", f"{s['count']}/{s['total']}")
            col3.metric("Mention", grade(pct)[0])
            st.progress(pct/100)
            st.divider()

        for c in dim["criteres"]:
            # Clé unique = dimension_id + critere_id
            k = f"{dim['id']}_{c['id']}"

            st.markdown(f"""
            <div class="critere-card" style="border-left-color:{dim['color']}">
                <strong>{c['label']}</strong><br>
                <span style="font-size:12px;color:#94A3B8">{c['desc']}</span>
            </div>
            """, unsafe_allow_html=True)

            col_note, col_comment = st.columns([1, 2])
            with col_note:
                current_val = notes.get(c["id"], 0)
                selected = st.selectbox(
                    "Note", NOTE_OPTIONS, index=current_val,
                    key=f"note_{k}", label_visibility="collapsed"
                )
                val = NOTE_OPTIONS.index(selected)
                notes[c["id"]] = val
                if val > 0:
                    lbl, color, bg = NOTE_LABELS[val]
                    st.markdown(f'<span class="note-label" style="background:{bg};color:{color}">{lbl}</span>',
                                unsafe_allow_html=True)
            with col_comment:
                comments[c["id"]] = st.text_input(
                    "Observation", value=comments.get(c["id"], ""),
                    placeholder="Remarque…", key=f"comment_{k}",
                    label_visibility="collapsed"
                )

            with st.expander(f"📷 Photos — {c['label']}"):
                uploaded = st.file_uploader(
                    "Photos", type=["jpg","jpeg","png","webp"],
                    accept_multiple_files=True,
                    key=f"img_{k}", label_visibility="collapsed"
                )
                if uploaded:
                    img_cols = st.columns(min(len(uploaded), 4))
                    for j, f in enumerate(uploaded):
                        img_cols[j%4].image(Image.open(f), caption=f.name, use_container_width=True)

            st.markdown("---")

        st.markdown(f"#### 📝 Observations générales — {dim['label']}")
        obs[dim["id"]] = st.text_area(
            "Observations", value=obs.get(dim["id"], ""),
            placeholder="Points forts, faibles, faits marquants…",
            key=f"obs_{dim['id']}", height=100, label_visibility="collapsed"
        )

# ─── RAPPORT ─────────────────────────────────────────────────────────────────
with tabs[-2]:
    st.markdown("## 📊 Rapport de visite")
    global_pct = calc_global(notes)

    if global_pct is not None:
        g_label, g_color, g_bg = grade(global_pct)
        st.markdown(f"""
        <div class="score-box">
            <div style="font-size:13px;color:rgba(255,255,255,0.5);margin-bottom:8px">
                {identity.get('etablissement','—')} · {identity.get('categorie','')} · {identity.get('ville','')}
            </div>
            <div class="score-pct">{global_pct}%</div>
            <div class="score-label">Score global pondéré</div>
            <div class="grade-badge" style="background:{g_bg};color:{g_color}">{g_label}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Aucun critère évalué pour l'instant.")

    cols = st.columns(len(DIMENSIONS))
    for i, dim in enumerate(DIMENSIONS):
        s = calc_dim_score(dim["id"], notes)
        pct = round((s["score"]/s["max"])*100) if s else None
        with cols[i]:
            st.markdown(f"""
            <div style="background:{dim['color_bg']};border-radius:12px;padding:16px;text-align:center;border:1px solid {dim['color']}33">
                <div style="font-size:22px">{dim['icon']}</div>
                <div style="font-size:11px;color:#64748B;font-weight:600;text-transform:uppercase;margin:4px 0">{dim['label']}</div>
                <div style="font-size:28px;font-weight:800;color:{dim['color']}">{str(pct)+'%' if pct is not None else '—'}</div>
                <div style="font-size:11px;color:#94A3B8">Poids {dim['weight']}%</div>
            </div>
            """, unsafe_allow_html=True)
            if pct is not None:
                st.progress(pct/100)

    st.divider()
    for dim in DIMENSIONS:
        st.markdown(f"""
        <div style="background:{dim['color_bg']};padding:10px 16px;border-radius:8px;margin-bottom:8px;font-weight:700;color:{dim['color']}">
            {dim['icon']} {dim['label']}
        </div>
        """, unsafe_allow_html=True)
        rows = [{
            "Critère":     c["label"],
            "Note /5":     notes.get(c["id"], 0) or "—",
            "Niveau":      NOTE_LABELS[notes.get(c["id"], 0)][0],
            "Observation": comments.get(c["id"], "")
        } for c in dim["criteres"]]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        if obs.get(dim["id"]):
            st.info(f"📝 {obs[dim['id']]}")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Soumettre le rapport final", type="primary", use_container_width=True, key="btn_submit"):
            if not st.session_state.visite_id:
                ok, result = sauvegarder_visite(identity, notes, comments, obs, global_pct)
            if st.session_state.visite_id:
                if soumettre_visite(st.session_state.visite_id):
                    st.success("🎉 Rapport soumis et enregistré dans la base de données !")
                else:
                    st.error("Erreur lors de la soumission.")
    with col2:
        identity_safe = {k: str(v) for k, v in identity.items()}
        export_data = {
            "etablissement": identity_safe,
            "notes":         {k: int(v) for k, v in notes.items()},
            "commentaires":  comments,
            "observations":  obs,
            "score_global":  int(global_pct) if global_pct is not None else None,
            "date_rapport":  str(datetime.date.today()),
        }
        st.download_button(
            "⬇️ Télécharger (JSON)",
            data=json.dumps(export_data, ensure_ascii=False, indent=2),
            file_name=f"rapport_{identity.get('etablissement','').replace(' ','_')}_{datetime.date.today()}.json",
            mime="application/json",
            use_container_width=True,
            key="btn_download"
        )

    st.markdown('<div class="warning-box">⚠️ Rapport confidentiel — usage interne uniquement. Conforme Loi n°80-14.</div>',
                unsafe_allow_html=True)

# ─── HISTORIQUE ──────────────────────────────────────────────────────────────
with tabs[-1]:
    st.markdown("## 🗂 Historique des visites")
    if st.button("🔄 Actualiser", key="btn_refresh"):
        st.rerun()

    visites = charger_visites()
    if not visites:
        st.info("Aucune visite enregistrée pour l'instant.")
    else:
        df = pd.DataFrame(visites)
        cols_ok = [c for c in ["etablissement","categorie","ville","date_visite",
                                "evaluateur_code","score_global","statut","created_at"] if c in df.columns]
        st.dataframe(df[cols_ok], use_container_width=True, hide_index=True)
        st.caption(f"Total : {len(visites)} visite(s)")
        if "score_global" in df.columns:
            scores = df["score_global"].dropna()
            if len(scores) > 0:
                c1, c2, c3 = st.columns(3)
                c1.metric("Score moyen", f"{round(scores.mean())}%")
                c2.metric("Score max",   f"{int(scores.max())}%")
                c3.metric("Score min",   f"{int(scores.min())}%") 
