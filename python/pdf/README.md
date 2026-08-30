# Accessibility Limitations (PDF/UA)

The current PDF generator does not produce an accessible document. Because it relies on an older version of the rendering engine (`WeasyPrint` 61) that lacks native tagged‑PDF support, screen readers, and other assistive technologies cannot reliably navigate or interpret the brief's content.

At the moment there is:

- No logical document structure as headings, sections, and reading order are not programmatically defined. Users who rely on screen readers cannot jump between sections or understand the hierarchy of information.

- There is missing alternative text for visuals where the status banner, color‑coded equity indicators, and any charts or graphics that might be added in the future do not have text equivalents. A user who cannot see the banner color would not know whether the equity check passed or requires review.

- While tables contain important data, their rows and columns are not linked in a way that screen readers can interpret. Users cannot reliably match a tract’s predicted filings to its neighborhood or action tier.

- Color is used as the sole communication method, for example, the banner’s background color (blue vs. yellow) is the only indicator of equity status. No accompanying text or icon provides the same information for users who are color-blind or visually impaired.

- Custom fonts may render inconsistently because the brief uses specific typefaces that may not be fully embedded. In some cases, this could cause characters to be omitted or replaced, making the text unreadable by assistive tools.

- Incompatible with current accessibility standards because the engine does not support PDF/UA‑1 (ISO 14289‑1) tagging, even basic compliance features like metadata language, title, and tag tree are unavailable without post‑processing.

## Note

I was aware of `fpdf2` having PDF/UA support for structural tagging, but it would require every tag through Python calls to create a template of procedural code, which is not a feasible even from the onset since there are more metadata flags needed beyond even the library’s current capabilities. The brief’s content is dynamic and generated from a template, so a static procedural approach would not scale.
