# Provider policies (M6A.7)

Checked: 20 November 2026, by web search of official provider pages.
Method: excerpts from the official pages, read in search results. Before any client-facing claim, open each link and confirm the quoted wording.

## Summary

| Provider | Consumer account (ChatGPT, Claude, Gemini app) | API key | Result to use in proposals |
|---|---|---|---|
| OpenAI | Possible only through "Sign in with ChatGPT", with conditions (below) | Yes | CONDITIONAL. Do not promise until eligibility is confirmed with OpenAI. Until then, the client uses their own OpenAI API key. |
| Anthropic | Not permitted for third-party apps | Yes | CLIENT'S OWN API KEY ONLY |
| Google | Not offered. Gemini API is for developers, not consumer use | Yes | CLIENT'S OWN API KEY ONLY |

## OpenAI

- Link: https://openai.com/policies/sign-in-with-chatgpt-terms/ (terms dated 29 September 2026)
- Other links read: https://openai.com/policies/business-terms , https://openai.com/policies/service-terms/
- What the page says (excerpt): an app may use "Sign in with ChatGPT" to connect a user's ChatGPT plan, only through OpenAI's supported sign-in flow, only for the application the user connected, and only as the user authorises. Tokens must be stored locally under the user's control. Pooling, reselling, or sharing plan usage between users is prohibited. The app must not ask users for their passwords or session cookies.
- Result: CONDITIONAL. The terms allow this route for an app. Whether our app qualifies, and whether approval is needed, is not stated in the excerpt. Verify before offering it.
- Practical decision for now: the client uses their own OpenAI API key. We do not supply or pay for any key.

## Anthropic

- Link: https://www.anthropic.com/legal/consumer-terms (consumer terms, Claude.ai and Claude Pro)
- Link: https://www.anthropic.com/legal/commercial-terms (API keys and business use)
- What the page says (excerpt): users may not share their Account login information, Anthropic API key, or Account credentials with anyone else. Automated access to the Services is not allowed except through an Anthropic API key or where Anthropic explicitly permits it.
- Result: CLIENT'S OWN API KEY ONLY. Consumer Claude accounts cannot be connected to a third-party app. We do not supply or pay for any key.

## Google

- Link: https://ai.google.dev/gemini-api/terms (Gemini API Additional Terms)
- What the page says (excerpt): use of Google AI Studio and the Gemini API is for developers building for professional or business purposes, not for consumer use.
- Result: CLIENT'S OWN API KEY ONLY. There is no consumer Gemini account connection for third-party apps. We do not supply or pay for any key.
- Data warning, important for our tests: on the free (unpaid) tier, Google uses submitted content to improve its products, and human reviewers may read it. Use only fictional documents on the free tier. On the paid tier, Google says it does not use prompts to improve its products, but it logs them for a limited time to detect policy violations.

## Decisions this record supports

1. Proposals offer two options: (a) local Ollama on the client's computer, free and private; (b) the client's own API key from any provider they choose, paid or free-tier. We never supply or pay for a key.
2. Free-tier API keys are allowed. They are the client's choice. The app does not block them. Before a free-tier key is used, the app shows a warning: free-tier providers may use submitted content to improve their products and human reviewers may read it, so the client should use fictional or non-sensitive text on the free tier.
3. What is NOT offered: connecting a consumer ChatGPT, Claude, or Gemini login to the app. This is a different route from an API key and is blocked by Anthropic and Google's terms (OpenAI's route is unconfirmed).
4. OpenAI "Sign in with ChatGPT" stays under review until eligibility is checked.
5. Before launch, open each link above and confirm the wording. Record the date you confirm it.

## Founder confirmation

- Confirmed by founder (name, date): ______________________
