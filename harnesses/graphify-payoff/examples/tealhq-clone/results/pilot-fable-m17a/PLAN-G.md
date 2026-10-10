# M17a plan: Contact detail and notes

Built from `9738747` (clean tree apart from the untracked `.graph-build.log`). Criteria
M17a-AC1 to AC5 in `docs/build-plan.md`; spec `screens.contactDetail` and
`contactFormDialog` in `specs/people-companies.json`; flows doc section 3.

Scope decisions (each gets an assumptions-log line in the same commit as the code):

- The right panel switches between Related Jobs and Notes. In M17a Related Jobs is the
  existing `PlaceholderPanel`; M17b fills it. Notes is the autosaving area (AC3, AC4).
- The outreach selects reuse the M16 `ChoiceCell` (button that opens a choose-one
  menu) rather than a native `<select>`, so list and detail behave the same. The detail
  adds a "None" entry so a choice can be cleared, which M16 left to this page.
- Work Experience is skipped (`build: skip`); no section is rendered.
- Delete on the detail sends `bulkDeleteContacts([id])` (M15 assumption), then goes
  back to `/contact-tracker`.
- The left list is all contacts newest first by `added_at`, as the job list pane is;
  the gaps list says collapsing it was not captured, so it gets the same "Contact list"
  toggle as the job detail.
- No contract, server, migration, scenario or mock change: `updateContact`,
  `bulkDeleteContacts` and the contact fields already exist.

## Files to create

| Path | What |
| --- | --- |
| `app/src/people/ContactDetailPage.tsx` | Route element for `/contact-tracker/:id`. Loads contacts with `useContacts`, finds the contact, renders the list pane toggle, header, sections and the right panel; not-found message with a link to the list when the id is unknown. Mirrors `JobDetailPage` without scope, stepper, guidance or tabs row. |
| `app/src/people/ContactDetailPage.module.css` | Page grid only if `JobDetailPage.module.css` cannot be imported as is (it holds `page`, `detail`, `listToggle`, `body`, `title`, `note`); prefer importing that module and skipping this file. |
| `app/src/people/ContactHeader.tsx` | Back link to the list, `h1` full name, "job title at company", location, `EditContactButton`, `DeleteContactsButton` with one id. Styles from `detail/JobHeader.module.css`. |
| `app/src/people/EditContactButton.tsx` | Opens `ContactFormDialog` titled "Edit contact", prefilled from the contact's nine text fields, saves with `store.updateContact`. Mirrors `detail/EditJobButton.tsx`. |
| `app/src/people/OutreachSection.tsx` | Collapsible section headed by the goal's label or "Outreach"; Relationship, Goal and Status `ChoiceCell`s with a clear entry; saves through `saves.save(...CHANGES.contactField(...), () => store.updateContact(...))` as `ContactCell` does. |
| `app/src/people/ContactDatesSection.tsx` | Collapsible "Dates": Date Saved read only (`formatTimestampDay`), Last contacted and Follow up as `DateCell`s. Reuses the section and field pieces extracted from `DatesSection` (below). |
| `app/src/people/ContactInfoSection.tsx` | Collapsible "Contact Information": email as `mailto:` link, LinkedIn and Twitter as links (only web addresses, opening in a new tab with the hidden hint as `JobHeader` does), phone as text; empty fields shown as "Not set". |
| `app/src/people/ContactSidePanel.tsx` | The right panel: a two-tab switch (Related Jobs, Notes) over `SidePanel`; Related Jobs shows `PlaceholderPanel`, Notes shows the shared notes panel bound to the contact. |
| `app/src/people/contactDetailTabs.ts` | The two side tab keys and labels, if the switch is not small enough to live in `ContactSidePanel.tsx`. |
| `app/src/detail/DetailListPane.tsx` | Generic left list: `{ id, to, primary, secondary }[]` links under a `nav` with an accessible name, optional groups. Extracted from `JobListPane`, which becomes a thin wrapper. Styles stay in `JobListPane.module.css`. |
| `app/src/detail/CollapsibleSection.tsx` | The `h2` toggle with `aria-expanded`/`aria-controls` and the `Icon` up/down, extracted from `DatesSection`; used by the three contact sections and by `DatesSection`. Styles from `DatesSection.module.css`. |
| `app/src/detail/DateField.tsx` | The `dt`/`dd` + `DateCell` row currently private in `DatesSection.tsx`, exported so the contact dates reuse it. |
| `app/src/format/webAddress.ts` | `isWebAddress(url)`, moved out of `JobHeader.tsx` so the contact links share it. |
| `app/e2e/m17a-contact-detail.test.ts` | One test per criterion, titles starting `M17a-AC1` … `M17a-AC5`; failure tests use the `page.route` refuse, drop-response and delay helpers as `m16-people-list.test.ts` and `m13-failures.test.ts` do; the slow-earlier-save test mirrors the M13 note test. |
| `app/src/people/outreachHeading.test.ts` | Only if the heading rule is pulled into a pure function; otherwise no new unit test. |

## Existing files to change

