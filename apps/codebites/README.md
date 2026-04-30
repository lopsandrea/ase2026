# CodeBites

> CRUD recipe platform with drag-and-drop image uploads.
> One of the four open-sourced internal Wideverse applications used as
> evaluation subjects in the Doc2Test paper (ASE'26 Industry Showcase).

- **Stack:** React 18 + Vite, in-memory store via `localStorage`.
- **Workflow archetype:** Form CRUD (`Form CRUD` row in Tab. 1).
- **Views:** ~15 (list, detail, new, edit, account, login, register, …).
- **License:** MIT (see [LICENSE](LICENSE)).

## Run locally

```bash
npm install
npm run dev          # http://localhost:3000
```

## Build & containerise

```bash
docker build -t codebites .
docker run -p 3000:3000 codebites
```
