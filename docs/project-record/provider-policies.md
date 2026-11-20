# Third-Party Model Provider Privacy & Security Policies

**Status**: **NOT VERIFIED**  
**Notice to Client**: StitchLab AI does not accept terms of service, data processing agreements, or commercial terms on behalf of clients. When connecting external paid model providers, the client must directly review, execute, and accept terms with each provider under their own commercial account.

---

## 1. OpenAI (API Services)

- **Provider**: OpenAI, LLC / OpenAI Ireland Ltd.
- **Verification Status**: **NOT VERIFIED**
- **Client Action Required**: Review and execute OpenAI Business Terms & Data Processing Addendum (DPA).
- **Default Policy Highlights (subject to client contract)**:
  - *Data Training*: Under OpenAI's business API policy, API customer data is reportedly not used to train models by default.
  - *Data Retention*: 30-day retention for abuse monitoring unless Zero Data Retention (ZDR) is requested and approved.
  - *Endpoint Jurisdiction*: Predominantly US-based endpoints unless EU residency addendum is in place.
- **Legal Link**: [https://openai.com/policies/business-terms](https://openai.com/policies/business-terms)

---

## 2. Anthropic (Claude API)

- **Provider**: Anthropic, PBC
- **Verification Status**: **NOT VERIFIED**
- **Client Action Required**: Review and execute Anthropic Commercial Terms of Service.
- **Default Policy Highlights (subject to client contract)**:
  - *Data Training*: Commercial API inputs/outputs are reportedly not used to train generative models.
  - *Data Retention*: Standard retention for trust and safety reviews.
  - *Security Measures*: SOC 2 Type II compliance reported.
- **Legal Link**: [https://www.anthropic.com/legal/commercial-terms](https://www.anthropic.com/legal/commercial-terms)

---

## 3. Google Cloud Vertex AI / Gemini API

- **Provider**: Google LLC
- **Verification Status**: **NOT VERIFIED**
- **Client Action Required**: Review and execute Google Cloud Terms of Service and Cloud Data Processing Addendum (CDPA).
- **Default Policy Highlights (subject to client contract)**:
  - *Data Training*: Customer data on Vertex AI is not used to train Google foundation models without explicit opt-in.
  - *Data Residency*: Region-specific deployment options available (e.g. EU regions, US regions).
  - *Compliance*: ISO/IEC 27001, SOC 1/2/3, HIPAA compliance capabilities available.
- **Legal Link**: [https://cloud.google.com/terms](https://cloud.google.com/terms)

---

## Summary Policy Table

| Provider | Model Adapter | Verification Status | Client Action Required | Training on API Data (Claimed) |
|---|---|---|---|---|
| OpenAI | `openai` | **NOT VERIFIED** | Direct Client Account & DPA | Opt-out / Off by default for API |
| Anthropic | `anthropic` (future) | **NOT VERIFIED** | Direct Client Account & Terms | Off by default for Commercial API |
| Google Cloud | `gemini` (future) | **NOT VERIFIED** | Direct GCP Project & DPA | Off by default on Vertex AI |
