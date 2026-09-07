---
name: Liquid Glass Premium Library
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#45464d'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#0051d5'
  on-secondary: '#ffffff'
  secondary-container: '#316bf3'
  on-secondary-container: '#fefcff'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#001c39'
  on-tertiary-container: '#3c86d9'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#dbe1ff'
  secondary-fixed-dim: '#b4c5ff'
  on-secondary-fixed: '#00174b'
  on-secondary-fixed-variant: '#003ea8'
  tertiary-fixed: '#d4e3ff'
  tertiary-fixed-dim: '#a4c9ff'
  on-tertiary-fixed: '#001c39'
  on-tertiary-fixed-variant: '#004883'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  display-lg:
    fontFamily: Poppins
    fontSize: 64px
    fontWeight: '700'
    lineHeight: 72px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Poppins
    fontSize: 48px
    fontWeight: '600'
    lineHeight: 56px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Poppins
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-md:
    fontFamily: Poppins
    fontSize: 32px
    fontWeight: '500'
    lineHeight: 40px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.05em
  caption:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 48px
  xl: 80px
  container-max: 1440px
  gutter: 24px
---

## Brand & Style
The design system embodies a "Liquid Glass" aesthetic tailored for a high-end academic environment. It balances the prestige of a traditional university with the cutting-edge feel of spatial computing. The brand personality is intellectual, serene, and forward-looking, aiming to evoke a sense of limitless knowledge and immersive focus.

The visual style is a hybrid of **Glassmorphism** and **Minimalism**. It utilizes high-translucency layers, expansive white space, and vibrant background blurs to create a sense of depth and lightness. Components appear as physical objects floating in a luminous, atmospheric space, heavily inspired by modern operating systems that prioritize clarity and depth.

## Colors
The palette is rooted in deep academic Navy (#0F172A) for authority and contrast, supported by a range of technical blues that provide energy and focus. The background is not a flat white but a "soft white" gradient with subtle shifts toward light blue, creating a canvas that feels alive and responsive to light.

Glass surfaces use a specific alpha-weighted white to maintain legibility against the dynamic background. The primary color is reserved for high-level branding and primary actions, while the lighter blues are used for interactive highlights and status indicators.

## Typography
The system employs a dual-typeface strategy. **Poppins** provides an editorial, sophisticated flair for headlines, using geometric shapes to convey modern luxury. For body text and functional UI elements, **Inter** is used for its exceptional readability and systematic feel.

Display styles should be used sparingly for hero sections or library categories to maintain an "editorial" feel. Labels use a slightly increased letter spacing and uppercase styling to provide a clear hierarchy against high-detail glass surfaces.

## Layout & Spacing
This design system utilizes a **fluid grid** with generous safe areas to emphasize the "floating" nature of the glass components. 

- **Desktop:** 12-column grid, 24px gutters, and 80px side margins. 
- **Tablet:** 8-column grid, 24px gutters, 40px side margins.
- **Mobile:** 4-column grid, 16px gutters, 20px side margins.

Spacings are strictly based on an 8px scale. High-level sections should favor the `xl` (80px) spacing to ensure the UI feels expansive and premium. Components should use `md` (24px) internal padding to maintain the "breathable" luxury aesthetic.

## Elevation & Depth
Depth is the core of this system. It is achieved through a combination of backdrop blurs and multi-layered shadows:

1.  **The Base Layer:** The soft white gradient background.
2.  **The Glass Layer:** Surfaces with `backdrop-filter: blur(24px)` and a subtle `1px` solid border (`rgba(255,255,255,0.25)`). This simulates the edge of a glass pane.
3.  **Soft Lighting:** Every glass panel has a very soft, high-spread shadow with low opacity (`rgba(15, 23, 42, 0.08)`) to lift it off the background.
4.  **Floating Elements:** Interactive elements like buttons use a "hover-lift" effect, increasing the shadow spread and slightly scaling the component (1.02x) to simulate physical movement toward the user.

## Shapes
Shapes are highly organic and soft. The standard corner radius for cards and major containers is `24px` to `32px`. Interactive elements like buttons and chips must always be **pill-shaped** (fully rounded) to contrast against the structured content of the library. This extreme roundedness reinforces the "Liquid" aspect of the design, making the UI feel safe, modern, and tactile.

## Components

- **Buttons:** Primary buttons are pill-shaped with a solid Navy or Blue fill. Secondary buttons use the Glass style (translucent white with blur) and a subtle border.
- **Search Bar:** A large, floating glass element with 32px rounded corners. Include a subtle inner glow to make the input area feel recessed into the glass.
- **Cards:** Used for book covers and research papers. They feature the 24px glass style with a "frosted" footer for metadata. On hover, the glass should become slightly more opaque.
- **Chips / Tags:** Small pill-shaped elements used for categories. They use a secondary blue tint with 10% opacity and no blur to remain legible at small sizes.
- **Navigation:** A floating bottom-dock or a slim top-bar, always using the 24px blur glass effect. Icons should be thin-stroke (2px) to match the Inter typography.
- **Modals:** Centered floating glass panes with a heavy backdrop blur (40px) on the content behind them to ensure absolute focus.