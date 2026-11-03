# Frontend Design System & UI Specification — CloudAttend

## 1. Design Direction
CloudAttend is styled as an academic administration platform: calm, trustworthy, readable, and task-focused.
- **Clarity over Clutter**: Avoid unnecessary decorative flourishes. Maintain high information density without visual noise.
- **Task-Centric Speed**: Faculty must be able to record an entire class's attendance in seconds with minimal clicks.
- **Immediate Understanding**: Students should grasp their attendance standing (percentage and status) at a glance.

---

## 2. Color Palette & Design Tokens

| Token | Hex Value | Semantic Role & UI Application |
| :--- | :--- | :--- |
| **Primary Navy** | `#17365D` | Main navigation bar, primary brand headers, key CTA buttons. |
| **Primary Blue** | `#2874C8` | Active navigation links, interactive states, secondary emphasis buttons. |
| **Accent Teal** | `#159A9C` | Chart visualizations, KPI accents, positive informational highlights. |
| **Page Background** | `#F5F7FA` | Overall viewport background, subtle contrast against white cards. |
| **Surface / Card** | `#FFFFFF` | Background for content cards, data tables, modal dialogs, and forms. |
| **Primary Text** | `#202A35` | High-contrast body text, headings, and primary table data. |
| **Muted Text** | `#667085` | Field helper text, table column headers, timestamps, secondary labels. |
| **Border** | `#D9E0E8` | Table row dividers, input field borders, card outline borders. |
| **Success** | `#198754` | "Present" status pill, saved flash alerts, positive indicators. |
| **Warning** | `#D98E04` | Attendance warning thresholds (< 75%), cautionary alerts. |
| **Error** | `#C0392B` | "Absent" status pill, form validation errors, system failure alerts. |

> **Contrast Rule**: Never rely solely on color to communicate status. Always pair status colors with clear text labels or descriptive icons.

---

## 3. Typography

- **Font Family**: System UI stack: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif` (or `Aptos Display` if available).

| Element | Size | Weight | Line Height | Guidance |
| :--- | :--- | :--- | :--- | :--- |
| **Page Title** | 24–32 px | 700 (Bold) | 1.2 | Used once at the top of each view. Sentence case. |
| **Section Headings**| 18–22 px | 600 (Semibold) | 1.3 | Card and panel headings. |
| **Body Text** | 14–16 px | 400 (Regular) | 1.5 | General content, table cell data, descriptions. |
| **Input Labels** | 12–14 px | 500 (Medium) | 1.4 | Positioned directly above form inputs. |
| **Buttons** | 14–16 px | 600 (Semibold) | 1.2 | Concise action verbs ("Save Attendance", "Add Student"). |
| **Table Headers** | 12–14 px | 600 (Semibold) | 1.4 | Uppercase or clear sentence case with sort indicators. |

---

## 4. Spacing, Grid & Layout Rhythm

- **Base Rhythm**: 8 px grid increments (`8px`, `16px`, `24px`, `32px`, `48px`).
- **Container Sizing**: Max desktop width `1200px`, centered with fluid side gutters (`padding: 0 1.5rem`).
- **Responsive Breakpoints**:
  - Desktop: 12-column grid layout.
  - Tablet (768px – 991px): 6 to 8-column layout with stacked navigation options.
  - Mobile (< 768px): Single-column cards, full-width inputs, and horizontally scrollable tables.
- **Card Geometry**:
  - Padding: `20px` to `24px` internal padding.
  - Border Radius: `8px` to `10px`.
  - Border: `1px solid #D9E0E8`.
  - Shadows: Subtle elevation (`box-shadow: 0 1px 3px rgba(0,0,0,0.06)`).

---

## 5. UI Component Specifications

### Buttons
- **Primary Button (`.btn-primary-navy`)**: Solid `#17365D`, white text, 8px radius, height 40–44px. Hover state deepens to `#0f243f`.
- **Secondary Button (`.btn-outline-secondary`)**: White surface with `#D9E0E8` border and `#202A35` text.
- **Danger Button (`.btn-danger`)**: Solid `#C0392B`, white text. Used only for destructive actions (e.g. deleting records).

### Form Controls
- **Height**: Minimum 40–44px to provide comfortable touch targets on mobile devices.
- **Borders**: `1px solid #D9E0E8`. On focus, transition to `border-color: #2874C8` with a soft focus ring (`box-shadow: 0 0 0 3px rgba(40, 116, 200, 0.2)`).
- **Labels**: Every input element must have an explicitly linked `<label for="...">`.

### Attendance Status Badges
- **Present**: Green badge with `#198754` background (or light green `#e8f5e9` with dark green text `#198754`).
- **Absent**: Red badge with `#C0392B` background (or light red `#ffebee` with dark red text `#C0392B`).

### Data Tables
- Header row with `#F5F7FA` background and bold `#202A35` text.
- Subtle horizontal row dividers (`1px solid #E9ECEF`).
- Row hover effect (`background-color: #F8F9FA`).
- Wrapped in an `overflow-x: auto` container to prevent mobile viewport distortion.

### Analytics & Chart Containers
- White background card with descriptive title, KPI cards above, and interactive Chart.js canvas.
- Fallback data table rendered directly below or toggled for screen readers and accessibility.

---

## 6. Standardized UI Messages & Empty States

| Context | Standard Message |
| :--- | :--- |
| **No Students** | *"No students have been added yet."* |
| **No Courses** | *"No courses are available."* |
| **No Attendance** | *"No attendance records found for this selection."* |
| **Save Success** | *"Attendance recorded successfully."* |
| **Save Failure** | *"Unable to save attendance. Please verify your inputs and try again."* |
| **Unauthorized** | *"You do not have permission to access this page."* |
| **System Error** | *"CloudAttend is temporarily unavailable. Please try again shortly."* |

---

## 7. Accessibility Checklist (WCAG 2.1 AA)
- [x] Minimum 4.5:1 color contrast ratio for all normal body text.
- [x] Visible keyboard focus indicator on all interactive inputs, buttons, and links.
- [x] All forms have programmatic labels and ARIA descriptive hints for validation errors.
- [x] Tabular data uses proper `<th>` scoping (`scope="col"`).
- [x] Charts have accessible text summaries or tabular mirrors.

