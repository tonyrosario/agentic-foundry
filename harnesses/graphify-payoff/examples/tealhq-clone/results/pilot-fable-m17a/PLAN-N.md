# PLAN: M17a Contact detail and notes

Built from `9738747` (M16 ticked). Spec: `screens.contactDetail`, `contactFormDialog`;
flows doc section 3. Criteria M17a-AC1 to AC5 in `docs/build-plan.md`.

Shape: `/contact-tracker/:id` mirrors `JobDetailPage`. Left: collapsible list of all
contacts, current one marked. Centre: header (name, "job title at company", location,
Edit, Delete) and three collapsible sections (outreach, Dates, Contact Information).
Right: a panel that switches between Related Jobs and Notes. Related Jobs is M17b, so
M17a shows a placeholder there and logs it. Work Experience is `build: skip`.

## Files to create

All under `app/` unless noted.

| File | What |
| --- | --- |
| `src/people/ContactDetailPage.tsx` | The page: reads `useContacts()`, finds the contact by `:id`, shows `LoadingStatus` until loaded, not-found message with a link to `/contact-tracker` for an unknown id, otherwise the list pane, header, sections and right panel. Owns the list-open and panel-tab state as `JobDetailPage` does |
| `src/people/ContactDetailPage.module.css` | Page, detail column, list toggle, body row; same tokens as `JobDetailPage.module.css` |
| `src/people/ContactListPane.tsx` (+ `.module.css`) | Left `nav` "Contacts": every contact newest first by `added_at`, each a `NavLink` to `contactPath(id)` showing full name over "job title at company". Modelled on `JobListPane` without grouping |
| `src/people/ContactHeader.tsx` (+ `.module.css`) | Back link to the list, `h1` full name, "job title at company", location, `EditContactButton`, delete button |
| `src/people/EditContactButton.tsx` | Opens `ContactFormDialog` titled "Edit contact" prefilled from the contact's nine text fields; save calls `store.updateContact(id, values)`. Mirrors `EditJobButton` |
| `src/people/DeleteContactButton.tsx` | The header's Delete: `ConfirmDialog`, then `store.bulkDeleteContacts([id])` (M15 assumption: no single delete), then navigate to `/contact-tracker`. Thin wrapper over `DeleteContactsButton` if its label and copy fit; otherwise its own confirm |
| `src/people/OutreachSection.tsx` | Collapsible section headed by the goal's label (or "Outreach" when none) with three native selects: Relationship, Goal, Status (`next_step`); each has a blank "None" option so a choice can be cleared (M16 assumption deferred clearing to this page). Saves through `saves.save(...CHANGES.contactField(...), () => store.updateContact(...))` |
| `src/people/ContactDatesSection.tsx` | Collapsible "Dates": Saved (read only, `formatTimestampDay(added_at)`), Last contacted and Follow up as `DateCell`s saving `last_contacted_at` / `follow_up_at` |
| `src/people/ContactInfoSection.tsx` (+ `.module.css`) | Collapsible "Contact Information": email as `mailto:` link, LinkedIn and Twitter as links when they are web addresses, phone as text; empty fields say "Not set". Read only |
| `src/people/ContactSidePanel.tsx` | Right panel with a two-tab `tablist` "Contact panels": Related Jobs (placeholder until M17b) and Notes (`NotesEditor` on the contact's `note`) |
| `src/components/CollapsibleSection.tsx` (+ `.module.css`) | Extracted from `DatesSection`: `section` with an `h2` toggle button (`aria-expanded`, `aria-controls`, up/down `Icon`) and children when open. Used by the three contact sections and by `DatesSection` |
| `src/components/NotesEditor.tsx` (+ move `NotesPanel.module.css` styles) | The autosave textarea from `detail/NotesPanel.tsx` made generic: props `text`, `change` (`[key, label]`), `write(value: string \| null)`, `recordId`. Debounce, flush on blur/unmount, draft from `saves.draftOf`, last-write-wins status unchanged |
| `src/format/links.ts` | `isWebAddress(url)` moved out of `JobHeader` so the contact header and info section share it |
| `e2e/m17a-contact-detail.test.ts` | One test per criterion, titles start with `M17a-AC1` … `M17a-AC5`. Reuses the M16 helpers (`unreachable`, `problems`, `contactsFromServer`) copied locally |

## Existing files to change

| File | Change |
| --- | --- |
| `src/App.tsx` | Add `<Route path="contact-tracker/:id" element={<ContactDetailPage />} />` beside the job detail routes (outside `TrackersLayout`, as job detail is) |
| `src/detail/DatesSection.tsx` | Use `CollapsibleSection` instead of its inline heading/toggle; keep its `DateField` |
| `src/detail/DatesSection.module.css` | Drop the `.section`, `.heading`, `.toggle` rules that move to `CollapsibleSection.module.css` |
| `src/detail/NotesPanel.tsx` | Becomes a thin job wrapper over `NotesEditor` (`CHANGES.note(job)`, `store.updateJob(id, { note })`) |
| `src/detail/NotesPanel.module.css` | Styles move to `NotesEditor.module.css`; file removed |
| `src/detail/JobHeader.tsx` | Import `isWebAddress` from `src/format/links.ts` |
| `src/people/DeleteContactsButton.tsx` | Only if reused for the single delete: accept an optional `label`/`message` or keep as is and call with `ids=[id]` (decide at build; prefer reuse) |
| `src/data/scenarios/inFlightPeople.ts` | Only if a seed contact lacks a field the tests need (email, LinkedIn, Twitter, phone, last contacted). Check first; prefer existing values |
| `app/README.md` | Code map: `src/people/` now includes the detail page; `src/components/` adds `CollapsibleSection`, `NotesEditor`; `src/format/` adds links |
| `docs/build-plan.md` | Assumptions log lines (same commit as the code): Related Jobs panel is a placeholder until M17b; outreach selects are native selects with a "None" option to clear; detail Delete reuses the bulk delete with one id; empty contact info fields read "Not set". Progress tick in its own `docs:` commit at the end |
| `CONTEXT.md` | Only if a new term is introduced (none expected) |

## Existing modules to reuse

- `src/people/ContactFormDialog.tsx` with `initial` for Edit (AC1, AC2 contact info changes)
- `src/people/contactPaths.ts` (`contactPath`, `CONTACT_TRACKER_PATH`) for links and the back link
- `src/data/contactRules.ts` `fullName`
- `src/data/peopleOptions.ts` `CONTACT_GOALS`, `CONTACT_NEXT_STEPS`, `CONTACT_RELATIONSHIPS`
- `src/store/changes.ts` `CHANGES.contactField(contact, field, name)`: also keys the note as `contact:note:<id>`, so no new entry is needed
- `src/store/useContacts.ts`, `src/store/useStore.ts` (`store`, `saves`), `saves.draftOf` for kept drafts (AC4)
- `src/components/DateCell.tsx` for the two calendar fields (keyboard already covered, AC5)
- `src/components/ConfirmDialog.tsx`, `src/components/LoadingStatus.tsx`, `src/components/Icon.tsx`, `Button.module.css`, `VisuallyHidden.module.css`
- `src/components/SelectField.tsx` or a plain `<select>` with `FormField.module.css` for the outreach selects
- `src/format/display.ts` `formatTimestampDay`, `formatDay`
- `src/shell/ProblemBanner.tsx` already shows failed saves with retry (AC4 reporting)
- `src/detail/PlaceholderPanel.tsx` for the Related Jobs slot
- `e2e/support/test.ts` fixtures (`scenarios`, per-worker server)

## Callers the change affects

- `src/people/ContactCell.tsx`: the Full Name link already targets `contactPath(id)`; it starts resolving instead of hitting `NotFoundPage`. No code change
- `src/detail/SidePanelContent.tsx`: still renders `NotesPanel`; its props do not change
- `src/detail/JobDetailPage.tsx`: unchanged, but `DatesSection` and `NotesPanel` under it are refactored, so `npm run e2e -- -g "M6b|M7|M13-AC3"` must stay green
- `src/App.tsx` route order: `contact-tracker/:id` must not be shadowed by the `*` route or the tracker placeholders
- `e2e/m16-people-list.test.ts`: unaffected; the M16 assumption that the name link is "not found until M17a" is superseded, and the matching log line gets a note
- `e2e/m2-shell.test.ts`, `m7-detail-panels.test.ts`: no People or Contacts placeholder entries are touched (the Contacts tab placeholder is M17b's)

## Order of work

1. Tests first: write `e2e/m17a-contact-detail.test.ts`, run, see AC1 fail on not-found.
2. Route + `ContactDetailPage` + `ContactListPane` + `ContactHeader` + Edit + Delete (AC1).
3. Extract `CollapsibleSection`; outreach, dates and contact info sections (AC2).
4. Extract `NotesEditor`; `ContactSidePanel` with Notes and the Related Jobs placeholder (AC3).
5. Failure and keyboard tests (AC4, AC5); fix as needed.
6. README code map, assumptions log; `npm run check`, `npm run e2e`, `npm run build`; commits per concern; tick M17a; push.
