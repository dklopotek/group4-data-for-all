# Heilmeier Catechism

## Q1: What are you trying to do, in plain words, no jargon?

We are making a map that tells Barcelona's urban planning agency which 400m × 400m zones in the city need green-infrastructure investment most urgently. The map scores each zone on four things planners can actually fix: too much pavement, too much heat, not enough tree cover, and tree species that cannot connect with the right soil fungi. Each zone gets a recommendation — "de-pave here," "plant here," "change species here," or "do all three" — tied to a real municipal budget line.

## Q2: How is it done today, and what are the limits of current practice?

Today, Barcelona allocates green-infrastructure capital through the Superilla and Eixos Verds programmes using general planning criteria — street width, traffic volume, public demand, political priority. There is no spatially explicit, data-driven tool that scores zones on the *combination* of barriers relevant to belowground ecological function. Soil fungi are invisible to current planning. The limit: capital may go to zones that are politically visible but ecologically low-leverage, or to interventions that address one barrier (e.g., planting trees) while ignoring co-requisites (those trees need unpaved soil and fungal partners to support belowground recovery).

## Q3: What is new in your approach and why do you think it will be successful?

Two things. First, we combine four barrier layers (sealed surface, heat, canopy, host-fungus mismatch) into a single priority score — none of the existing planning tools do this. Second, we anchor every intervention recommendation to a documented Ajuntament budget line, so the output is directly actionable within existing institutional processes. It will succeed because it uses only data that already exists and is maintained (satellite imagery, municipal tree inventory, published fungal trait databases), makes only claims the data can support (barrier concentration, not network state), and plugs into a decision cycle that already exists.

## Q4: Who cares — what difference will it make?

Barcelona Regional's analysts and Ajuntament Espais Verds i Biodiversitat staff care, because they are the ones writing the annual capital allocation recommendations. If the map works, it means the next round of Superilla de-paving or Eixos Verds planting is routed to the zones where the data says it will matter most for belowground ecological function — not just where it is most visible. For Barcelona residents, the difference is that public money spent on green infrastructure delivers more ecological return per euro.

## Q5: What are the risks?

1. **AM-blindness confound**: Arbuscular mycorrhizal fungi (partners of most BCN street trees) are invisible to citizen science. The host-mycorrhizal mismatch sub-score is structurally suppressed for AM-dominant zones. Mitigation: flag categorically, do not fake a quantitative score.
2. **Intervention heuristic is simple**: The intervention-type recommendation uses "highest sub-score → intervention type," which is defensible but not optimal. Mitigation: document as a heuristic, not an optimizer.
3. **No ground-truth validation**: We cannot verify that barrier reduction actually produces mycorrhizal recovery. Mitigation: we explicitly do not claim this.
4. **Peri-urban reference patch is N=1**: The Collserola reference patch is used qualitatively, not statistically. Mitigation: document as methodological anchor only.
5. **Data staleness**: Tree inventory is snapshot-based; satellite data has cloud gaps. Mitigation: document vintage in all outputs.

## Q6: How much will it cost?

Zero euros in direct data or software cost. All inputs are open data (Copernicus, Landsat, GBIF, Open Data BCN). All tools are open-source (Python, GeoPandas, rasterio, networkx). Personnel cost is the team's seminar time (~4 weeks, 3-4 people, part-time).

## Q7: How long will it take?

Four weeks (one seminar session remaining after Session 2). Session 3: data preparation retrofitting + personal data layers. Session 4: modeling, evaluation, and final output packaging.

## Q8: What are the mid-term and final exams for success?

**Mid-term exam (Session 3 end):** All five pipeline notebooks retrofitted with CRISP-DM process documentation (before/after row counts, design decision cells, bounds assertions). Validation notebook passing all range checks.

**Final exam (Session 4 end):** A ranked GeoJSON of ≤15 priority zones, each with four sub-scores, an intervention-type recommendation, and a budget-line reference. Reproducible from a clean clone. Accompanied by a product card that explicitly states what the map cannot claim.
