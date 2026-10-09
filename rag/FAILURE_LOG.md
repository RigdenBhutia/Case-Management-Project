# RAG Failure Log

## 1. Photoshop not linked to Adobe Creative Cloud
- **Stage:** Generation (model reasoning)
- **Symptom:** "Can I install Photoshop?" was refused, although the policy lists Adobe Creative Cloud.
- **Root cause:** llama3.2 treated Photoshop and Adobe Creative Cloud as unrelated. Loosening the prompt wording did not change this.
- **Fix:** Made the source policy explicit ("Adobe Creative Cloud (including Photoshop, Illustrator, and Premiere Pro)"). The top retrieval score also rose from 0.435 to 0.539.
- **Residual limitation:** Any relationship left implicit in a future document is likely to fail the same way.

## 2. Fixed-size chunking mixed topics
- **Stage:** Chunking
- **Symptom:** Top-1 retrieval accuracy was 11/12 for fixed-size chunks vs 12/12 for paragraph chunks.
- **Likely cause:** 30-word windows cross paragraph boundaries, blurring chunk meaning. (Not confirmed by inspecting the matched chunk.)
- **Fix:** Paragraph chunking selected.
- **Residual limitation:** Window size and overlap (30/10) were not tuned. Paragraph chunking suits these short, one-idea paragraphs and may not suit long documents.

## 3. Out-of-scope question passes the score cutoff
- **Stage:** Retrieval
- **Symptom:** "How much does a replacement laptop cost?" scored 0.428, inside the range of valid questions.
- **Root cause:** Similarity measures topic closeness, not whether the document answers the question.
- **Fix:** Second layer. The prompt instructs the model to refuse when the passages don't answer. The end-to-end run refused this question.
- **Residual limitation:** Relies on model behaviour. Only one near-miss question passed the cutoff, so the sample is small.

## 4. Valid question refused inconsistently
- **Stage:** Generation
- **Symptom:** "My laptop won't turn on..." was refused once, then answered correctly in 3 of 3 reruns.
- **Root cause:** Sampling randomness in the model.
- **Fix:** Temperature 0 and a fixed seed.
- **Residual limitation:** This gives consistency, not correctness. Results are specific to llama3.2.

## 5. Similarity threshold was a guess
- **Stage:** Retrieval
- **Fix:** Threshold sweep on the evaluation set chose 0.35. The threshold is applied to the best chunk only, and the top 2 chunks are kept as context if it passes.
- **Residual limitation:** Tuned and measured on the same 17 questions. Needs held-out questions.

## Open issues (not yet fixed)
- The Photoshop answer cited the vendor-list rule but omitted the manager-approval rule from the second chunk.
- The `sources` field in the API response can include chunks the answer did not cite.