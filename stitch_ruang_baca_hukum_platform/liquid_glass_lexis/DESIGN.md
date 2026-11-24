---
name: Liquid Glass Lexis
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#434654'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#737686'
  outline-variant: '#c3c6d7'
  surface-tint: '#0854d7'
  primary: '#003ca3'
  on-primary: '#ffffff'
  primary-container: '#0051d5'
  on-primary-container: '#c8d4ff'
  inverse-primary: '#b4c5ff'
  secondary: '#565e74'
  on-secondary: '#ffffff'
  secondary-container: '#dae2fd'
  on-secondary-container: '#5c647a'
  tertiary: '#004f35'
  on-tertiary: '#ffffff'
  tertiary-container: '#006a48'
  on-tertiary-container: '#60eeb1'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dbe1ff'
  primary-fixed-dim: '#b4c5ff'
  on-primary-fixed: '#00174b'
  on-primary-fixed-variant: '#003ea7'
  secondary-fixed: '#dae2fd'
  secondary-fixed-dim: '#bec6e0'
  on-secondary-fixed: '#131b2e'
  on-secondary-fixed-variant: '#3f465c'
  tertiary-fixed: '#6ffbbe'
  tertiary-fixed-dim: '#4edea3'
  on-tertiary-fixed: '#002113'
  on-tertiary-fixed-variant: '#005236'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display-lg:
    fontFamily: Outfit
    fontSize: 40px
    fontWeight: '600'
    lineHeight: 48px
    letterSpacing: -0.02em
  display-md:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.015em
  headline-lg:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Outfit
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  headline-sm:
    fontFamily: Outfit
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  title-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.04em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.05em
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  gutter: 1.5rem
  margin: 2.5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style

This design system expresses the intellectual prestige and refined composure of an elite university law faculty reading room (*Ruang Baca Fakultas Hukum*). The aesthetic fuses contemporary minimalist glassmorphism with juridical precision. The interface must communicate authority, focus, and transparency—transforming rigorous archival research into a frictionless, serene digital workspace.

### Core Tenets
- **Scholarly Transparency**: Utilizing ethereal, translucent white glass panels to structure dense legal texts, jurisprudence registers, and room reservation catalogs without visual congestion.
- **Juridical Decorum**: Balancing cutting-edge glassmorphism with traditional institutional sobriety through deep slate navy tones and measured proportions.
- **Architectural Stillness**: A serene atmospheric background reminiscent of natural daylight filtering through floor-to-ceiling library windows over polished stone and frosted partition screens.
- **Target Audience**: Law professors, doctoral researchers, postgraduate law candidates, and undergraduate honors scholars navigating jurisprudence repositories, primary source treaties, and quiet study alcoves.

## Colors

The palette establishes an intellectual hierarchy using deep slate navy for authoritative typography, cobalt blue for critical actions and active states, and a clean frosted glass canvas layered over subtle atmospheric cool glows.

### Color Roles & Semantics
- **Technical Cobalt Blue (`#0051D5` / `#316BF3`)**: Primary actions, active navigation anchors, highlighted citations, and primary metrics (*cth. Pinjam Buku, Akses Repositori*).
- **Deep Academic Navy (`#0F172A` / `#131B2E`)**: Display headings, legal document identifiers, and high-emphasis labels. Represents academic weight and permanence.
- **Soft Secondary Slate (`#475569` / `#64748B`)**: Body text, archival metadata (Nomor Panggil, Klasifikasi DDC, ISBN/ISSN), and unselected filter options.
- **Canvas & Glass Foundations**:
  - Atmospheric Canvas: `#F8FAFC` to `#EEF2F6` with subtle ambient radial gradients in `#E0E7FF` (opacity 40%).
  - Frosted Surface: `rgba(255, 255, 255, 0.75)` with high blur filters.
  - Border Highlights: Crisp top-left highlight of `rgba(255, 255, 255, 0.8)` grading down to `rgba(226, 232, 240, 0.6)`.
- **Status & Juridical Alerts**:
  - **Tersedia / Aktif (Emerald Green `#10B981`)**: Real-time availability, confirmed cubicle bookings, and returned loans.
  - **Keterlambatan / Denda (Crimson Red `#BA1A1A`)**: Expired borrow windows, disciplinary holds, and overdue book sanctions.
  - **Menunggu Konfirmasi (Warm Amber `#F59E0B`)**: Pending access requests for restricted rare manuscripts and thesis defense archives.

## Typography

The typographic system pairs the structural, geometric clarity of Outfit for headings, room identifiers, and quantitative circulation figures with the neutral legibility of Inter for body text, search outputs, and catalog records.

### Implementation Guidelines
- **Bahasa Indonesia Academic Standards**: Use proper grammatical capitalization and standardized academic terminology (*Katalog Induk*, *Yurisprudensi Mahkamah Agung*, *Ruang Baca Referensi*, *Status Sirkulasi*).
- **Tabular Figures**: Always enable tabular figures (`tnum`) in Inter for call numbers (Nomor Panggil DDC), ISBNs, timestamps, and citation indices to maintain column alignment across data tables.
- **Hierarchy Contrast**: Major section titles use Outfit Semibold with tight tracking (`-0.02em`) to produce a sleek, contemporary academic tone, while micro-copy such as status badges uses Inter Semibold in uppercase tracking (`0.05em`).

## Layout & Spacing

The layout is anchored to a 1440px desktop viewport structured via a 12-column responsive fluid grid. Generous breathing room between content modules mimics the peaceful volume of a physical library hall.

