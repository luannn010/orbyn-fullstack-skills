# URL migration

Covers a domain change, a subdomain moved into a folder, slug clean-up on one
domain, and merging two sites. Other sites, bookmarks and old posts keep using the
former addresses long after a move, so treat the redirects as permanent.

## Mistakes that lose rankings

- **Losing pages from the map.** Build the list from every source, not just today's
  sitemap, and send each page somewhere relevant; pointing many unrelated pages at
  the home page makes search engines treat them as missing.
- **Extra hops.** Each old address goes straight to its final address; stacking a
  protocol change, a slug change and a domain change multiplies the hops.
- **Hiding the redirects.** If the old domain disallows crawling, or lapses, or the
  rules are removed later, crawlers stop learning where pages went.
- **Shipping preview settings.** A leftover `noindex` or blanket disallow on the new
  site removes it from the index at launch.

## Steps

1. **Inventory every old URL:** the sitemap, the route tree, analytics and Search
   Console exports the person provides, and old URLs that still have links.
2. **Map 1-to-1** to each page's closest equivalent. A page with no equivalent goes
   to its nearest parent topic, or returns 410 when it is truly gone.
3. **Implement in the host's own config** (framework redirects, server or edge
   rules) as 301 or 308. Avoid 302 and 307 for permanent moves.
4. **Check the map offline:**
   `python3 scripts/verify_redirects.py --map redirects.csv --old-pages old-urls.txt`
   reports duplicates, self-redirects, chains inside the map (with the direct
   target), loops and old pages with no rule.
5. **Cut over.** Everything that builds an absolute URL (canonical tags, social
   cards, structured data, locale alternates) reads the new origin, and the new
   sitemap contains new addresses only. Leaving the previous sitemap online for some
   weeks gives crawlers a list of old addresses to revisit, which is how they see the
   redirects. Help people and engines connect the two names: mention the previous
   name in the organisation's structured data and in the site's own about text. For
   a full domain change, the person also tells the search console about the move
   with its address-change tool.
6. **Check live** against the person's domain after deploy:
   `python3 scripts/verify_redirects.py --map redirects.csv --base https://old.example.com --allow-host new.example.com`.
   It follows each redirect by hand, only to the listed hosts, and fails on a 302
   or 307, more than one hop, a wrong target, a loop or a target that is not 200.
   A target on another host is checked only when that host is passed with
   `--allow-host`; otherwise the rule fails as not requested. A bare host allows
   only the scheme's default port (`host:port` for another); URLs with a user name
   or password, `file://` and other schemes are never requested. Offline, `--host
   https://example.com` treats absolute URLs on that origin as paths, so chains
   mixing both forms are found. `--slash loose`
   (default) treats `/a` and `/a/` as the same; use `strict` when the site does not.
   Exit 0 means every rule passed, 1 any failure (offline issues included), 2 bad
   input.
7. **Watch** the new property's indexed count rise as the old one falls. Moves can
   take weeks to settle; a count that does not move at all after a couple of weeks
   is worth checking for a crawl blocker.

Asking site owners to update their links is outreach: only on the person's request,
and they send it.
