"""
Client Mystère — SMIT / Loi 80-14 / Arrêté 985-24
Application Streamlit avec critères officiels de l'Arrêté conjoint n°985-24
"""

import streamlit as st
import pandas as pd
from PIL import Image
import io
import datetime
import json
import os

# ─── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Client Mystère — SMIT",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
  html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

  .page-title { font-size: 26px; font-weight: 800; margin-bottom: 4px; }
  .page-sub   { font-size: 13px; color: #64748B; margin-bottom: 20px; }

  .section-header {
    padding: 10px 16px; border-radius: 8px; margin: 16px 0 10px 0;
    font-weight: 700; font-size: 14px;
    background: #F1F5F9; border-left: 4px solid #0EA5E9;
  }
  .critere-card {
    background: #F8FAFC; border-radius: 10px; padding: 14px 16px;
    margin-bottom: 10px; border: 1px solid #E2E8F0;
  }
  .badge-a {
    display: inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 700; background: #FEE2E2; color: #DC2626;
    margin-bottom: 6px;
  }
  .badge-b {
    display: inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 700; background: #DBEAFE; color: #2563EB;
    margin-bottom: 6px;
  }
  .score-box {
    background: #0F172A; color: white; border-radius: 14px;
    padding: 24px; text-align: center; margin-bottom: 16px;
  }
  .score-pct  { font-size: 48px; font-weight: 800; line-height: 1; }
  .score-label{ font-size: 12px; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
  .grade-badge{ display: inline-block; padding: 6px 18px; border-radius: 20px; font-size: 13px; font-weight: 700; margin-top: 12px; }
  .stat-card  { background:#F8FAFC; border-radius:12px; padding:16px; text-align:center; border:1px solid #E2E8F0; }
  .warning-box{
    background: #FEF3C7; border: 1px solid #FCD34D; border-radius: 10px;
    padding: 14px 18px; color: #92400E; font-size: 13px; margin-top: 20px;
  }
  .progress-bar-outer { background:#E2E8F0; border-radius:99px; height:8px; margin-top:4px; }
  .progress-bar-inner { height:8px; border-radius:99px; transition: width 0.3s; }
</style>
""", unsafe_allow_html=True)

# ─── CHARGEMENT DES CRITÈRES ───────────────────────────────────────────────────
@st.cache_data
def load_criteres():
    """Charge les critères depuis le JSON officiel (Arrêté 985-24)."""
    json_path = os.path.join(os.path.dirname(__file__), "criteres_arrete_985_24.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["criteres"]
    return []

ALL_CRITERES = load_criteres()

def get_types():
    return sorted(set(c["type_etablissement"] for c in ALL_CRITERES))

def get_categories(type_etab):
    return sorted(set(c["categorie"] for c in ALL_CRITERES if c["type_etablissement"] == type_etab))

def get_sections(type_etab, categorie):
    return sorted(set(
        c["section"] for c in ALL_CRITERES
        if c["type_etablissement"] == type_etab and c["categorie"] == categorie
        and c["section"] not in ("Général", "Non défini", "")
    )) + (["Général"] if any(
        c["section"] in ("Général", "Non défini", "")
        for c in ALL_CRITERES
        if c["type_etablissement"] == type_etab and c["categorie"] == categorie
    ) else [])

def get_criteres(type_etab, categorie, section=None):
    result = [
        c for c in ALL_CRITERES
        if c["type_etablissement"] == type_etab and c["categorie"] == categorie
    ]
    if section:
        if section == "Général":
            result = [c for c in result if c["section"] in ("Général", "Non défini", "")]
        else:
            result = [c for c in result if c["section"] == section]
    return result

# ─── SCORING ───────────────────────────────────────────────────────────────────
def calc_scores(criteres, reponses_a, reponses_b):
    """
    Calcule les scores selon l'arrêté 985-24 :
    - Norme A (obligatoire) : 100% de conformité requise
    - Norme B (complémentaire) : 70% min des points requis
    """
    a_criteres = [c for c in criteres if c["norme_obligatoire_A"]]
    b_criteres = [c for c in criteres if c["points_complementaire_B"] > 0]

    # Score A
    a_total = len(a_criteres)
    a_conforme = sum(1 for c in a_criteres if reponses_a.get(c["critere"]) == "conforme")
    a_nc = sum(1 for c in a_criteres if reponses_a.get(c["critere"]) == "non_conforme")
    a_na = sum(1 for c in a_criteres if reponses_a.get(c["critere"]) == "na")
    a_evalues = a_conforme + a_nc
    a_pct = round((a_conforme / (a_evalues - a_na)) * 100) if (a_evalues - a_na) > 0 else None

    # Score B
    b_points_max = sum(c["points_complementaire_B"] for c in b_criteres)
    b_points_earned = sum(
        reponses_b.get(c["critere"], 0) for c in b_criteres
    )
    b_evalues = sum(1 for c in b_criteres if reponses_b.get(c["critere"], -1) >= 0)
    b_pct = round((b_points_earned / b_points_max) * 100) if b_points_max > 0 else None

    return {
        "a_total": a_total, "a_conforme": a_conforme, "a_nc": a_nc,
        "a_evalues": a_evalues, "a_pct": a_pct,
        "b_total": len(b_criteres), "b_points_max": b_points_max,
        "b_points_earned": b_points_earned, "b_evalues": b_evalues, "b_pct": b_pct,
    }

def grade(pct):
    if pct is None: return ("Non évalué", "#94A3B8", "#F1F5F9")
    if pct >= 90:   return ("Excellent 🏆", "#10B981", "#D1FAE5")
    if pct >= 75:   return ("Bien ✅",       "#0EA5E9", "#E0F2FE")
    if pct >= 60:   return ("Acceptable ⚠️", "#F59E0B", "#FEF3C7")
    if pct >= 40:   return ("Insuffisant ❌", "#EF4444", "#FEE2E2")
    return               ("Critique 🚨",    "#7C3AED", "#EDE9FE")

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
for key in ["identity", "reponses_a", "reponses_b", "comments", "obs_section", "images"]:
    if key not in st.session_state:
        st.session_state[key] = {}

identity     = st.session_state.identity
reponses_a   = st.session_state.reponses_a    # {critere_text: "conforme"|"non_conforme"|"na"}
reponses_b   = st.session_state.reponses_b    # {critere_text: int points}
comments     = st.session_state.comments       # {critere_text: str}
obs_section  = st.session_state.obs_section   # {section: str}
images       = st.session_state.images         # {critere_text: [files]}

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🕵️ Client Mystère")
    st.markdown("**Arrêté n°985-24 — SMIT / Loi 80-14**")
    st.divider()

    # ── Sélection type & catégorie
    st.markdown("### 🏨 Type d'établissement")

    if not ALL_CRITERES:
        st.error("⚠️ Fichier `criteres_arrete_985_24.json` introuvable.\nVeuillez l'ajouter à la racine du projet.")
        st.stop()

    types = get_types()
    selected_type = st.selectbox(
        "Type", types,
        index=types.index(identity.get("type_etab", types[0])) if identity.get("type_etab") in types else 0,
        key="sb_type"
    )
    identity["type_etab"] = selected_type

    categories = get_categories(selected_type)
    selected_cat = st.selectbox(
        "Catégorie", categories,
        index=categories.index(identity.get("categorie", categories[0])) if identity.get("categorie") in categories else 0,
        key="sb_cat"
    )
    identity["categorie"] = selected_cat

    st.divider()

    # ── Informations de la visite
    st.markdown("### 📋 Informations de la visite")
    identity["etablissement"] = st.text_input("Nom de l'établissement", value=identity.get("etablissement", ""), placeholder="Hôtel Atlas…")
    identity["ville"]         = st.text_input("Ville", value=identity.get("ville", ""), placeholder="Marrakech…")
    identity["date"]          = st.date_input("Date de visite", value=datetime.date.today())
    identity["evaluateur"]    = st.text_input("Code évaluateur", value=identity.get("evaluateur", ""), placeholder="EV-0042")
    identity["nuitees"]       = st.number_input("Nombre de nuit(s)", min_value=1, max_value=30, value=int(identity.get("nuitees", 1)))

    st.divider()

    # ── Progression
    all_crit = get_criteres(selected_type, selected_cat)
    a_crit = [c for c in all_crit if c["norme_obligatoire_A"]]
    b_crit = [c for c in all_crit if c["points_complementaire_B"] > 0]
    a_evalues = sum(1 for c in a_crit if reponses_a.get(c["critere"]) in ("conforme", "non_conforme"))
    b_evalues = sum(1 for c in b_crit if reponses_b.get(c["critere"], -1) >= 0)

    st.markdown(f"**Norme A :** {a_evalues}/{len(a_crit)} évalués")
    st.progress(a_evalues / len(a_crit) if a_crit else 0)
    st.markdown(f"**Norme B :** {b_evalues}/{len(b_crit)} évalués")
    st.progress(b_evalues / len(b_crit) if b_crit else 0)

    st.divider()
    if st.button("↺ Réinitialiser tout", type="secondary", use_container_width=True):
        for k in ["reponses_a", "reponses_b", "comments", "obs_section", "images"]:
            st.session_state[k] = {}
        st.rerun()

# ─── TITRE PRINCIPAL ──────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-title">🕵️ Client Mystère à Blanc — SMIT</div>
<div class="page-sub">
    {selected_cat} &nbsp;·&nbsp; {identity.get('etablissement') or 'Établissement non renseigné'}
    &nbsp;·&nbsp; {identity.get('ville') or ''} &nbsp;·&nbsp;
    Évaluateur : {identity.get('evaluateur') or '—'}
</div>
""", unsafe_allow_html=True)

# ─── ONGLETS : SECTIONS + RAPPORT ─────────────────────────────────────────────
sections = get_sections(selected_type, selected_cat)

# On limite les onglets à 12 max pour lisibilité, reste en "Autres"
MAX_TABS = 12
if len(sections) > MAX_TABS:
    tab_sections = sections[:MAX_TABS - 1] + ["Autres sections"]
else:
    tab_sections = sections

tab_labels = tab_sections + ["📊 Rapport final"]
tabs = st.tabs(tab_labels)

# ─── ONGLETS DE CRITÈRES ───────────────────────────────────────────────────────
for t_idx, tab_section in enumerate(tab_sections):
    with tabs[t_idx]:

        # Récupérer les critères de cette section (ou des sections regroupées)
        if tab_section == "Autres sections":
            criteres_section = get_criteres(selected_type, selected_cat)
            criteres_section = [c for c in criteres_section if c["section"] not in sections[:MAX_TABS - 1]]
        else:
            criteres_section = get_criteres(selected_type, selected_cat, tab_section)

        if not criteres_section:
            st.info("Aucun critère dans cette section.")
            continue

        # En-tête section
        a_in_sec = [c for c in criteres_section if c["norme_obligatoire_A"]]
        b_in_sec = [c for c in criteres_section if c["points_complementaire_B"] > 0]
        col1, col2, col3 = st.columns(3)
        col1.metric("Total critères", len(criteres_section))
        col2.metric("🔴 Norme A obligatoire", len(a_in_sec))
        col3.metric("🔵 Norme B complémentaire", len(b_in_sec))

        # Score en temps réel pour cette section
        sc = calc_scores(criteres_section, reponses_a, reponses_b)
        c1, c2 = st.columns(2)
        with c1:
            pct_a = sc["a_pct"]
            g_a, ga_color, ga_bg = grade(pct_a)
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size:11px;color:#64748B;font-weight:600;text-transform:uppercase">Conformité Norme A</div>
                <div style="font-size:32px;font-weight:800;color:{'#DC2626' if pct_a is not None and pct_a < 100 else '#10B981'}">
                    {pct_a if pct_a is not None else '—'}{'%' if pct_a is not None else ''}
                </div>
                <div style="font-size:11px;color:#94A3B8">Cible : 100% • {sc['a_conforme']}/{sc['a_evalues']} conformes</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            pct_b = sc["b_pct"]
            g_b, gb_color, gb_bg = grade(pct_b)
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size:11px;color:#64748B;font-weight:600;text-transform:uppercase">Score Norme B</div>
                <div style="font-size:32px;font-weight:800;color:{'#DC2626' if pct_b is not None and pct_b < 70 else '#2563EB'}">
                    {pct_b if pct_b is not None else '—'}{'%' if pct_b is not None else ''}
                </div>
                <div style="font-size:11px;color:#94A3B8">Cible : 70% • {sc['b_points_earned']}/{sc['b_points_max']} pts</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # ── Norme A (obligatoires) ──────────────────────────────────────────
        if a_in_sec:
            st.markdown("""
            <div class="section-header" style="border-left-color:#DC2626;background:#FEF2F2">
                🔴 Normes obligatoires "A" — Conformité requise à 100%
            </div>
            """, unsafe_allow_html=True)

            for c in a_in_sec:
                cid = c["critere"]
                with st.container():
                    st.markdown(f"""
                    <div class="critere-card">
                        <span class="badge-a">Norme A — Obligatoire</span><br>
                        <strong style="font-size:13px">{cid}</strong>
                    </div>
                    """, unsafe_allow_html=True)

                    col_rep, col_comment = st.columns([1, 2])
                    with col_rep:
                        current = reponses_a.get(cid, "non_evalue")
                        options = {
                            "non_evalue": "— Non évalué —",
                            "conforme":   "✅ Conforme",
                            "non_conforme": "❌ Non conforme",
                            "na":         "N/A — Non applicable",
                        }
                        selected_r = st.radio(
                            "Résultat",
                            list(options.keys()),
                            format_func=lambda x: options[x],
                            index=list(options.keys()).index(current),
                            key=f"a_{hash(cid) % 9999999}",
                            label_visibility="collapsed",
                            horizontal=False,
                        )
                        reponses_a[cid] = selected_r

                    with col_comment:
                        comments[cid] = st.text_area(
                            "Observation",
                            value=comments.get(cid, ""),
                            placeholder="Remarque, fait observé, justification…",
                            key=f"com_{hash(cid) % 9999999}",
                            height=80,
                            label_visibility="collapsed",
                        )

                    # Photo upload
                    with st.expander(f"📷 Photos — preuve de conformité"):
                        uploaded = st.file_uploader(
                            "Photos",
                            type=["jpg", "jpeg", "png", "webp"],
                            accept_multiple_files=True,
                            key=f"img_{hash(cid) % 9999999}",
                            label_visibility="collapsed",
                        )
                        if uploaded:
                            images[cid] = uploaded
                            cols_img = st.columns(min(len(uploaded), 4))
                            for ji, fi in enumerate(uploaded):
                                cols_img[ji % 4].image(Image.open(fi), caption=fi.name, use_container_width=True)

                    st.markdown("<hr style='margin:8px 0;border-color:#F1F5F9'>", unsafe_allow_html=True)

        # ── Norme B (complémentaires) ───────────────────────────────────────
        if b_in_sec:
            st.markdown("""
            <div class="section-header" style="border-left-color:#2563EB;background:#EFF6FF">
                🔵 Normes complémentaires "B" — Score pondéré (cible ≥ 70%)
            </div>
            """, unsafe_allow_html=True)

            for c in b_in_sec:
                cid = c["critere"]
                max_pts = c["points_complementaire_B"]
                with st.container():
                    st.markdown(f"""
                    <div class="critere-card">
                        <span class="badge-b">Norme B — {max_pts} pts</span><br>
                        <strong style="font-size:13px">{cid}</strong>
                    </div>
                    """, unsafe_allow_html=True)

                    col_pts, col_comment = st.columns([1, 2])
                    with col_pts:
                        current_pts = reponses_b.get(cid, None)
                        # Slider de 0 à max_pts
                        val = st.slider(
                            f"Score (0 à {max_pts})",
                            min_value=0,
                            max_value=max_pts,
                            value=current_pts if current_pts is not None else 0,
                            key=f"b_{hash(cid) % 9999999}",
                        )
                        reponses_b[cid] = val
                        pct_crit = round((val / max_pts) * 100) if max_pts else 0
                        color_crit = "#10B981" if pct_crit >= 70 else ("#F59E0B" if pct_crit >= 40 else "#EF4444")
                        st.markdown(f"<span style='color:{color_crit};font-weight:700;font-size:13px'>{val}/{max_pts} pts ({pct_crit}%)</span>", unsafe_allow_html=True)

                    with col_comment:
                        comments[cid] = st.text_area(
                            "Observation",
                            value=comments.get(cid, ""),
                            placeholder="Remarque, fait observé…",
                            key=f"comb_{hash(cid) % 9999999}",
                            height=80,
                            label_visibility="collapsed",
                        )

                    with st.expander(f"📷 Photos — {cid[:40]}…" if len(cid) > 40 else f"📷 Photos"):
                        uploaded = st.file_uploader(
                            "Photos",
                            type=["jpg", "jpeg", "png", "webp"],
                            accept_multiple_files=True,
                            key=f"imgb_{hash(cid) % 9999999}",
                            label_visibility="collapsed",
                        )
                        if uploaded:
                            images[cid] = uploaded
                            cols_img = st.columns(min(len(uploaded), 4))
                            for ji, fi in enumerate(uploaded):
                                cols_img[ji % 4].image(Image.open(fi), caption=fi.name, use_container_width=True)

                    st.markdown("<hr style='margin:8px 0;border-color:#F1F5F9'>", unsafe_allow_html=True)

        # ── Observations générales de la section ───────────────────────────
        st.markdown(f"#### 📝 Observations générales — {tab_section}")
        obs_section[tab_section] = st.text_area(
            "Observations",
            value=obs_section.get(tab_section, ""),
            placeholder=f"Points forts, points faibles, faits marquants pour « {tab_section} »…",
            key=f"obs_{t_idx}",
            height=90,
            label_visibility="collapsed",
        )

# ─── RAPPORT FINAL ─────────────────────────────────────────────────────────────
with tabs[-1]:
    st.markdown("## 📊 Rapport de visite mystère")
    st.markdown(f"**{selected_cat}** &nbsp;·&nbsp; Arrêté conjoint n°985-24")

    all_crit_full = get_criteres(selected_type, selected_cat)
    sc_global = calc_scores(all_crit_full, reponses_a, reponses_b)

    etab  = identity.get("etablissement", "Établissement non renseigné")
    ville = identity.get("ville", "")
    date_v = identity.get("date", datetime.date.today())
    evalu = identity.get("evaluateur", "")

    # ── Scores globaux
    col1, col2 = st.columns(2)
    with col1:
        pct_a = sc_global["a_pct"]
        ok_a = pct_a is not None and pct_a == 100
        st.markdown(f"""
        <div class="score-box" style="background:{'#064E3B' if ok_a else '#7F1D1D'}">
            <div style="font-size:13px;color:rgba(255,255,255,0.5)">{etab} · {ville} · {date_v}</div>
            <div class="score-pct">{pct_a if pct_a is not None else '—'}{'%' if pct_a is not None else ''}</div>
            <div class="score-label">Conformité Norme A (obligatoire)</div>
            <div class="grade-badge" style="background:{'#D1FAE5' if ok_a else '#FEE2E2'};color:{'#065F46' if ok_a else '#991B1B'}">
                {'✅ Conforme — 100% atteint' if ok_a else ('❌ Non conforme — 100% requis' if pct_a is not None else 'Non évalué')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        pct_b = sc_global["b_pct"]
        ok_b = pct_b is not None and pct_b >= 70
        st.markdown(f"""
        <div class="score-box" style="background:{'#1E3A5F' if ok_b else '#1E1B4B'}">
            <div style="font-size:13px;color:rgba(255,255,255,0.5)">{sc_global['b_points_earned']}/{sc_global['b_points_max']} points obtenus</div>
            <div class="score-pct">{pct_b if pct_b is not None else '—'}{'%' if pct_b is not None else ''}</div>
            <div class="score-label">Score Norme B (complémentaire)</div>
            <div class="grade-badge" style="background:{'#DBEAFE' if ok_b else '#EDE9FE'};color:{'#1E40AF' if ok_b else '#5B21B6'}">
                {'✅ Objectif atteint — ≥ 70%' if ok_b else ('⚠️ Insuffisant — 70% requis' if pct_b is not None else 'Non évalué')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Tableau récapitulatif par section
    st.markdown("### 📈 Résultats par section")
    rows_sec = []
    for sec in sections:
        crit_sec = get_criteres(selected_type, selected_cat, sec)
        sc_sec = calc_scores(crit_sec, reponses_a, reponses_b)
        rows_sec.append({
            "Section": sec,
            "Critères total": len(crit_sec),
            "Norme A — Conformité": f"{sc_sec['a_pct']}%" if sc_sec['a_pct'] is not None else "Non évalué",
            "Norme A — Conformes": f"{sc_sec['a_conforme']}/{sc_sec['a_evalues']}",
            "Norme B — Score": f"{sc_sec['b_pct']}%" if sc_sec['b_pct'] is not None else "Non évalué",
            "Norme B — Points": f"{sc_sec['b_points_earned']}/{sc_sec['b_points_max']}",
        })
    if rows_sec:
        df_sec = pd.DataFrame(rows_sec)
        st.dataframe(df_sec, use_container_width=True, hide_index=True)

    st.divider()

    # ── Non-conformités norme A
    nc_list = [
        {"Critère": cid, "Section": next((c["section"] for c in all_crit_full if c["critere"] == cid), "—"),
         "Observation": comments.get(cid, "")}
        for cid, val in reponses_a.items() if val == "non_conforme"
    ]
    if nc_list:
        st.markdown(f"### 🚨 Non-conformités Norme A ({len(nc_list)} critères)")
        st.dataframe(pd.DataFrame(nc_list), use_container_width=True, hide_index=True)
        st.divider()

    # ── Observations par section
    obs_filled = {k: v for k, v in obs_section.items() if v}
    if obs_filled:
        st.markdown("### 📝 Observations par section")
        for sec, obs_text in obs_filled.items():
            st.markdown(f"**{sec}**")
            st.info(obs_text)

    # ── Export JSON
    st.markdown("### 💾 Export des données")

    identity_safe = {k: str(v) for k, v in identity.items()}
    export_data = {
        "etablissement": identity_safe,
        "arrete_reference": "Arrêté conjoint n°985-24 du 24 décembre 2024",
        "type_etablissement": selected_type,
        "categorie": selected_cat,
        "date_rapport": str(datetime.date.today()),
        "evaluateur": evalu,
        "scores": {
            "norme_a_conformite_pct": sc_global["a_pct"],
            "norme_a_conforme": sc_global["a_conforme"],
            "norme_a_total": sc_global["a_total"],
            "norme_b_score_pct": sc_global["b_pct"],
            "norme_b_points_obtenus": sc_global["b_points_earned"],
            "norme_b_points_max": sc_global["b_points_max"],
        },
        "reponses_norme_a": reponses_a,
        "reponses_norme_b": reponses_b,
        "commentaires": comments,
        "observations_sections": obs_section,
    }

    st.download_button(
        label="⬇️ Télécharger le rapport complet (JSON)",
        data=json.dumps(export_data, ensure_ascii=False, indent=2),
        file_name=f"rapport_mystere_{identity.get('etablissement','').replace(' ','_')}_{str(datetime.date.today())}.json",
        mime="application/json",
    )

    st.markdown("""
    <div class="warning-box">
        ⚠️ Ce rapport est issu d'une visite mystère à blanc confidentielle — usage interne uniquement.
        Conforme à la grille Arrêté conjoint n°985-24, Bulletin Officiel n°7407 bis du 27 mai 2025.
        Ministère du Tourisme, de l'Artisanat et de l'Économie Sociale et Solidaire — SMIT.
    </div>
    """, unsafe_allow_html=True)