### Spatial Architecture
- **Desktop Grid (1440px)**: 12 columns with 24px (`1.5rem`) gutters and 40px (`2.5rem`) margins. Main reading room dashboard splits between a 280px fixed glass navigation rail, an 800px primary research viewport, and a 320px ambient study panel.
- **Rhythm**: All paddings and container heights follow an 8px grid cadence (`space-xs` = 4px, `space-sm` = 8px, `space-md` = 16px, `space-lg` = 24px, `space-xl` = 32px).
- **Glass Panel Nesting**: Inner cards nested within larger frosted glass panels must feature `space-md` padding to preserve spatial depth and perimeter refraction.

## Elevation & Depth

Visual depth is achieved through layered refraction, controlled optical blur, and subtle dual-toned edge highlights rather than dark, muddy dropshadows.

### The Glassmorphic Stack
- **Base Canvas**: Soft off-white `#F8FAFC` with two fixed ambient light gradients: `#E0E7FF` at 30% opacity blurred at 120px positioned in the upper right, and `#DBEAFE` at 25% opacity in the bottom left.
- **Level 1 (Structural Panels & Sidebars)**:
  - Background: `rgba(255, 255, 255, 0.72)`
  - Filter: `backdrop-filter: blur(20px) saturate(180%)`
  - Border: `1px solid rgba(255, 255, 255, 0.6)`
  - Shadow: `0 8px 32px -4px rgba(15, 23, 42, 0.04), 0 2px 8px -2px rgba(15, 23, 42, 0.02)`
- **Level 2 (Interactive Cards & Floating Modals)**:
  - Background: `rgba(255, 255, 255, 0.85)`
  - Filter: `backdrop-filter: blur(16px)`
  - Border: `1px solid rgba(255, 255, 255, 0.8)`
  - Shadow: `0 16px 36px -6px rgba(15, 23, 42, 0.06), 0 4px 12px -2px rgba(15, 23, 42, 0.03)`
- **Level 3 (Dropdowns, Overlays & Active Hover States)**:
  - Background: `rgba(255, 255, 255, 0.95)`
  - Border: `1px solid rgba(0, 81, 213, 0.15)`
  - Shadow: `0 24px 48px -8px rgba(15, 23, 42, 0.08), 0 0 0 1px rgba(255, 255, 255, 0.9)`

## Shapes

The design uses a high roundedness scale (`level 3`), combining generous pill geometry for interactive controls with sweeping rounded corners on major glass containers.

### Shape Hierarchy
- **Primary Enclosures (Dashboard Panes & Hero Cards)**: Border radius of `24px` (`rounded-2xl` to `rounded-3xl`), evoking thick beveled glass tabletops.
- **Interactive Controls (Buttons, Inputs, Filter Pills, Status Badges)**: Fully pill-shaped with `9999px` (`rounded-full`).
- **Inner Data Cells & Grid Items**: Border radius of `16px` (`rounded-xl`) to establish a soft visual relationship within parent cards.

## Components

All components are rendered using formal academic Bahasa Indonesia.

### Buttons & Interactive Triggers
- **Tombol Utama (Primary Action)**: Pill-shaped (`rounded-full`), filled with Technical Cobalt (`#0051D5`), text in pure white (`#FFFFFF`) Inter Medium 14px. On hover: subtle scale transform (1.01) with a luminous cobalt outer glow (`0 8px 24px -4px rgba(0, 81, 213, 0.35)`).
- **Tombol Kaca (Glass Secondary)**: Pill-shaped, background `rgba(255, 255, 255, 0.8)`, border `1px solid rgba(226, 232, 240, 0.8)`, text in `#0F172A`. Hover transitions background to pure `#FFFFFF`.
- **Tombol Destruktif (Destructive / Batalkan)**: Translucent crimson tint `rgba(186, 26, 26, 0.08)`, border `1px solid rgba(186, 26, 26, 0.2)`, text in `#BA1A1A`.

### Search Bar (Bilah Pencarian Katalog Hukum)
- Full-width pill enclosure (`rounded-full`, height 52px) with `backdrop-filter: blur(20px)` and background `rgba(255, 255, 255, 0.85)`.
- Features an integrated quick-filter dropdown (*cth. Judul, Yurisprudensi, Pengarang, Putusan MA*) on the left edge, subtle search icon in `#64748B`, placeholder "Cari putusan perdata, jurnal hukum, atau nomor panggil...", and a keyboard shortcut tag (`⌘K`) on the right.

### Badges & Status Chips
- Pill-shaped (`rounded-full`), height 26px, padding 0 12px, font size 12px Inter Semibold.
- **Tersedia (Available)**: Background `rgba(16, 185, 129, 0.12)`, text `#059669`, with a 6px pulsing green indicator dot.
- **Dipinjam (Checked Out)**: Background `rgba(100, 116, 139, 0.12)`, text `#475569`.
- **Terlambat / Denda (Overdue)**: Background `rgba(186, 26, 26, 0.12)`, text `#BA1A1A`.
- **Reservasi Bilik (Reserved Study Room)**: Background `rgba(0, 81, 213, 0.1)`, text `#0051D5`.

### Law Archive Cards (Kartu Dokumen & Buku)
- Background `rgba(255, 255, 255, 0.75)`, padding 24px, border radius 24px, border `1px solid rgba(255, 255, 255, 0.7)`.
- Displays book title in Outfit Semibold 18px (`#0F172A`), author and edition in Inter 14px (`#475569`), call number badge (Nomor Panggil) styled like an archival spine label in a monospaced tabular pill, and quick reservation action pill.

### Cubicle Booking Grid (Reservasi Bilik Riset Hukum)
- Visual floor map card with interactive room slots representing private research pods (*Bilik Riset S3*, *Meja Baca Tenang*).
- Active/selected states illuminate with a frosted cobalt border and ambient interior blue tint (`rgba(0, 81, 213, 0.05)`).