"""
Client Mystère à Blanc — SMIT / Loi 80-14
Application Streamlit avec upload d'images par critère
"""

import streamlit as st
import pandas as pd
from PIL import Image
import io
import datetime
import json

# ─── CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Client Mystère — SMIT",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
  html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

  .dim-header {
    padding: 14px 20px; border-radius: 10px; margin-bottom: 12px;
    font-weight: 700; font-size: 16px; display: flex; align-items: center; gap: 10px;
  }
  .score-box {
    background: #0F172A; color: white; border-radius: 14px;
    padding: 24px; text-align: center; margin-bottom: 16px;
  }
  .score-pct { font-size: 48px; font-weight: 800; line-height: 1; }
  .score-label { font-size: 12px; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
  .grade-badge { display: inline-block; padding: 6px 18px; border-radius: 20px; font-size: 13px; font-weight: 700; margin-top: 12px; }
  .critere-card { background: #F8F7F4; border-radius: 10px; padding: 14px; margin-bottom: 10px; border-left: 4px solid #E2E8F0; }
  .note-label { font-size: 12px; font-weight: 600; padding: 3px 10px; border-radius: 20px; display: inline-block; margin-bottom: 6px; }
  .warning-box {
    background: #FEF3C7; border: 1px solid #FCD34D; border-radius: 10px;
    padding: 14px 18px; color: #92400E; font-size: 13px; margin-top: 20px;
  }
  .stRadio > div { flex-direction: row !important; gap: 8px; }
</style>
""", unsafe_allow_html=True)

# ─── DATA ───────────────────────────────────────────────────────────────────
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
    0: ("Non évalué",   "#94A3B8", "#F1F5F9"),
    1: ("Insuffisant",  "#EF4444", "#FEE2E2"),
    2: ("Faible",       "#F97316", "#FFEDD5"),
    3: ("Acceptable",   "#EAB308", "#FEF9C3"),
    4: ("Bien",         "#22C55E", "#DCFCE7"),
    5: ("Excellent",    "#0EA5E9", "#E0F2FE"),
}

NOTE_OPTIONS = ["— Non évalué —", "1 ⭐ Insuffisant", "2 ⭐⭐ Faible",
                "3 ⭐⭐⭐ Acceptable", "4 ⭐⭐⭐⭐ Bien", "5 ⭐⭐⭐⭐⭐ Excellent"]

def grade(pct):
    if pct >= 90: return ("Excellent 🏆",   "#10B981", "#D1FAE5")
    if pct >= 75: return ("Bien ✅",         "#0EA5E9", "#E0F2FE")
    if pct >= 60: return ("Acceptable ⚠️",   "#F59E0B", "#FEF3C7")
    if pct >= 40: return ("Insuffisant ❌",   "#EF4444", "#FEE2E2")
    return         ("Critique 🚨",           "#7C3AED", "#EDE9FE")

def calc_dim_score(dim_id, notes):
    dim = next(d for d in DIMENSIONS if d["id"] == dim_id)
    vals = [notes.get(c["id"], 0) for c in dim["criteres"] if notes.get(c["id"], 0) > 0]
    if not vals:
        return None
    return {"score": sum(vals), "max": len(vals) * 5, "count": len(vals), "total": len(dim["criteres"])}

def calc_global(notes):
    total_w, total_score = 0, 0
    for dim in DIMENSIONS:
        s = calc_dim_score(dim["id"], notes)
        if s:
            total_score += (s["score"] / s["max"]) * 100 * dim["weight"]
            total_w += dim["weight"]
    return round(total_score / total_w) if total_w else None

# ─── STATE ──────────────────────────────────────────────────────────────────
if "notes"    not in st.session_state: st.session_state.notes    = {}
if "comments" not in st.session_state: st.session_state.comments = {}
if "obs"      not in st.session_state: st.session_state.obs      = {}
if "images"   not in st.session_state: st.session_state.images   = {}  # {critere_id: [bytes]}
if "identity" not in st.session_state: st.session_state.identity = {}

notes    = st.session_state.notes
comments = st.session_state.comments
obs      = st.session_state.obs
images   = st.session_state.images
identity = st.session_state.identity

# ─── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🕵️ Client Mystère à Blanc")
    st.markdown("**Loi 80-14 — SMIT**")
    st.divider()

    st.markdown("### 📋 Informations de la visite")
    identity["etablissement"] = st.text_input("Nom de l'établissement", value=identity.get("etablissement", ""), placeholder="Hôtel Atlas…")
    identity["categorie"]     = st.selectbox("Catégorie", ["", "3 ★★★", "4 ★★★★", "5 ★★★★★", "Riad / Maison d'hôtes", "Résidence / Kasbah"], index=["", "3 ★★★", "4 ★★★★", "5 ★★★★★", "Riad / Maison d'hôtes", "Résidence / Kasbah"].index(identity.get("categorie", "")) if identity.get("categorie", "") in ["", "3 ★★★", "4 ★★★★", "5 ★★★★★", "Riad / Maison d'hôtes", "Résidence / Kasbah"] else 0)
    identity["ville"]         = st.text_input("Ville", value=identity.get("ville", ""), placeholder="Marrakech…")
    identity["date"]          = st.date_input("Date de visite", value=datetime.date.today())
    identity["evaluateur"]    = st.text_input("Code évaluateur", value=identity.get("evaluateur", ""), placeholder="EV-0042")
    identity["nuitees"]       = st.number_input("Nombre de nuit(s)", min_value=1, max_value=30, value=int(identity.get("nuitees", 1)))

    st.divider()

    # Global score in sidebar
    global_pct = calc_global(notes)
    all_criteres = [c for d in DIMENSIONS for c in d["criteres"]]
    evaluated = sum(1 for c in all_criteres if notes.get(c["id"], 0) > 0)

    st.markdown(f"**Progression :** {evaluated}/{len(all_criteres)} critères")
    if global_pct is not None:
        g_label, g_color, _ = grade(global_pct)
        st.markdown(f"**Score global :** :{g_color.replace('#','')}[**{global_pct}%**] — {g_label}")
        st.progress(global_pct / 100)

    st.divider()
    if st.button("↺ Réinitialiser tout", type="secondary", use_container_width=True):
        for key in ["notes", "comments", "obs", "images", "identity"]:
            st.session_state[key] = {}
        st.rerun()

# ─── MAIN TABS ──────────────────────────────────────────────────────────────
tab_labels = [f"{d['icon']} {d['label']}" for d in DIMENSIONS] + ["📊 Rapport final"]
tabs = st.tabs(tab_labels)

# ─── DIMENSION TABS ─────────────────────────────────────────────────────────
for i, dim in enumerate(DIMENSIONS):
    with tabs[i]:
        # Header
        st.markdown(f"""
        <div class="dim-header" style="background:{dim['color_bg']}; border-left: 5px solid {dim['color']};">
            {dim['icon']} <span style="color:{dim['color']}">{dim['label']}</span>
            &nbsp;·&nbsp; <span style="font-weight:400; font-size:13px; color:#64748B">Pondération {dim['weight']}%</span>
        </div>
        """, unsafe_allow_html=True)

        s = calc_dim_score(dim["id"], notes)
        if s:
            pct = round((s["score"] / s["max"]) * 100)
            g_label, g_color, g_bg = grade(pct)
            col1, col2, col3 = st.columns(3)
            col1.metric("Score dimension", f"{pct}%")
            col2.metric("Critères évalués", f"{s['count']}/{s['total']}")
            col3.metric("Mention", g_label)
            st.progress(pct / 100)
            st.divider()

        # Critères
        for c in dim["criteres"]:
            with st.container():
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
                        "Note",
                        NOTE_OPTIONS,
                        index=current_val,
                        key=f"note_{c['id']}",
                        label_visibility="collapsed"
                    )
                    val = NOTE_OPTIONS.index(selected)
                    notes[c["id"]] = val

                    if val > 0:
                        label, color, bg = NOTE_LABELS[val]
                        st.markdown(f'<span class="note-label" style="background:{bg};color:{color}">{label}</span>', unsafe_allow_html=True)

                with col_comment:
                    comments[c["id"]] = st.text_input(
                        "Observation",
                        value=comments.get(c["id"], ""),
                        placeholder="Remarque, fait observé…",
                        key=f"comment_{c['id']}",
                        label_visibility="collapsed"
                    )

                # ── Image upload ──────────────────────────────────────────
                with st.expander(f"📷 Ajouter des photos — {c['label']}"):
                    uploaded = st.file_uploader(
                        "Glissez vos photos ici (JPG, PNG)",
                        type=["jpg", "jpeg", "png", "webp"],
                        accept_multiple_files=True,
                        key=f"img_{c['id']}",
                        label_visibility="collapsed"
                    )
                    if uploaded:
                        images[c["id"]] = uploaded
                        cols = st.columns(min(len(uploaded), 4))
                        for j, f in enumerate(uploaded):
                            img = Image.open(f)
                            cols[j % 4].image(img, caption=f.name, use_container_width=True)

                st.markdown("---")

        # Observations générales de la dimension
        st.markdown(f"#### 📝 Observations générales — {dim['label']}")
        obs[dim["id"]] = st.text_area(
            "Observations",
            value=obs.get(dim["id"], ""),
            placeholder=f"Points forts, points faibles, faits marquants pour la dimension « {dim['label']} »…",
            key=f"obs_{dim['id']}",
            height=100,
            label_visibility="collapsed"
        )

# ─── RAPPORT FINAL ──────────────────────────────────────────────────────────
with tabs[-1]:
    st.markdown("## 📊 Rapport de visite mystère à blanc")

    global_pct = calc_global(notes)
    etab = identity.get("etablissement", "Établissement non renseigné")
    cat  = identity.get("categorie", "")
    ville = identity.get("ville", "")
    date_v = identity.get("date", datetime.date.today())
    evaluateur = identity.get("evaluateur", "")

    # Hero score
    if global_pct is not None:
        g_label, g_color, g_bg = grade(global_pct)
        st.markdown(f"""
        <div class="score-box">
            <div style="font-size:13px;color:rgba(255,255,255,0.5);margin-bottom:8px">
                {etab} &nbsp;·&nbsp; {cat} &nbsp;·&nbsp; {ville} &nbsp;·&nbsp; {date_v} &nbsp;·&nbsp; Évaluateur : {evaluateur}
            </div>
            <div class="score-pct">{global_pct}%</div>
            <div class="score-label">Score global pondéré</div>
            <div class="grade-badge" style="background:{g_bg};color:{g_color}">{g_label}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Aucun critère évalué. Commencez à remplir le formulaire.")

    # Scores par dimension
    st.markdown("### 📈 Scores par dimension")
    cols = st.columns(len(DIMENSIONS))
    for i, dim in enumerate(DIMENSIONS):
        s = calc_dim_score(dim["id"], notes)
        pct = round((s["score"] / s["max"]) * 100) if s else None
        with cols[i]:
            st.markdown(f"""
            <div style="background:{dim['color_bg']};border-radius:12px;padding:16px;text-align:center;border:1px solid {dim['color']}33">
                <div style="font-size:22px">{dim['icon']}</div>
                <div style="font-size:11px;color:#64748B;font-weight:600;text-transform:uppercase;margin:4px 0">{dim['label']}</div>
                <div style="font-size:28px;font-weight:800;color:{dim['color']}">{pct if pct is not None else '—'}{('%' if pct is not None else '')}</div>
                <div style="font-size:11px;color:#94A3B8">Poids {dim['weight']}%</div>
            </div>
            """, unsafe_allow_html=True)
            if pct is not None:
                st.progress(pct / 100)

    st.divider()

    # Barres détaillées
    st.markdown("### 📊 Répartition des scores")
    for dim in DIMENSIONS:
        s = calc_dim_score(dim["id"], notes)
        pct = round((s["score"] / s["max"]) * 100) if s else 0
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"{dim['icon']} **{dim['label']}** *(poids {dim['weight']}%)*")
            st.progress(pct / 100)
        with col2:
            st.markdown(f"**{pct}%**" if s else "*Non évalué*")

    st.divider()

    # Tableau détaillé
    st.markdown("### 📋 Détail critère par critère")
    for dim in DIMENSIONS:
        st.markdown(f"""
        <div style="background:{dim['color_bg']};padding:10px 16px;border-radius:8px;margin-bottom:8px;font-weight:700;color:{dim['color']}">
            {dim['icon']} {dim['label']}
        </div>
        """, unsafe_allow_html=True)

        rows = []
        for c in dim["criteres"]:
            val = notes.get(c["id"], 0)
            label = NOTE_LABELS[val][0] if val > 0 else "Non évalué"
            comment = comments.get(c["id"], "")
            rows.append({"Critère": c["label"], "Note /5": val if val > 0 else "—", "Niveau": label, "Observation": comment})

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Observations de la dimension
        if obs.get(dim["id"]):
            st.info(f"📝 {obs[dim['id']]}")

        # Photos par critère dans la dimension
        photos_in_dim = [(c, images[c["id"]]) for c in dim["criteres"] if c["id"] in images and images[c["id"]]]
        if photos_in_dim:
            st.markdown("**📷 Photos jointes :**")
            for c, imgs in photos_in_dim:
                st.markdown(f"*{c['label']}*")
                img_cols = st.columns(min(len(imgs), 4))
                for j, f in enumerate(imgs):
                    img_cols[j % 4].image(Image.open(f), caption=f.name, use_container_width=True)

        st.markdown("---")

    # Export JSON
    st.markdown("### 💾 Export des données")

    # Convertir toutes les valeurs non-sérialisables en string
    identity_safe = {k: str(v) for k, v in identity.items()}

    export_data = {
        "etablissement": identity_safe,
        "notes": {k: int(v) for k, v in notes.items()},
        "commentaires": comments,
        "observations": obs,
        "score_global": int(global_pct) if global_pct is not None else None,
        "date_rapport": str(datetime.date.today()),
    }
    st.download_button(
        label="⬇️ Télécharger le rapport (JSON)",
        data=json.dumps(export_data, ensure_ascii=False, indent=2),
        file_name=f"rapport_client_mystere_{identity.get('etablissement','').replace(' ','_')}_{str(datetime.date.today())}.json",
        mime="application/json",
    )

    st.markdown("""
    <div class="warning-box">
        ⚠️ Ce rapport est issu d'une visite mystère à blanc confidentielle — usage interne uniquement.
        Conforme à la grille Loi n°80-14, Ministère du Tourisme du Maroc.
    </div>
    """, unsafe_allow_html=True)
