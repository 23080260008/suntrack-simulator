# ============================================================
# SUNTRACK v2.8 - SOLAR ENERGY OPTIMIZATION SIMULATOR
# ============================================================
# Install dependencies:
# python -m pip install streamlit numpy plotly reportlab
#
# Run:
# python -m streamlit run app.py
# ============================================================

import math
from io import BytesIO
from datetime import datetime

import numpy as np
import plotly.graph_objects as go
import streamlit as st

# ReportLab is used only for PDF export.
try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# ------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------
st.set_page_config(
    page_title="SunTrack Simulator",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

    :root {
        --sun-ink: #172b36;
        --sun-muted: #657780;
        --sun-green: #087f70;
        --sun-gold: #f0ad24;
        --sun-coral: #e76f51;
        --sun-blue: #4285c5;
        --sun-line: #dce7e3;
        --sun-paper: #cfe7f3;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: var(--sun-ink);
    }

    .stApp {
        background-color: var(--sun-paper);
        background-image:
            linear-gradient(180deg, rgba(221, 242, 252, .76), rgba(220, 239, 247, .84)),
            url("https://images.unsplash.com/photo-1534088568595-a066f410bcda?auto=format&fit=crop&w=2400&q=85");
        background-position: center top;
        background-size: cover;
        background-attachment: fixed;
    }

    [data-testid="stHeader"] {
        background: rgba(211, 235, 247, .72);
        backdrop-filter: blur(10px);
    }

    [data-testid="stSidebar"] {
        background: rgba(221, 240, 248, .9);
        backdrop-filter: blur(12px);
        border-right: 1px solid var(--sun-line);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        font-family: 'Manrope', sans-serif;
        color: var(--sun-ink);
    }

    h1, h2, h3 {
        font-family: 'Manrope', sans-serif !important;
        color: var(--sun-ink);
        letter-spacing: 0;
    }

    h1 { font-weight: 800 !important; }
    h2 { font-weight: 700 !important; }
    h3 { font-weight: 700 !important; }

    .suntrack-hero {
        position: relative;
        overflow: hidden;
        margin: 8px 0 22px;
        padding: 28px 32px 26px;
        border-radius: 8px;
        color: #fff;
        background: linear-gradient(112deg, #07584f 0%, #087f70 66%, #bd8619 130%);
        box-shadow: 0 12px 28px rgba(8, 93, 79, .16);
        animation: suntrack-enter .45s ease-out both;
    }

    .suntrack-hero::after {
        position: absolute;
        right: 0;
        bottom: 0;
        width: 42%;
        height: 4px;
        content: "";
        background: linear-gradient(90deg, var(--sun-gold), #f6d26d, var(--sun-coral));
    }

    .suntrack-hero-kicker {
        color: #f7d77e;
        font-size: .75rem;
        font-weight: 700;
        letter-spacing: 1.1px;
    }

    .suntrack-hero h1 {
        margin: 5px 0 0;
        color: white !important;
        font-size: 46px;
        line-height: 1.15;
        text-shadow: 0 2px 18px rgba(0, 44, 38, .18);
    }

    .suntrack-hero h1 span {
        color: #ffd25e;
    }

    .suntrack-hero p {
        margin: 6px 0 0;
        color: rgba(255, 255, 255, .86);
        font-size: 1.08rem;
        font-weight: 500;
    }

    .suntrack-hero p span {
        color: #ffd25e;
        font-weight: 700;
    }

    @keyframes suntrack-enter {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @media (prefers-reduced-motion: reduce) {
        .suntrack-hero { animation: none; }
    }

    main h2 {
        padding-left: 12px;
        border-left: 4px solid var(--sun-coral);
        color: #12645c;
    }

    [data-testid="stSlider"] [data-rac][data-orientation="horizontal"] > [data-rac][data-orientation="horizontal"] > div:first-child {
        background-color: #c8d8d2 !important;
        border-radius: 999px;
        filter: hue-rotate(165deg);
    }

    [data-testid="stSlider"] [data-rac][data-orientation="horizontal"] > div:nth-child(2) {
        background-color: var(--sun-green) !important;
        border-radius: 50%;
        box-shadow: 0 0 0 4px rgba(8, 127, 112, .14);
    }

    [data-testid="stSliderThumbValue"] {
        color: var(--sun-green);
    }

    [data-testid="stSliderThumbValue"] [data-testid="stMarkdownContainer"] p {
        color: var(--sun-green) !important;
    }

    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, .94);
        border: 1px solid var(--sun-line);
        border-top: 4px solid var(--sun-gold);
        border-radius: 8px;
        padding: 16px 18px;
        box-shadow: 0 5px 16px rgba(23, 43, 54, .055);
    }

    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(4n + 2) [data-testid="stMetric"] {
        border-top-color: var(--sun-blue);
    }

    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(4n + 3) [data-testid="stMetric"] {
        border-top-color: var(--sun-coral);
    }

    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(4n + 4) [data-testid="stMetric"] {
        border-top-color: var(--sun-green);
    }

    [data-testid="stMetricLabel"] p {
        color: var(--sun-muted);
        min-height: 2.4rem;
        overflow: visible;
        font-size: .78rem;
        font-weight: 600;
        line-height: 1.25;
        white-space: normal;
        text-overflow: clip;
    }

    [data-testid="stMetricValue"] {
        color: var(--sun-ink);
        font-family: 'Manrope', sans-serif;
        font-weight: 700;
        font-size: 1.55rem;
        overflow-wrap: anywhere;
    }

    [data-testid="stMetricValue"] [data-testid="stMarkdownContainer"] {
        overflow: visible;
    }

    [data-testid="stMetricValue"] [data-testid="stMarkdownContainer"] p {
        width: 100%;
        margin: 0;
        overflow: visible;
        font-size: 24px !important;
        text-overflow: clip;
        white-space: nowrap;
    }

    [data-testid="stVerticalBlock"] > [data-testid="stPlotlyChart"] {
        background: rgba(255, 255, 255, .94);
        border: 1px solid #d5e4df;
        border-radius: 8px;
        padding: 8px;
        box-shadow: 0 5px 18px rgba(23, 43, 54, .045);
    }

    [data-testid="stBaseButton-primary"],
    [data-testid="stDownloadButton"] button {
        background: var(--sun-green);
        border-color: var(--sun-green);
        color: white;
        font-weight: 700;
        border-radius: 6px;
    }

    [data-testid="stBaseButton-primary"]:hover,
    [data-testid="stDownloadButton"] button:hover {
        background: #105f53;
        border-color: #105f53;
        color: white;
    }

    [data-testid="stExpander"] {
        border: 1px solid #d9e5dc;
        border-radius: 6px;
        background: rgba(255, 255, 255, .72);
    }

    [data-testid="stCaptionContainer"] {
        color: var(--sun-muted);
    }

    @media (max-width: 700px) {
        .suntrack-hero { padding: 22px 20px; }
        .suntrack-hero h1 { font-size: 32px; }
        [data-testid="stMetric"] { padding: 12px; }
        [data-testid="stMetricValue"] [data-testid="stMarkdownContainer"] p {
            font-size: 20px !important;
        }
        [data-testid="stVerticalBlock"] > [data-testid="stPlotlyChart"] { padding: 2px; }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------
def integrate_trapezoid(y, x):
    """
    Integrate y over x using the trapezoidal rule.
    This implementation does not depend on np.trapz()
    or np.trapezoid(), so it is compatible with different
    NumPy versions.
    """
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)

    if y.ndim != 1 or x.ndim != 1:
        raise ValueError("y and x must be one-dimensional arrays.")

    if len(y) != len(x):
        raise ValueError("y and x must have the same length.")

    if len(x) < 2:
        return 0.0

    return float(
        np.sum(
            (y[:-1] + y[1:]) * np.diff(x) / 2.0
        )
    )


def calculate_instantaneous_power(
    irradiance,
    panel_area,
    efficiency,
    solar_elevation,
    panel_tilt,
    temperature,
    shade
):
    """
    Simplified 2D photovoltaic power model.
    """

    reference_temperature = 25.0

    # Illustrative temperature coefficient:
    # -0.4% per degree Celsius
    temperature_coefficient = -0.004

    incidence_angle = abs(
        90.0 - solar_elevation - panel_tilt
    )

    orientation_factor = max(
        0.0,
        math.cos(math.radians(incidence_angle))
    )

    effective_irradiance = (
        irradiance * orientation_factor
    )

    shaded_irradiance = (
        effective_irradiance *
        (1.0 - shade / 100.0)
    )

    adjusted_efficiency = efficiency * (
        1.0 + temperature_coefficient *
        (temperature - reference_temperature)
    )

    adjusted_efficiency = max(
        0.0,
        adjusted_efficiency
    )

    power = (
        adjusted_efficiency *
        panel_area *
        shaded_irradiance
    )

    return {
        "power": power,
        "incidence_angle": incidence_angle,
        "effective_irradiance": effective_irradiance,
        "shaded_irradiance": shaded_irradiance,
        "adjusted_efficiency": adjusted_efficiency,
        "orientation_factor": orientation_factor
    }


def make_daily_profiles(
    max_irradiance,
    max_solar_elevation
):
    """
    Create idealized sinusoidal daylight profiles
    from 06:00 to 18:00.
    """

    hours = np.arange(
        6.0,
        18.0001,
        0.1
    )

    solar_shape = np.maximum(
        0.0,
        np.sin(
            np.pi * (hours - 6.0) / 12.0
        )
    )

    elevation = (
        max_solar_elevation * solar_shape
    )

    irradiance_profile = (
        max_irradiance * solar_shape
    )

    return hours, elevation, irradiance_profile


def calculate_daily_power(
    hours,
    solar_elevation,
    irradiance_profile,
    panel_area,
    efficiency,
    panel_tilt,
    temperature,
    shade
):

    values = []

    for elev, irradiance in zip(
        solar_elevation,
        irradiance_profile
    ):

        result = calculate_instantaneous_power(
            irradiance=irradiance,
            panel_area=panel_area,
            efficiency=efficiency,
            solar_elevation=elev,
            panel_tilt=panel_tilt,
            temperature=temperature,
            shade=shade
        )

        values.append(result["power"])

    return np.asarray(
        values,
        dtype=float
    )


def calculate_daily_energy(
    power_values,
    hours
):
    """
    Returns daily energy in Wh.
    Power is in W and time is in hours.
    """

    return integrate_trapezoid(
        power_values,
        hours
    )


def create_suntrack_pdf():

    if not REPORTLAB_AVAILABLE:
        return None

    report_current_power = instant_result["power"]

    report_hour_energy = report_current_power

    report_energy_current = (
        calculate_daily_energy(
            daily_power,
            time
        ) / 1000.0
    )

    report_energy_no_shade = (
        calculate_daily_energy(
            power_no_shading,
            time
        ) / 1000.0
    )

    report_energy_optimized = (
        calculate_daily_energy(
            power_optimized,
            time
        ) / 1000.0
    )

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "SunTrackTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#D99000"),
        fontSize=20,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        "SunTrackSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=9,
        textColor=colors.grey,
        spaceAfter=18
    )

    story = [
        Paragraph("SUNTRACK", title_style),

        Paragraph(
            "Solar Energy Simulation Report",
            subtitle_style
        ),

        Paragraph(
            "1. Simulation Parameters",
            styles["Heading2"]
        )
    ]

    parameter_data = [
        ["Parameter", "Simulation Value"],

        [
            "Solar irradiance peak",
            f"{G:.1f} W/m2"
        ],

        [
            "Panel area",
            f"{A:.2f} m2"
        ],

        [
            "Initial panel efficiency",
            f"{eff * 100:.2f}%"
        ],

        [
            "Panel temperature",
            f"{T_cell:.1f} deg C"
        ],

        [
            "Maximum solar elevation",
            f"{alpha:.1f} deg"
        ],

        [
            "Panel tilt angle",
            f"{beta:.1f} deg"
        ],

        [
            "Shading level",
            f"{shading:.1f}%"
        ],

        [
            "Temperature-adjusted efficiency",
            f"{eff_temp * 100:.2f}%"
        ]
    ]

    parameter_table = Table(
        parameter_data,
        colWidths=[230, 230]
    )

    parameter_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#F2B84B")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.black
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            )
        ])
    )

    story.extend([
        parameter_table,
        Spacer(1, 18)
    ])

    story.append(
        Paragraph(
            "2. Simulation Results",
            styles["Heading2"]
        )
    )

    result_data = [
        ["Output", "Result"],

        [
            "Instantaneous output power",
            f"{report_current_power:.2f} W"
        ],

        [
            "Energy for one hour at current power",
            f"{report_hour_energy:.2f} Wh"
        ],

        [
            "Estimated daily energy - current condition",
            f"{report_energy_current:.3f} kWh"
        ],

        [
            "Estimated daily energy - no shading",
            f"{report_energy_no_shade:.3f} kWh"
        ],

        [
            "Estimated daily energy - optimized tilt",
            f"{report_energy_optimized:.3f} kWh"
        ],

        [
            "Daily energy optimal tilt",
            f"{daily_optimal_angle:.1f} deg"
        ],

        [
            "Reference / measured power",
            f"{reference_power:.2f} W"
        ],

        [
            "Absolute power error",
            f"{power_abs_error:.2f} W"
        ],

        [
            "Relative power error",
            (
                f"{power_rel_error:.2f}%"
                if power_rel_error is not None
                else "Not defined"
            )
        ],

        [
            "Reference / measured daily energy",
            f"{reference_daily_energy:.2f} Wh"
        ],

        [
            "Absolute daily-energy error",
            f"{energy_abs_error:.2f} Wh"
        ],

        [
            "Relative daily-energy error",
            (
                f"{energy_rel_error:.2f}%"
                if energy_rel_error is not None
                else "Not defined"
            )
        ]
    ]

    result_table = Table(
        result_data,
        colWidths=[280, 180]
    )

    result_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#DCEAF7")
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            )
        ])
    )

    story.extend([
        result_table,
        Spacer(1, 18)
    ])

    story.append(
        Paragraph(
            "3. Physics Model",
            styles["Heading2"]
        )
    )

    physics_text = (
        "The electrical output power is estimated using "
        "P = eta_T * A * G_shaded. The effective irradiance is "
        "adjusted using a simplified angle-of-incidence factor "
        "and a uniform shading factor. Panel efficiency is adjusted "
        "using a linear temperature coefficient."
    )

    story.append(
        Paragraph(
            physics_text,
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "4. Assumptions and Limitations",
            styles["Heading2"]
        )
    )

    limitations = (
        "This is an educational, simplified 2D model. The daily solar "
        "irradiance and solar elevation are represented by idealized "
        "sinusoidal profiles between 06:00 and 18:00. Panel temperature "
        "is assumed constant during the day. Shading is treated as a "
        "uniform reduction in irradiance. The model does not include "
        "solar azimuth, diffuse radiation, weather variability, "
        "bypass-diode behavior, inverter losses, or measured panel data. "
        "The temperature coefficient is illustrative and should be "
        "replaced with the value in the actual panel datasheet."
    )

    story.append(
        Paragraph(
            limitations,
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 16))

    story.append(
        Paragraph(
            (
                "Report generated: "
                f"{datetime.now().strftime('%d %B %Y, %H:%M:%S')}"
            ),
            styles["Italic"]
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------
st.markdown(
    """
    <section class="suntrack-hero">
        <div class="suntrack-hero-kicker">SOLAR ENERGY · MODEL 2.8</div>
        <h1>SunTrack <span>☀</span></h1>
        <p>Follow the sun. <span>Find the power.</span></p>
    </section>
    """,
    unsafe_allow_html=True
)

st.divider()


# ------------------------------------------------------------
# SIDEBAR - USER INPUTS
# ------------------------------------------------------------
st.sidebar.header("Simulation setup")

with st.sidebar.expander("Panel specification", expanded=True):
    A = st.slider(
        "Panel area (m²)", 0.5, 5.0, 1.6, step=0.1,
        key="panel_area"
    )
    eff_percent = st.slider(
        "Panel efficiency (%)", 5, 30, 20, step=1,
        key="panel_efficiency"
    )
    T_cell = st.slider(
        "Panel temperature (°C)", 15, 75, 25, step=1,
        key="panel_temperature"
    )

with st.sidebar.expander("Sun conditions", expanded=True):
    G = st.slider(
        "Peak irradiance (W/m²)", 100, 1200, 800, step=10,
        key="peak_irradiance"
    )
    alpha = st.slider(
        "Maximum solar elevation (°)", 0, 90, 50, step=1,
        key="solar_elevation"
    )
    shading = st.slider(
        "Uniform shading (%)", 0, 100, 0, step=1,
        key="shading_level"
    )

with st.sidebar.expander("Panel orientation", expanded=True):
    beta = st.slider(
        "Panel tilt angle (°)", 0, 90, 40, step=1,
        key="panel_tilt"
    )

eff = eff_percent / 100.0

st.sidebar.divider()

st.sidebar.caption(
    "Daily prediction uses an idealized 06:00-18:00 solar profile."
)


# ------------------------------------------------------------
# INSTANTANEOUS PHYSICS CALCULATION
# ------------------------------------------------------------
instant_result = calculate_instantaneous_power(
    irradiance=G,
    panel_area=A,
    efficiency=eff,
    solar_elevation=alpha,
    panel_tilt=beta,
    temperature=T_cell,
    shade=shading
)

P = instant_result["power"]

theta = instant_result["incidence_angle"]

G_effective = instant_result["effective_irradiance"]

G_shaded = instant_result["shaded_irradiance"]

eff_temp = instant_result["adjusted_efficiency"]

E = P * 1.0

beta_opt = 90.0 - alpha


# ------------------------------------------------------------
# DASHBOARD
# ------------------------------------------------------------
st.header(
    "Simulation Dashboard"
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Instantaneous Output Power",
    f"{P:.2f} W"
)

col2.metric(
    "Effective Irradiance",
    f"{G_shaded:.1f} W/m²"
)

col3.metric(
    "Energy (1 hour)",
    f"{E:.2f} Wh"
)

col4.metric(
    "Adjusted Efficiency",
    f"{eff_temp * 100:.2f}%"
)

st.caption(
    f"Angle of incidence: {theta:.1f}° | "
    f"Geometrical optimum for this instant: {beta_opt:.1f}°"
)

st.divider()


# ------------------------------------------------------------
# SHADING VISUALIZATION
# ------------------------------------------------------------
st.header(
    "Solar Panel Shading Visualization"
)

st.write(
    "Conceptual 10 × 10 panel map. Each square represents an equal "
    "fraction of the panel area; this is not an electrical cell model."
)

x_shaded = []
y_shaded = []

x_lit = []
y_lit = []

shaded_cells = int(round(shading))

for i in range(100):

    x = i % 10

    y = 9 - (i // 10)

    if i < shaded_cells:

        x_shaded.append(x)
        y_shaded.append(y)

    else:

        x_lit.append(x)
        y_lit.append(y)


fig_panel = go.Figure()

fig_panel.add_trace(
    go.Scatter(
        x=x_lit,
        y=y_lit,
        mode="markers",

        marker=dict(
            symbol="square",
            size=27,
            color="#F5C542",
            line=dict(
                color="#D49D20",
                width=1
            )
        ),

        name="Unshaded area"
    )
)

fig_panel.add_trace(
    go.Scatter(
        x=x_shaded,
        y=y_shaded,
        mode="markers",

        marker=dict(
            symbol="square",
            size=27,
            color="#555B65",
            line=dict(
                color="#343A40",
                width=1
            )
        ),

        name="Shaded area"
    )
)

fig_panel.update_layout(
    title=f"Conceptual Panel Coverage: {shading}% Shaded",

    height=350,

    xaxis=dict(
        visible=False,
        range=[-0.6, 9.6]
    ),

    yaxis=dict(
        visible=False,
        range=[-0.6, 9.6],
        scaleanchor="x"
    ),

    template="plotly_white",

    margin=dict(
        l=10,
        r=10,
        t=50,
        b=40
    ),

    legend=dict(
        orientation="h",
        y=-0.1
    )
)

st.plotly_chart(
    fig_panel,
    use_container_width=True
)

st.caption(
    "Yellow: unshaded area | Gray: shaded area. "
    "The shading percentage is applied uniformly in the power model."
)

st.divider()


# ------------------------------------------------------------
# POWER OUTPUT ANALYSIS
# ------------------------------------------------------------
st.header(
    "Power Output Analysis"
)

angles = np.linspace(
    0.0,
    90.0,
    181
)

powers = []

for angle in angles:

    result = calculate_instantaneous_power(
        irradiance=G,
        panel_area=A,
        efficiency=eff,
        solar_elevation=alpha,
        panel_tilt=angle,
        temperature=T_cell,
        shade=shading
    )

    powers.append(
        result["power"]
    )


powers = np.asarray(
    powers
)

best_index = int(
    np.argmax(powers)
)

best_angle = float(
    angles[best_index]
)

best_power = float(
    powers[best_index]
)

current_power = P

power_gain = (
    best_power - current_power
)

improvement = (
    (power_gain / current_power) * 100.0
    if current_power > 0
    else 0.0
)


fig_angle = go.Figure()

fig_angle.add_trace(
    go.Scatter(
        x=angles,
        y=powers,
        mode="lines",
        name="Simulated output power",

        line=dict(
            color="#F4A623",
            width=3
        ),

        fill="tozeroy",

        fillcolor="rgba(244,166,35,0.12)"
    )
)

fig_angle.add_trace(
    go.Scatter(
        x=[beta],
        y=[current_power],
        mode="markers",
        name="Current panel angle",

        marker=dict(
            color="#2878B5",
            size=12
        )
    )
)

fig_angle.add_trace(
    go.Scatter(
        x=[best_angle],
        y=[best_power],
        mode="markers",
        name="Maximum-power angle",

        marker=dict(
            color="#16A085",
            size=14,
            symbol="star"
        )
    )
)

fig_angle.update_layout(
    title="Output Power as a Function of Panel Tilt",

    xaxis_title="Panel Tilt Angle (°)",

    yaxis_title="Output Power (W)",

    template="plotly_white",

    hovermode="x unified",

    height=450,

    xaxis=dict(
        dtick=10,
        showgrid=True,
        gridcolor="#EAEAEA"
    ),

    yaxis=dict(
        rangemode="tozero",
        showgrid=True,
        gridcolor="#EAEAEA"
    )
)

st.plotly_chart(
    fig_angle,
    use_container_width=True
)

st.caption(
    "Blue marker: selected panel angle | "
    "Green star: angle producing the highest simulated instantaneous power."
)


st.subheader(
    "Automatic Instantaneous Angle Optimization"
)

c1, c2, c3 = st.columns(3)

c1.metric(
    "Current Panel Angle",
    f"{beta:.1f}°"
)

c2.metric(
    "Optimal Panel Angle",
    f"{best_angle:.1f}°"
)

c3.metric(
    "Maximum Output Power",
    f"{best_power:.2f} W"
)

st.write(
    f"Potential power gain: **{power_gain:.2f} W "
    f"({improvement:.2f}%)**"
)

st.info(
    "This optimization searches panel tilt angles from 0° to 90° "
    "for the selected instantaneous solar elevation. It is not the "
    "same as optimizing total energy over an entire day."
)

st.divider()


# ------------------------------------------------------------
# DAILY ENERGY PREDICTION
# ------------------------------------------------------------
st.header(
    "Daily Energy Prediction"
)

st.write(
    "Estimate solar power and accumulated energy during an idealized "
    "day from 06:00 to 18:00."
)

time, solar_elevation, daily_irradiance = (
    make_daily_profiles(G, alpha)
)

daily_power = calculate_daily_power(
    time,
    solar_elevation,
    daily_irradiance,
    A,
    eff,
    beta,
    T_cell,
    shading
)

dt = float(
    time[1] - time[0]
)

energy_intervals = (
    (daily_power[:-1] + daily_power[1:]) / 2.0
) * dt

cumulative_energy = np.concatenate(
    (
        [0.0],
        np.cumsum(energy_intervals)
    )
)

total_daily_energy = float(
    cumulative_energy[-1]
)

peak_index = int(
    np.argmax(daily_power)
)

peak_power = float(
    daily_power[peak_index]
)

peak_time = float(
    time[peak_index]
)


c1, c2, c3 = st.columns(3)

c1.metric(
    "Estimated Daily Energy",
    f"{total_daily_energy:.2f} Wh"
)

c2.metric(
    "Maximum Daily Power",
    f"{peak_power:.2f} W"
)

peak_hour = int(peak_time)

peak_minute = int(
    round((peak_time - peak_hour) * 60)
)

if peak_minute == 60:

    peak_hour += 1

    peak_minute = 0

c3.metric(
    "Peak Production Time",
    f"{peak_hour:02d}:{peak_minute:02d}"
)


fig_daily = go.Figure()

fig_daily.add_trace(
    go.Scatter(
        x=time,
        y=daily_power,
        mode="lines",
        name="Solar power",

        line=dict(
            color="#F4A623",
            width=4,
            shape="spline"
        ),

        fill="tozeroy",

        fillcolor="rgba(244,166,35,0.15)"
    )
)

fig_daily.add_trace(
    go.Scatter(
        x=[peak_time],
        y=[peak_power],
        mode="markers",
        name="Peak power",

        marker=dict(
            color="#16A085",
            size=13,
            symbol="star"
        )
    )
)

fig_daily.update_layout(
    title="Daily Solar Power Generation",

    xaxis_title="Time of Day",

    yaxis_title="Output Power (W)",

    xaxis=dict(
        dtick=1,
        showgrid=True,
        gridcolor="#EAEAEA"
    ),

    yaxis=dict(
        rangemode="tozero",
        showgrid=True,
        gridcolor="#EAEAEA"
    ),

    template="plotly_white",

    hovermode="x unified",

    height=400
)

st.plotly_chart(
    fig_daily,
    use_container_width=True
)


st.subheader(
    "Cumulative Energy Production"
)

fig_energy = go.Figure()

fig_energy.add_trace(
    go.Scatter(
        x=time,
        y=cumulative_energy,
        mode="lines",
        name="Cumulative energy",

        line=dict(
            color="#2878B5",
            width=4,
            shape="spline"
        ),

        fill="tozeroy",

        fillcolor="rgba(40,120,181,0.12)"
    )
)

fig_energy.update_layout(
    title="Accumulated Solar Energy",

    xaxis_title="Time of Day",

    yaxis_title="Accumulated Energy (Wh)",

    xaxis=dict(
        dtick=1,
        showgrid=True,
        gridcolor="#EAEAEA"
    ),

    yaxis=dict(
        rangemode="tozero",
        showgrid=True,
        gridcolor="#EAEAEA"
    ),

    template="plotly_white",

    hovermode="x unified",

    height=400
)

st.plotly_chart(
    fig_energy,
    use_container_width=True
)

st.info(
    "Daily energy is obtained by trapezoidal numerical integration "
    "of the simulated power curve. The model assumes sinusoidal "
    "irradiance and solar elevation profiles, constant panel temperature, "
    "fixed panel tilt, and uniform shading."
)

st.divider()


# ------------------------------------------------------------
# SCENARIO COMPARISON
# ------------------------------------------------------------
st.header(
    "Solar Panel Scenario Comparison"
)

st.write(
    "Compare estimated daily energy under three operating scenarios."
)

power_current = daily_power

power_no_shading = calculate_daily_power(
    time,
    solar_elevation,
    daily_irradiance,
    A,
    eff,
    beta,
    T_cell,
    0
)

energy_current = calculate_daily_energy(
    power_current,
    time
)

energy_no_shading = calculate_daily_energy(
    power_no_shading,
    time
)

candidate_angles = np.linspace(
    0.0,
    90.0,
    181
)

candidate_energies = []

for candidate in candidate_angles:

    candidate_power = calculate_daily_power(
        time,
        solar_elevation,
        daily_irradiance,
        A,
        eff,
        candidate,
        T_cell,
        shading
    )

    candidate_energies.append(
        calculate_daily_energy(
            candidate_power,
            time
        )
    )


optimal_index = int(
    np.argmax(candidate_energies)
)

daily_optimal_angle = float(
    candidate_angles[optimal_index]
)

power_optimized = calculate_daily_power(
    time,
    solar_elevation,
    daily_irradiance,
    A,
    eff,
    daily_optimal_angle,
    T_cell,
    shading
)

energy_optimized = calculate_daily_energy(
    power_optimized,
    time
)


c1, c2, c3 = st.columns(3)

c1.metric(
    "Current Condition",
    f"{energy_current:.2f} Wh"
)

c2.metric(
    "Without Shading",
    f"{energy_no_shading:.2f} Wh"
)

c3.metric(
    "Optimized Daily Tilt",
    f"{energy_optimized:.2f} Wh",

    help=(
        f"Optimal daily tilt: "
        f"{daily_optimal_angle:.1f} degrees"
    )
)


fig_comparison = go.Figure()

scenario_names = [
    "Current condition",
    "Without shading",
    "Optimized tilt"
]

scenario_energies = [
    energy_current,
    energy_no_shading,
    energy_optimized
]

fig_comparison.add_trace(
    go.Bar(
        x=scenario_names,
        y=scenario_energies,

        text=[
            f"{v:.1f} Wh"
            for v in scenario_energies
        ],

        textposition="outside",

        marker_color=[
            "#2878B5",
            "#F4A623",
            "#16A085"
        ]
    )
)

fig_comparison.update_layout(
    title="Comparison of Daily Energy Production",

    xaxis_title="Simulation Scenario",

    yaxis_title="Daily Energy (Wh)",

    template="plotly_white",

    height=430,

    showlegend=False,

    yaxis=dict(
        rangemode="tozero",
        showgrid=True,
        gridcolor="#EAEAEA"
    )
)

st.plotly_chart(
    fig_comparison,
    use_container_width=True
)


st.subheader(
    "Power Profile Comparison"
)

fig_scenarios = go.Figure()

fig_scenarios.add_trace(
    go.Scatter(
        x=time,
        y=power_current,
        mode="lines",
        name="Current condition",

        line=dict(
            color="#2878B5",
            width=3
        )
    )
)

fig_scenarios.add_trace(
    go.Scatter(
        x=time,
        y=power_no_shading,
        mode="lines",
        name="Without shading",

        line=dict(
            color="#F4A623",
            width=3
        )
    )
)

fig_scenarios.add_trace(
    go.Scatter(
        x=time,
        y=power_optimized,
        mode="lines",
        name="Optimized tilt",

        line=dict(
            color="#16A085",
            width=3
        )
    )
)

fig_scenarios.update_layout(
    title="Daily Power Profile Under Different Scenarios",

    xaxis_title="Time of Day",

    yaxis_title="Output Power (W)",

    template="plotly_white",

    hovermode="x unified",

    height=450,

    xaxis=dict(
        dtick=1,
        showgrid=True,
        gridcolor="#EAEAEA"
    ),

    yaxis=dict(
        rangemode="tozero",
        showgrid=True,
        gridcolor="#EAEAEA"
    )
)

st.plotly_chart(
    fig_scenarios,
    use_container_width=True
)

st.info(
    "Current condition uses the selected tilt and shading. Without "
    "shading removes the shading loss while retaining the selected tilt. "
    "Optimized tilt selects the angle that maximizes integrated daily "
    "energy under the selected shading level."
)

st.caption(
    "All scenarios use the same idealized solar profiles, panel area, "
    "efficiency, and constant temperature."
)

st.divider()


# ------------------------------------------------------------
# INTERACTIVE 3D SOLAR PANEL VISUALIZATION
# ------------------------------------------------------------
st.header(
    "Interactive 3D Solar Panel Visualization"
)

st.write(
    "Explore the geometric relationship between the panel orientation "
    "and the position of the Sun in a simplified vertical plane."
)

beta_rad = math.radians(beta)

alpha_rad = math.radians(alpha)

panel_length = 1.0

panel_width = 0.7

panel_height = 1.2

u = np.linspace(
    -panel_length / 2,
    panel_length / 2,
    2
)

v = np.linspace(
    -panel_width / 2,
    panel_width / 2,
    2
)

U, V = np.meshgrid(u, v)

X_panel = U

Y_panel = V * math.cos(beta_rad)

Z_panel = (
    panel_height -
    V * math.sin(beta_rad)
)

panel_center = np.array([
    0.0,
    0.0,
    panel_height
])

sun_direction = np.array([
    0.0,
    math.cos(alpha_rad),
    math.sin(alpha_rad)
])

sun_position = (
    panel_center +
    2.5 * sun_direction
)


fig_3d = go.Figure()

fig_3d.add_trace(
    go.Surface(
        x=[[-2, 2], [-2, 2]],
        y=[[-2, -2], [2, 2]],
        z=[[0, 0], [0, 0]],

        opacity=0.18,

        showscale=False,

        colorscale=[
            [0, "#D8DEE9"],
            [1, "#D8DEE9"]
        ],

        name="Ground"
    )
)

fig_3d.add_trace(
    go.Surface(
        x=X_panel,
        y=Y_panel,
        z=Z_panel,

        opacity=0.95,

        showscale=False,

        colorscale=[
            [0, "#2878B5"],
            [1, "#56A6D8"]
        ],

        name="Solar panel"
    )
)


# Panel perimeter
corners = [
    (-panel_length / 2, -panel_width / 2),
    (panel_length / 2, -panel_width / 2),
    (panel_length / 2, panel_width / 2),
    (-panel_length / 2, panel_width / 2),
    (-panel_length / 2, -panel_width / 2)
]

edge_x = []
edge_y = []
edge_z = []

for x_local, v_local in corners:

    edge_x.append(x_local)

    edge_y.append(
        v_local * math.cos(beta_rad)
    )

    edge_z.append(
        panel_height -
        v_local * math.sin(beta_rad)
    )


fig_3d.add_trace(
    go.Scatter3d(
        x=edge_x,
        y=edge_y,
        z=edge_z,

        mode="lines",

        line=dict(
            color="#123B5D",
            width=6
        ),

        name="Panel frame"
    )
)


fig_3d.add_trace(
    go.Scatter3d(
        x=[
            panel_center[0],
            sun_position[0]
        ],

        y=[
            panel_center[1],
            sun_position[1]
        ],

        z=[
            panel_center[2],
            sun_position[2]
        ],

        mode="lines",

        line=dict(
            color="#F4C542",
            width=6,
            dash="dash"
        ),

        name="Direction from panel to Sun"
    )
)


fig_3d.add_trace(
    go.Scatter3d(
        x=[sun_position[0]],
        y=[sun_position[1]],
        z=[sun_position[2]],

        mode="markers+text",

        marker=dict(
            size=13,
            color="#F4C542",
            symbol="circle"
        ),

        text=["SUN"],

        textposition="top center",

        name="Sun position"
    )
)


fig_3d.add_trace(
    go.Scatter3d(
        x=[0],
        y=[0],
        z=[panel_height],

        mode="markers+text",

        marker=dict(
            size=5,
            color="#123B5D"
        ),

        text=["Panel center"],

        textposition="bottom center",

        name="Panel center"
    )
)


fig_3d.update_layout(
    title="3D Geometry of Solar Panel and Sun Position",

    scene=dict(
        xaxis_title="X",
        yaxis_title="Y",
        zaxis_title="Height",

        aspectmode="manual",

        aspectratio=dict(
            x=1.2,
            y=1.2,
            z=0.8
        ),

        camera=dict(
            eye=dict(
                x=1.6,
                y=-1.8,
                z=1.2
            )
        )
    ),

    template="plotly_white",

    height=600,

    margin=dict(
        l=0,
        r=0,
        t=55,
        b=0
    )
)

st.plotly_chart(
    fig_3d,
    use_container_width=True
)

st.caption(
    "The dashed line indicates the direction from the panel toward the "
    "Sun, not the direction of photon travel. The 3D scene is a geometric "
    "illustration and is not a full ray-tracing simulation."
)

st.divider()


# ------------------------------------------------------------
# VALIDATION AND ERROR ANALYSIS
# ------------------------------------------------------------
st.header(
    "Model Validation and Error Analysis"
)

st.write(
    "Compare the simulation output with experimental measurements "
    "or a trusted reference value obtained under the same operating "
    "conditions. Enter measured values below."
)

val_col1, val_col2 = st.columns(2)


with val_col1:

    reference_power = st.number_input(
        "Reference / measured power (W)",

        min_value=0.0,

        max_value=100000.0,

        value=float(max(P, 0.0)),

        step=1.0,

        help=(
            "Enter the power measured from a real panel "
            "or provided by a reliable reference."
        )
    )


with val_col2:

    reference_daily_energy = st.number_input(
        "Reference / measured daily energy (Wh)",

        min_value=0.0,

        max_value=1000000.0,

        value=float(max(total_daily_energy, 0.0)),

        step=1.0,

        help=(
            "Enter measured daily energy for the same panel "
            "and comparable weather conditions."
        )
    )


power_abs_error = abs(
    P - reference_power
)

power_rel_error = (
    power_abs_error / abs(reference_power) * 100.0
    if reference_power > 0
    else None
)

energy_abs_error = abs(
    total_daily_energy - reference_daily_energy
)

energy_rel_error = (
    energy_abs_error /
    abs(reference_daily_energy) * 100.0
    if reference_daily_energy > 0
    else None
)


v1, v2, v3 = st.columns(3)

v1.metric(
    "Simulated Power",
    f"{P:.2f} W"
)

v2.metric(
    "Absolute Power Error",
    f"{power_abs_error:.2f} W"
)

v3.metric(
    "Relative Power Error",

    (
        f"{power_rel_error:.2f}%"
        if power_rel_error is not None
        else "Not defined"
    )
)


v4, v5, v6 = st.columns(3)

v4.metric(
    "Simulated Daily Energy",
    f"{total_daily_energy:.2f} Wh"
)

v5.metric(
    "Absolute Energy Error",
    f"{energy_abs_error:.2f} Wh"
)

v6.metric(
    "Relative Energy Error",

    (
        f"{energy_rel_error:.2f}%"
        if energy_rel_error is not None
        else "Not defined"
    )
)


if power_rel_error is None:

    st.warning(
        "Relative power error cannot be calculated because the reference "
        "power is zero. Enter a non-zero measured/reference value."
    )

else:

    st.latex(
        r"\mathrm{Relative\ Error}(\%) = "
        r"\left|\frac{P_{sim}-P_{ref}}{P_{ref}}\right|\times100\%"
    )

    if energy_rel_error is not None:

        st.write(
            f"Power relative error: **{power_rel_error:.2f}%**. "
            f"Daily-energy relative error: "
            f"**{energy_rel_error:.2f}%**."
        )

    else:

        st.write(
            f"Power relative error: **{power_rel_error:.2f}%**."
        )


fig_validation = go.Figure()

fig_validation.add_trace(
    go.Bar(
        x=[
            "Power (W)",
            "Daily energy (Wh)"
        ],

        y=[
            P,
            total_daily_energy
        ],

        name="Simulation",

        marker_color="#2878B5"
    )
)

fig_validation.add_trace(
    go.Bar(
        x=[
            "Power (W)",
            "Daily energy (Wh)"
        ],

        y=[
            reference_power,
            reference_daily_energy
        ],

        name="Reference / measurement",

        marker_color="#F4A623"
    )
)

fig_validation.update_layout(
    title="Simulation Results Compared with Reference Values",

    barmode="group",

    template="plotly_white",

    height=420,

    yaxis_title="Value (units shown on x-axis)"
)

st.plotly_chart(
    fig_validation,
    use_container_width=True
)


st.warning(
    "Important: this comparison is only meaningful when the reference "
    "measurement uses the same panel area, efficiency, irradiance, "
    "temperature, tilt, and shading conditions. A single comparison point "
    "is a preliminary check, not a complete scientific validation. "
    "For stronger validation, collect measurements at several irradiance "
    "levels and times, then calculate MAE, RMSE, and mean percentage error."
)

st.divider()


# ------------------------------------------------------------
# PDF REPORT EXPORT
# ------------------------------------------------------------
st.header(
    "Export Simulation Report"
)

st.write(
    "Generate a PDF summary containing the selected parameters, "
    "simulation results, physics model, and model limitations."
)

if REPORTLAB_AVAILABLE:

    pdf_data = create_suntrack_pdf()

    st.download_button(
        label="Download SunTrack Report (PDF)",

        data=pdf_data,

        file_name="SunTrack_Simulation_Report.pdf",

        mime="application/pdf",

        use_container_width=True
    )

else:

    st.warning(
        "PDF export requires ReportLab. Install it using: "
        "python -m pip install reportlab"
    )

st.divider()


# ------------------------------------------------------------
# PHYSICS MODEL AND LIMITATIONS
# ------------------------------------------------------------
st.header(
    "Physics Model"
)

st.subheader(
    "1. Electrical Output Power"
)

st.latex(
    r"P = \eta_T \times A \times G_{\mathrm{shaded}}"
)


st.subheader(
    "2. Effective Solar Irradiance"
)

st.latex(
    r"G_{\mathrm{shaded}} = G \times "
    r"\max(0,\cos\theta) \times "
    r"\left(1-\frac{S}{100}\right)"
)


st.subheader(
    "3. Temperature-Dependent Efficiency"
)

st.latex(
    r"\eta_T = \eta_{\mathrm{ref}} "
    r"\left[1+\gamma(T_{\mathrm{cell}}-T_{\mathrm{ref}})\right]"
)


st.subheader(
    "4. Angle of Incidence"
)

st.latex(
    r"\theta = |90^\circ-\alpha-\beta|"
)


st.markdown(
    r"""
    **Symbols**

    - $P$: estimated electrical output power (W).
    - $\eta_T$: panel efficiency after temperature correction.
    - $\eta_{\mathrm{ref}}$: panel efficiency at the reference temperature.
    - $A$: panel area (m²).
    - $G$: peak solar irradiance (W/m²).
    - $G_{\mathrm{shaded}}$: irradiance after orientation and shading losses (W/m²).
    - $\theta$: angle of incidence between the sunlight and panel normal (degrees).
    - $S$: uniform shading percentage (%).
    - $\alpha$: solar elevation angle (degrees).
    - $\beta$: panel tilt angle measured from the horizontal (degrees).
    - $\gamma$: temperature coefficient of efficiency (per °C).
    - $T_{\mathrm{cell}}$: panel cell temperature (°C).
    - $T_{\mathrm{ref}}$: reference temperature, set to 25 °C.
    """
)


st.warning(
    "Model limitations: SunTrack uses a simplified 2D photovoltaic model. "
    "The angle equation assumes the Sun and panel are in the same vertical "
    "plane. Daily irradiance and solar elevation are idealized sinusoidal "
    "profiles, panel temperature is constant, and shading is uniform. "
    "The model does not yet include solar azimuth, diffuse irradiance, "
    "weather variation, bypass-diode effects, inverter losses, or measured "
    "panel data. The temperature coefficient (-0.004 per °C) is an "
    "illustrative assumption; replace it with the actual module datasheet "
    "value for quantitative analysis."
)

st.divider()

st.caption(
    "SunTrack v2.8 | Solar Energy Optimization Simulator | "
    "Educational model - results are estimates, not guaranteed field output."
)