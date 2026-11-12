# Crawler policy

Decide with the person which crawlers may read which paths, then state it honestly.

- **Search crawlers stay allowed.** Blocking them, or a default-deny robots.txt that
  only allows one engine, removes the site from other engines and from AI answers
  that draw on them.
- **Training versus answering.** Several AI companies publish separate user-agent
  tokens for model training and for answering or search. A site can disallow the
  training tokens and keep the answering ones. Check each company's current
  documentation for its tokens; they change. Two catches: some tokens are only
  robots.txt switches that no crawler sends (Google's AI Overviews use the normal
  search crawler, so they cannot be blocked apart from search), and fetchers that
  act on a user's request may not follow robots.txt at all.
- **robots.txt is a request,** not access control. Content that must not be copied
  needs authentication, rate limits or edge rules, and those are the person's
  decision because they can also block real search crawlers and people.
- **Verify a claimed search crawler** by reverse DNS and forward confirmation, or the
  operator's published IP ranges, before trusting its user agent.
- **Never cloak.** Crawlers and people get the same content. Do not serve fake gate
  pages, hidden instructions aimed at AI agents, or different text by user agent.
- **Never block** CSS, JavaScript or image paths the page needs to render.
- An API that public pages call while rendering must stay crawlable; block only API
  routes the public pages never use.

Report the final robots.txt and any edge rules, and which crawlers each allows.
