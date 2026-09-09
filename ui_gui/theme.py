"""Sistema de Diseño y Tema Visual Clean Windows 11 Light / Minimalist para PITA GUI."""

from __future__ import annotations
import customtkinter as ctk

# ----------------------------------------------------------------------
# PALETA DE COLORES - CLEAN WINDOWS 11 LIGHT / MINIMALIST
# ----------------------------------------------------------------------
class Colors:
    # Canvas & Layout
    BG_WINDOW = "#F3F4F6"       # Canvas principal (Gris/Slate suave)
    BG_PAGE = "#F3F4F6"         # Alias para páginas y modales
    BG_HEADER = "#FFFFFF"       # Barra superior header (Blanco Puro)
    BG_SIDEBAR = "#F8FAFC"      # Barra lateral de navegación
    BG_CARD = "#FFFFFF"         # Tarjetas y paneles elevados (Blanco Puro)
    BG_CARD_HOVER = "#F1F5F9"   # Hover sobre tarjetas y filas
    BG_INPUT = "#FFFFFF"        # Campos de texto e inputs
    
    # Bordes y Separadores
    BORDER_SUBTLE = "#E2E8F0"   # Borde delgado crisp (Slate 200)
    BORDER_ACCENT = "#0067C0"   # Borde activo azul Windows 11
    
    # Textos (Alta legibilidad)
    TEXT_MAIN = "#0F172A"       # Texto principal (Slate 900)
    TEXT_MUTED = "#64748B"      # Texto secundario (Slate 500)
    TEXT_ACCENT = "#0284C7"     # Texto de énfasis cian/azul (Sky 600)
    
    # Colores Primarios y de Acción (Windows 11 Royal Blue)
    WIN_BLUE = "#0067C0"        # Azul Windows 11 Accent
    WIN_BLUE_HOVER = "#005FB8"  # Hover Azul Windows
    
    ACCENT_PRIMARY = "#2563EB"  # Azul primario Fluent (Blue 600)
    ACCENT_PRIMARY_HOVER = "#1D4ED8" # Hover Azul primario
    
    ACCENT_SUCCESS = "#10B981"  # Verde Emerald de éxito/activo
    ACCENT_SUCCESS_HOVER = "#059669"
    
    ACCENT_WARNING = "#F59E0B"  # Amber de advertencia
    ACCENT_WARNING_HOVER = "#D97706"
    
    ACCENT_DANGER = "#EF4444"   # Rojo Crimson de eliminación/alerta
    ACCENT_DANGER_HOVER = "#DC2626"
    
    ACCENT_INDIGO = "#4F46E5"   # Índigo limpio
    ACCENT_INDIGO_HOVER = "#4338CA"
    
    # Badges & Status Pills (Pastel Suave y Limpio)
    BADGE_ACTIVE_BG = "#DCFCE7"
    BADGE_ACTIVE_TXT = "#15803D"
    BADGE_ACTIVE_BORDER = "#86EFAC"
    
    BADGE_EBRA_BG = "#FEE2E2"
    BADGE_EBRA_TXT = "#B91C1C"
    BADGE_EBRA_BORDER = "#FCA5A5"
    
    BADGE_INFO_BG = "#E0F2FE"
    BADGE_INFO_TXT = "#0369A1"
    BADGE_INFO_BORDER = "#7DD3FC"


# ----------------------------------------------------------------------
# TIPOGRAFÍA Y FUENTES ESTILO SEGOE UI / INTER
# ----------------------------------------------------------------------
class Fonts:
    TITLE_LARGE = ("Segoe UI", 22, "bold")
    TITLE_MEDIUM = ("Segoe UI", 16, "bold")
    TITLE_SMALL = ("Segoe UI", 13, "bold")
    BODY_MAIN = ("Segoe UI", 12)
    BODY_BOLD = ("Segoe UI", 12, "bold")
    BODY_SMALL = ("Segoe UI", 11)
    CAPTION = ("Segoe UI", 10)


def aplicar_configuracion_tema() -> None:
    """Aplica la configuración global de CustomTkinter en modo Light Limpio."""
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")


def create_styled_tabview(parent: ctk.CTkFrame | ctk.CTk) -> ctk.CTkTabview:
    """Crea un CTkTabview estilizado con diseño limpio, claro e integrado estilo Windows 11."""
    tv = ctk.CTkTabview(
        parent,
        fg_color="transparent",
        segmented_button_fg_color="#E2E8F0",
        segmented_button_selected_color=Colors.WIN_BLUE,
        segmented_button_selected_hover_color=Colors.WIN_BLUE_HOVER,
        segmented_button_unselected_color="#FFFFFF",
        segmented_button_unselected_hover_color="#F1F5F9",
        text_color=Colors.TEXT_MAIN,
    )
    try:
        tv._segmented_button.configure(font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"))
    except Exception:
        pass
    return tv
