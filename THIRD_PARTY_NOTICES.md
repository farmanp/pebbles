# Third-party materials

Cookie Cats comparison provenance is recorded in
`public_comparisons/cookie_cats/provenance.json`, including pinned source URLs,
commit and SHA-256 fingerprints. The mirror has no repository license; upstream
dataset terms have not been independently established. Downloaded data,
notebooks and derived per-user packets are excluded from this repository.

`python3 scripts/setup_fixtures.py --with-public-data` retrieves the named public
files for local comparison/testing and refuses changed fingerprints. It does not
execute the analyst notebook, grant redistribution rights, or establish the
original company's experiment plan. Review upstream terms before other uses.

GitHub Actions are referenced by immutable commits and retain their upstream
licenses. The Pebbles runtime uses the Python standard library and local browser
JavaScript; it does not bundle external frontend libraries or fonts.
