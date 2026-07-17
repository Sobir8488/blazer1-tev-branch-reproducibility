# Final Zenodo upload checklist

The ZIP is technically complete. Confirm only the record-level identity fields before publication:

1. Creator names and order.
2. Affiliations and ORCID identifiers, where applicable.
3. Reserved version DOI inserted into the manuscript Data Availability statement.
4. Journal DOI added later with the relation `isSupplementTo`.
5. Uploaded filename and version both read `v1_1_0` / `1.1.0`.

The current creator metadata is `Turaev, S.` because no final manuscript author list was present in the supplied source. Replace it in `.zenodo.json`, `metadata/zenodo_deposit_metadata.json`, `CITATION.cff`, and `codemeta.json` only if the final creator list differs.