| Path | Change |
| --- | --- |
| `app/src/App.tsx` | Add `<Route path="contact-tracker/:id" element={<ContactDetailPage />} />` beside the job detail routes, outside `TrackersLayout`. |
| `app/src/detail/NotesPanel.tsx` | Make it record-agnostic: props become `{ change: [key, label], note: string \| null, recordId, save: (text: string \| null) => Promise<unknown> }` (or a `JobNotesPanel` wrapper keeps the current props). The debounce, flush-on-unmount, `draftOf` draft restore and the stale-write guard stay as they are. |
| `app/src/detail/SidePanelContent.tsx` | Pass the job-bound props to the changed `NotesPanel`. |
| `app/src/detail/DatesSection.tsx` | Use `CollapsibleSection` and the exported `DateField`; behaviour unchanged. |
| `app/src/detail/JobListPane.tsx` | Delegate to `DetailListPane`; keep its props so `JobDetailPage` is untouched. |
| `app/src/detail/JobHeader.tsx` | Import `isWebAddress` from `format/webAddress.ts` instead of its private copy. |
| `app/src/components/ChoiceCell.tsx` | Optional `clearLabel` prop adding a "None" entry, with `onChange(value: K \| null)` when set; existing callers unchanged when the prop is absent. |
| `app/src/people/DeleteContactsButton.tsx` | No code change expected; `onDone` on the detail navigates to the list. If its "N selected" wording leaks into the dialog title ("Delete 1 contact?") that is acceptable. |
| `app/README.md` | Code map: `src/people/` gains the contact detail page and its sections; `src/detail/` notes the shared `DetailListPane`, `CollapsibleSection`, `DateField`; `src/format/` gains `webAddress.ts`. |
| `docs/build-plan.md` | Assumptions log lines for the decisions above (same commits as the code); tick M17a in Progress in its own `docs:` commit after review. |
| `CONTEXT.md` | Only if a term is added; none expected. |

## Existing modules to reuse (no second version)

- `components/DateCell`, `components/ChoiceCell` (+ `Menu`), `components/ConfirmDialog`,
  `components/FormDialog` via `people/ContactFormDialog` (edit mode = `initial`),
  `components/LoadingStatus`, `components/Icon`, `components/VisuallyHidden.module.css`,
  `components/Button.module.css`.
- `detail/SidePanel`, `detail/PlaceholderPanel`, `detail/NotesPanel` (generalised),
  `detail/JobListPane` → `DetailListPane`, `detail/DatesSection` pieces, the detail
  CSS modules (`JobDetailPage`, `JobHeader`, `JobListPane`, `DatesSection`, `NotesPanel`,
  `SidePanel`).
- `store/useContacts`, `store/useStore` (`store`, `saves`), `store/changes`
  (`CHANGES.contactField(contact, 'note', 'Note')` keys the note save as
  `contact:note:<id>`; no new entry needed), `saveRegistry.draftOf` for the kept draft.
- `data/contactRules.fullName`, `data/peopleOptions` (`CONTACT_GOALS`,
  `CONTACT_NEXT_STEPS`, `CONTACT_RELATIONSHIPS`), `format/display.formatTimestampDay`,
  `people/contactPaths` (`CONTACT_TRACKER_PATH`, `contactPath`), `pages/NotFoundPage`
  pattern (inline not-found as `JobDetailPage` does, not the page component).
- E2E: `e2e/support/test` fixtures (`scenarios`, per-worker server), seed ids such as
  `seed-contact-06`, the `/api/contacts` read-back used by M16.

## Callers the change affects

| Changed module | Callers to re-check |
| --- | --- |
| `NotesPanel` props | `detail/SidePanelContent.tsx` (only caller). M7-AC3 and M13-AC3 note tests must stay green. |
| `JobListPane` → `DetailListPane` | `detail/JobDetailPage.tsx` (only caller). M6a-AC2 list tests. |
| `DatesSection` → `CollapsibleSection` + `DateField` | `detail/JobDetailPage.tsx`. M6b dates tests. |
| `JobHeader` / `isWebAddress` | `detail/JobDetailPage.tsx`. M6a-AC1 URL test. |
| `ChoiceCell` optional clear | `people/ContactCell.tsx` (unchanged behaviour without the prop). M16-AC3, AC8. |
| `DeleteContactsButton` | `people/ContactToolbar.tsx` (unchanged) and the new header. M16-AC6. |
| `App.tsx` route | `people/ContactCell.tsx` already links to `contactPath(id)`; M16's "not found until M17a" assumption line becomes history. `pages/NotFoundPage` no longer catches `/contact-tracker/<id>`. |
| `ContactFormDialog` edit mode | `people/AddContactButton.tsx` unchanged; `initial` prop already exists. |

## Order of work

1. Test first: `m17a-contact-detail.test.ts` with AC1 (route, list, header, edit, delete,
   not found); watch it fail on the current not-found page. Then the route, page, pane
   extraction, header, edit and delete. Commit.
2. AC2: `CollapsibleSection` and `DateField` extraction, `ChoiceCell` clear entry,
   outreach, dates and contact-info sections. Commit.
3. AC3 and AC4: generalise `NotesPanel`, the side panel switch, the failure tests
   (refused select, date and note; draft kept across leaving; slow earlier note save).
   Commit.
4. AC5 keyboard tests; fixes if any. README code map and assumptions lines ride with the
   commits they belong to.
5. `npm run check`, `npm run e2e`, `npm run contract`, `npm run build`; graph refresh with
   `graphify update app` from the repo root; review; tick M17a; push.
