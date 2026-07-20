"""
Minimal line-icon set in the Lucide visual language: 24x24 viewbox,
stroke-based, rounded caps/joins, currentColor. These are original,
hand-drawn SVG paths (not copied from the Lucide library) built to match
its aesthetic for the sidebar nav and section headers.
"""

_ICON_PATHS = {
    "dashboard": '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    "file-text": '<path d="M6 2h9l5 5v15a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1z"/><path d="M14 2v5h5"/><line x1="8.5" y1="13" x2="15.5" y2="13"/><line x1="8.5" y1="17" x2="13" y2="17"/>',
    "brain": '<path d="M9 4a3 3 0 0 0-3 3v1a3 3 0 0 0-1.5 5.6A3 3 0 0 0 7 18a3 3 0 0 0 2 2.8V21a2 2 0 0 0 4 0v-.2A3 3 0 0 0 15 18a3 3 0 0 0 2.5-4.4A3 3 0 0 0 16 8V7a3 3 0 0 0-3-3z"/><line x1="9" y1="4" x2="9" y2="20"/><line x1="15" y1="4" x2="15" y2="20"/>',
    "search-check": '<circle cx="10.5" cy="10.5" r="6.5"/><line x1="19" y1="19" x2="15.3" y2="15.3"/><path d="M7.5 10.5l2 2 3.5-3.5"/>',
    "rocket": '<path d="M13 3c3 1 6 4 7 8-2 0-4 1-6 3s-3 4-3 6c-4-1-7-4-8-7 2-4 6-8 10-10z"/><circle cx="12" cy="9" r="1.6"/><path d="M6 15c-1.5 0-3 1.2-3 3.5S4.5 22 4.5 22 6 20.5 6 19s-.5-3-2-3z" transform="translate(0,-0.5)"/>',
    "map": '<polygon points="3,6 9,3 15,6 21,3 21,18 15,21 9,18 3,21"/><line x1="9" y1="3" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="21"/>',
    "bar-chart": '<line x1="5" y1="21" x2="5" y2="11"/><line x1="12" y1="21" x2="12" y2="6"/><line x1="19" y1="21" x2="19" y2="14"/><line x1="3" y1="21" x2="21" y2="21"/>',
    "settings": '<circle cx="12" cy="12" r="3"/><path d="M19.4 13a1.7 1.7 0 0 0 .34 1.87l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.7 1.7 0 0 0-1.87-.34 1.7 1.7 0 0 0-1 1.55V19a2 2 0 0 1-4 0v-.09a1.7 1.7 0 0 0-1-1.55 1.7 1.7 0 0 0-1.87.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.7 1.7 0 0 0 .34-1.87 1.7 1.7 0 0 0-1.55-1H4a2 2 0 0 1 0-4h.09a1.7 1.7 0 0 0 1.55-1 1.7 1.7 0 0 0-.34-1.87l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.7 1.7 0 0 0 1.87.34H10a1.7 1.7 0 0 0 1-1.55V4a2 2 0 0 1 4 0v.09a1.7 1.7 0 0 0 1 1.55 1.7 1.7 0 0 0 1.87-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.7 1.7 0 0 0-.34 1.87V10a1.7 1.7 0 0 0 1.55 1H20a2 2 0 0 1 0 4h-.09a1.7 1.7 0 0 0-1.55 1z"/>',
    "check": '<polyline points="20,6 9,17 4,12"/>',
    "upload": '<path d="M12 3v12"/><polyline points="7,8 12,3 17,8"/><path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/>',
    "compass": '<circle cx="12" cy="12" r="9"/><polygon points="15,9 13,13 9,15 11,11"/>',
    "target": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="0.7" fill="currentColor"/>',
    "sparkles": '<path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5z"/><path d="M19 15l.7 2.1 2.1.7-2.1.7L19 20.6l-.7-2.1-2.1-.7 2.1-.7z"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><polyline points="12,7 12,12 15.5,14"/>',
    "chevron-down": '<polyline points="6,9 12,15 18,9"/>',
    "download": '<path d="M12 3v12"/><polyline points="7,12 12,17 17,12"/><path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/>',
    "alert-triangle": '<path d="M12 3l10 18H2z"/><line x1="12" y1="9" x2="12" y2="14"/><circle cx="12" cy="17.2" r="0.6" fill="currentColor"/>',
    "key": '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9"/><path d="M16 7l3 3"/><path d="M13 10l2.5 2.5"/>',
    "trending-up": '<polyline points="3,17 9,11 13,15 21,7"/><polyline points="15,7 21,7 21,13"/>',
    "trending-down": '<polyline points="3,7 9,13 13,9 21,17"/><polyline points="15,17 21,17 21,11"/>',
    "minus": '<line x1="5" y1="12" x2="19" y2="12"/>',
    "layers": '<polygon points="12,2 22,8 12,14 2,8"/><polyline points="2,14 12,20 22,14"/>',
    "cpu": '<rect x="6" y="6" width="12" height="12" rx="1.5"/><rect x="10" y="10" width="4" height="4"/><line x1="2" y1="9" x2="6" y2="9"/><line x1="2" y1="15" x2="6" y2="15"/><line x1="18" y1="9" x2="22" y2="9"/><line x1="18" y1="15" x2="22" y2="15"/><line x1="9" y1="2" x2="9" y2="6"/><line x1="15" y1="2" x2="15" y2="6"/><line x1="9" y1="18" x2="9" y2="22"/><line x1="15" y1="18" x2="15" y2="22"/>',
    "database": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    "git-branch": '<line x1="7" y1="3" x2="7" y2="15"/><circle cx="7" cy="18" r="2.3"/><circle cx="17" cy="6" r="2.3"/><path d="M17 8.3a7 7 0 0 1-7 6.7"/>',
    "file-check": '<path d="M6 2h9l5 5v15a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1z"/><path d="M14 2v5h5"/><polyline points="8.5,15 11,17.5 15.5,12.5"/>',
    "arrow-right": '<line x1="4" y1="12" x2="20" y2="12"/><polyline points="14,6 20,12 14,18"/>',
    "flag": '<line x1="5" y1="3" x2="5" y2="21"/><path d="M5 4h13l-3 5 3 5H5"/>',
}


def icon(name: str, size: int = 18, color: str = "currentColor", stroke_width: float = 1.8) -> str:
    path = _ICON_PATHS.get(name, "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round">{path}</svg>'
    )