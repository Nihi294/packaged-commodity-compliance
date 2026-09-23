# SahiPack — Landing Page Prototype

AI-assisted Legal Metrology compliance inspection platform. This is a
frontend-only prototype: no backend, OCR pipeline, database, or auth — just
a polished landing page with realistic mock data and interactions.

## Stack
React + Vite + Tailwind CSS + React Router + Lucide icons.

## Run it

```bash
npm install
npm run dev
```

Then open the printed local URL (usually http://localhost:5173).

To build for production:

```bash
npm run build
```

## Structure

```
src/
  components/   Navbar, Hero, Problem, Workflow, Capabilities,
                InspectionPreview, TrustSection, CTA, Footer
  pages/        Home.jsx, Inspection.jsx (mock /inspection flow)
  App.jsx       Route definitions
  main.jsx      Entry point
```

## Notes
- "Start an inspection" buttons route to `/inspection`, a simulated
  upload → scan → result flow using sample data (frame_0184.jpg / SC-2291).
- All product imagery is hand-built SVG/CSS — no external stock images.
- Respects `prefers-reduced-motion`.
