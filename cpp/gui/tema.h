#ifndef TEMA_H
#define TEMA_H

#include "imgui.h"

namespace pita {
namespace tema {

// ======================================================================
// PALETA DE COLORES - CLEAN WINDOWS 11 LIGHT
// (Réplica de ui_gui/theme.py)
// ======================================================================

// Canvas & Layout
inline ImVec4 BG_WINDOW()         { return ImVec4(0.953f, 0.957f, 0.965f, 1.0f); } // #F3F4F6
inline ImVec4 BG_HEADER()         { return ImVec4(1.0f, 1.0f, 1.0f, 1.0f); }       // #FFFFFF
inline ImVec4 BG_SIDEBAR()        { return ImVec4(0.973f, 0.980f, 0.988f, 1.0f); } // #F8FAFC
inline ImVec4 BG_CARD()           { return ImVec4(1.0f, 1.0f, 1.0f, 1.0f); }       // #FFFFFF
inline ImVec4 BG_CARD_HOVER()     { return ImVec4(0.945f, 0.961f, 0.976f, 1.0f); } // #F1F5F9

// Borders
inline ImVec4 BORDER_SUBTLE()     { return ImVec4(0.886f, 0.910f, 0.941f, 1.0f); } // #E2E8F0
inline ImVec4 BORDER_ACCENT()     { return ImVec4(0.0f, 0.404f, 0.753f, 1.0f); }   // #0067C0

// Text
inline ImVec4 TEXT_MAIN()         { return ImVec4(0.059f, 0.090f, 0.165f, 1.0f); } // #0F172A
inline ImVec4 TEXT_MUTED()        { return ImVec4(0.392f, 0.455f, 0.545f, 1.0f); } // #64748B
inline ImVec4 TEXT_ACCENT()       { return ImVec4(0.008f, 0.522f, 0.780f, 1.0f); } // #0284C7
inline ImVec4 TEXT_WHITE()        { return ImVec4(1.0f, 1.0f, 1.0f, 1.0f); }       // #FFFFFF

// Primary Action Colors
inline ImVec4 WIN_BLUE()          { return ImVec4(0.0f, 0.404f, 0.753f, 1.0f); }   // #0067C0
inline ImVec4 WIN_BLUE_HOVER()    { return ImVec4(0.0f, 0.373f, 0.722f, 1.0f); }   // #005FB8
inline ImVec4 ACCENT_PRIMARY()    { return ImVec4(0.145f, 0.388f, 0.922f, 1.0f); } // #2563EB
inline ImVec4 ACCENT_SUCCESS()    { return ImVec4(0.063f, 0.725f, 0.506f, 1.0f); } // #10B981
inline ImVec4 ACCENT_SUCCESS_H()  { return ImVec4(0.020f, 0.588f, 0.412f, 1.0f); } // #059669
inline ImVec4 ACCENT_WARNING()    { return ImVec4(0.961f, 0.620f, 0.043f, 1.0f); } // #F59E0B
inline ImVec4 ACCENT_DANGER()     { return ImVec4(0.937f, 0.267f, 0.267f, 1.0f); } // #EF4444
inline ImVec4 ACCENT_DANGER_H()   { return ImVec4(0.863f, 0.149f, 0.149f, 1.0f); } // #DC2626
inline ImVec4 ACCENT_INDIGO()     { return ImVec4(0.310f, 0.275f, 0.898f, 1.0f); } // #4F46E5

// Badge Colors
inline ImVec4 BADGE_ACTIVE_BG()   { return ImVec4(0.863f, 0.988f, 0.906f, 1.0f); } // #DCFCE7
inline ImVec4 BADGE_ACTIVE_TXT()  { return ImVec4(0.082f, 0.502f, 0.239f, 1.0f); } // #15803D
inline ImVec4 BADGE_EBRA_BG()     { return ImVec4(0.996f, 0.886f, 0.886f, 1.0f); } // #FEE2E2
inline ImVec4 BADGE_EBRA_TXT()    { return ImVec4(0.725f, 0.110f, 0.110f, 1.0f); } // #B91C1C
inline ImVec4 BADGE_INFO_BG()     { return ImVec4(0.878f, 0.949f, 0.996f, 1.0f); } // #E0F2FE
inline ImVec4 BADGE_INFO_TXT()    { return ImVec4(0.012f, 0.412f, 0.631f, 1.0f); } // #0369A1

// ======================================================================
// HELPERS
// ======================================================================

inline ImU32 toU32(const ImVec4& c) {
    return IM_COL32(
        (int)(c.x * 255.0f),
        (int)(c.y * 255.0f),
        (int)(c.z * 255.0f),
        (int)(c.w * 255.0f)
    );
}

inline ImVec4 withAlpha(const ImVec4& c, float a) {
    return ImVec4(c.x, c.y, c.z, a);
}

// ======================================================================
// APLICAR TEMA GLOBAL ImGui
// ======================================================================

inline void aplicarTema() {
    ImGuiStyle& style = ImGui::GetStyle();

    // Roundness & Spacing
    style.WindowRounding    = 6.0f;
    style.ChildRounding     = 6.0f;
    style.FrameRounding     = 5.0f;
    style.PopupRounding     = 6.0f;
    style.ScrollbarRounding = 8.0f;
    style.GrabRounding      = 4.0f;
    style.TabRounding       = 5.0f;

    style.WindowPadding     = ImVec2(12, 12);
    style.FramePadding      = ImVec2(10, 6);
    style.ItemSpacing       = ImVec2(10, 6);
    style.ItemInnerSpacing  = ImVec2(6, 4);
    style.ScrollbarSize     = 12.0f;
    style.GrabMinSize       = 8.0f;

    style.WindowBorderSize  = 1.0f;
    style.ChildBorderSize   = 1.0f;
    style.PopupBorderSize   = 1.0f;
    style.FrameBorderSize   = 1.0f;
    style.TabBorderSize     = 0.0f;

    // Colors
    ImVec4* colors = style.Colors;

    colors[ImGuiCol_WindowBg]           = BG_WINDOW();
    colors[ImGuiCol_ChildBg]            = ImVec4(0, 0, 0, 0); // transparent
    colors[ImGuiCol_PopupBg]            = BG_CARD();
    colors[ImGuiCol_Border]             = BORDER_SUBTLE();
    colors[ImGuiCol_BorderShadow]       = ImVec4(0, 0, 0, 0);

    colors[ImGuiCol_FrameBg]            = ImVec4(0.95f, 0.96f, 0.97f, 1.0f);
    colors[ImGuiCol_FrameBgHovered]     = ImVec4(0.92f, 0.93f, 0.95f, 1.0f);
    colors[ImGuiCol_FrameBgActive]      = ImVec4(0.88f, 0.90f, 0.93f, 1.0f);

    colors[ImGuiCol_TitleBg]            = BG_HEADER();
    colors[ImGuiCol_TitleBgActive]      = BG_HEADER();
    colors[ImGuiCol_TitleBgCollapsed]   = BG_HEADER();
    colors[ImGuiCol_MenuBarBg]          = BG_HEADER();

    colors[ImGuiCol_ScrollbarBg]        = ImVec4(0.96f, 0.97f, 0.98f, 1.0f);
    colors[ImGuiCol_ScrollbarGrab]      = ImVec4(0.80f, 0.83f, 0.87f, 1.0f);
    colors[ImGuiCol_ScrollbarGrabHovered] = ImVec4(0.70f, 0.73f, 0.78f, 1.0f);
    colors[ImGuiCol_ScrollbarGrabActive]  = ImVec4(0.60f, 0.63f, 0.68f, 1.0f);

    colors[ImGuiCol_CheckMark]          = WIN_BLUE();
    colors[ImGuiCol_SliderGrab]         = WIN_BLUE();
    colors[ImGuiCol_SliderGrabActive]   = WIN_BLUE_HOVER();

    colors[ImGuiCol_Button]             = WIN_BLUE();
    colors[ImGuiCol_ButtonHovered]      = WIN_BLUE_HOVER();
    colors[ImGuiCol_ButtonActive]       = ImVec4(0.0f, 0.33f, 0.65f, 1.0f);

    colors[ImGuiCol_Header]             = ImVec4(0.93f, 0.95f, 0.98f, 1.0f);
    colors[ImGuiCol_HeaderHovered]      = ImVec4(0.88f, 0.91f, 0.96f, 1.0f);
    colors[ImGuiCol_HeaderActive]       = ImVec4(0.83f, 0.87f, 0.94f, 1.0f);

    colors[ImGuiCol_Separator]          = BORDER_SUBTLE();
    colors[ImGuiCol_SeparatorHovered]   = WIN_BLUE();
    colors[ImGuiCol_SeparatorActive]    = WIN_BLUE_HOVER();

    colors[ImGuiCol_Tab]                = ImVec4(0.94f, 0.95f, 0.97f, 1.0f);
    colors[ImGuiCol_TabHovered]         = withAlpha(WIN_BLUE(), 0.25f);
    colors[ImGuiCol_TabSelected]        = WIN_BLUE();
    colors[ImGuiCol_TabDimmed]          = ImVec4(0.94f, 0.95f, 0.97f, 1.0f);
    colors[ImGuiCol_TabDimmedSelected]  = withAlpha(WIN_BLUE(), 0.5f);

    colors[ImGuiCol_TableHeaderBg]      = ImVec4(0.94f, 0.95f, 0.97f, 1.0f);
    colors[ImGuiCol_TableBorderStrong]  = BORDER_SUBTLE();
    colors[ImGuiCol_TableBorderLight]   = ImVec4(0.92f, 0.93f, 0.95f, 1.0f);
    colors[ImGuiCol_TableRowBg]         = ImVec4(0, 0, 0, 0);
    colors[ImGuiCol_TableRowBgAlt]      = ImVec4(0.97f, 0.98f, 0.99f, 1.0f);

    colors[ImGuiCol_Text]               = TEXT_MAIN();
    colors[ImGuiCol_TextDisabled]       = TEXT_MUTED();

    colors[ImGuiCol_PlotLines]          = WIN_BLUE();
    colors[ImGuiCol_PlotHistogram]      = WIN_BLUE();

    colors[ImGuiCol_ModalWindowDimBg]   = ImVec4(0.0f, 0.0f, 0.0f, 0.35f);

    colors[ImGuiCol_TextSelectedBg]     = withAlpha(WIN_BLUE(), 0.25f);
    colors[ImGuiCol_NavHighlight]       = WIN_BLUE();
}

} // namespace tema
} // namespace pita

#endif // TEMA_H
