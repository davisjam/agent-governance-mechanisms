# Vendored third-party assets

## `paged.polyfill.js`

- **Source:** <https://unpkg.com/pagedjs/dist/paged.polyfill.js>
- **Version:** Paged.js v0.4.3 (MIT license)
- **Role:** Browser JavaScript for the PDF print build only. When the combined
  print HTML (`book/_print/print.html`, gitignored) is loaded in headless
  Chrome, this polyfill paginates the single-column HTML into 6×9in book pages,
  applying the `@page` rules (running heads, folios, TOC page numbers via
  `target-counter`). It runs in the browser during the PDF render; the Python
  build (`build_book_html.py`) stays stdlib-only — this is a static asset.
- **Regenerate the PDF:** `python3 book/build_book_html.py --pdf` emits the
  combined print HTML, then renders it to `book/mage-book.pdf` via headless
  Chrome. See that flag's implementation for the exact Chrome invocation.
