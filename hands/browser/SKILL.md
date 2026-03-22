---
name: browser-automation
version: "1.0.0"
description: Playwright-based browser automation patterns for autonomous web interaction
author: LibreFang
tags: [browser, automation, playwright, web, scraping]
tools: [browser_navigate, browser_click, browser_type, browser_screenshot, browser_read_page, browser_close]
runtime: prompt_only
---

# Browser Automation Skill

## Playwright CSS Selector Reference

### Basic Selectors
| Selector | Description | Example |
|----------|-------------|---------|
| `#id` | By ID | `#checkout-btn` |
| `.class` | By class | `.add-to-cart` |
| `tag` | By element | `button`, `input` |
| `[attr=val]` | By attribute | `[data-testid="submit"]` |
| `tag.class` | Combined | `button.primary` |
| `parent child` | Descendant | `div.container button` |
| `parent > child` | Direct child | `ul > li` |
| `:nth-child(n)` | Nth element | `li:nth-child(2)` |
| `:first-child` | First element | `ul > li:first-child` |
| `:last-child` | Last element | `ul > li:last-child` |
| `[attr*=val]` | Attribute contains | `[class*="price"]` |
| `[attr^=val]` | Attribute starts with | `[href^="https"]` |
| `[attr$=val]` | Attribute ends with | `[href$=".pdf"]` |
| `:not(sel)` | Negation | `button:not(.disabled)` |
| `sel1, sel2` | Multiple selectors | `#submit, button[type="submit"]` |

### Form Selectors
| Selector | Use Case |
|----------|----------|
| `input[type="email"]` | Email fields |
| `input[type="password"]` | Password fields |
| `input[type="search"]` | Search boxes |
| `input[name="q"]` | Google/search query |
| `textarea` | Multi-line text areas |
| `select[name="country"]` | Dropdown menus |
| `input[type="checkbox"]` | Checkboxes |
| `input[type="radio"]` | Radio buttons |
| `button[type="submit"]` | Submit buttons |
| `input[type="file"]` | File upload fields |
| `input[type="date"]` | Date pickers |
| `input[type="tel"]` | Phone number fields |
| `input[autocomplete="cc-number"]` | Credit card fields |
| `[contenteditable="true"]` | Rich text editors |

### Navigation Selectors
| Selector | Use Case |
|----------|----------|
| `a[href*="cart"]` | Cart links |
| `a[href*="checkout"]` | Checkout links |
| `a[href*="login"]` | Login links |
| `nav a` | Navigation menu links |
| `.breadcrumb a` | Breadcrumb links |
| `[role="navigation"] a` | ARIA nav links |
| `a[href*="account"]` | Account/profile links |
| `a[href*="register"], a[href*="signup"]` | Registration links |
| `header a[href="/"]` | Logo/home link |
| `footer a` | Footer links |

### E-commerce Selectors
| Selector | Use Case |
|----------|----------|
| `.product-price`, `[data-price]` | Product prices |
| `.add-to-cart`, `#add-to-cart` | Add to cart buttons |
| `.cart-total`, `.order-total` | Cart total |
| `.quantity`, `input[name="quantity"]` | Quantity selectors |
| `.checkout-btn`, `#checkout` | Checkout buttons |
| `[data-product-id]` | Product identifiers |
| `.product-title`, `h1.product-name` | Product names |
| `.product-image img`, `[data-zoom-image]` | Product images |
| `.star-rating`, `[data-rating]` | Review ratings |
| `.in-stock`, `.availability` | Stock status |
| `select[name="size"], .size-selector` | Size selectors |
| `[data-variant], .color-swatch` | Variant selectors |

---

## Site-Specific Selector Patterns

### Google Search
| Element | Selector |
|---------|----------|
| Search input | `input[name="q"]`, `textarea[name="q"]` |
| Search button | `input[name="btnK"]`, `button[type="submit"]` |
| Result titles | `h3` (within `#search`) |
| Result links | `#search a[href^="http"]` |
| Result snippets | `.VwiC3b`, `div[data-sncf]` |
| "Next" pagination | `a#pnnext` |
| "People also ask" | `.related-question-pair` |

### Amazon
| Element | Selector |
|---------|----------|
| Search input | `#twotabsearchtextbox` |
| Search button | `#nav-search-submit-button` |
| Product titles | `h2 a.a-link-normal span` |
| Prices | `.a-price .a-offscreen`, `.a-price-whole` |
| Add to cart | `#add-to-cart-button` |
| Buy now | `#buy-now-button` |
| Quantity dropdown | `#quantity` |
| Star rating | `i.a-icon-star span` |
| Cart count | `#nav-cart-count` |

### LinkedIn
| Element | Selector |
|---------|----------|
| Username | `#username` |
| Password | `#password` |
| Sign in | `button[type="submit"]` |
| Search | `input[role="combobox"]` |
| Profile name | `.text-heading-xlarge` |
| Connection button | `button[aria-label*="Connect"]` |
| Message button | `button[aria-label*="Message"]` |

### GitHub
| Element | Selector |
|---------|----------|
| Search | `input[name="q"]` |
| Repository name | `[itemprop="name"] a` |
| Star button | `button[aria-label*="Star"]` |
| File contents | `.blob-code-inner` |
| Issue title | `#issue_title`, `.js-issue-title` |
| Submit button | `button[type="submit"]` |

Note: Site selectors change frequently. When a saved selector fails, fall back to `browser_read_page` to discover the current DOM structure, then construct a new selector from the live page.

---

## Common Workflows

### Product Search & Purchase
```
1. browser_navigate → store homepage
2. browser_type → search box with product name
3. browser_click → search button or press Enter
4. browser_read_page → scan results
5. browser_click → desired product
6. browser_read_page → verify product details & price
7. browser_click → "Add to Cart"
8. browser_navigate → cart page
9. browser_read_page → verify cart contents & total
10. STOP → Report to user, wait for approval
11. browser_click → "Proceed to Checkout" (only after approval)
```

### Account Login
```
1. browser_navigate → login page
2. browser_read_page → identify form fields and any CAPTCHA
3. browser_type → email/username field
4. browser_type → password field
5. browser_click → login/submit button
6. browser_read_page → verify successful login (check for dashboard/profile elements)
7. If MFA required → inform user, wait for code input
```

### Form Submission
```
1. browser_navigate → form page
2. browser_read_page → understand form structure
3. browser_type → fill each field sequentially
4. browser_click → checkboxes/radio buttons as needed
5. browser_screenshot → visual verification before submit
6. browser_click → submit button
7. browser_read_page → verify confirmation
```

### Price Comparison
```
1. For each store:
   a. browser_navigate → store URL
   b. browser_type → search query
   c. browser_read_page → extract prices
   d. memory_store → save price data
2. memory_recall → compare all prices
3. Report findings to user
```

### Multi-Page Data Extraction
```
1. browser_navigate → starting page
2. browser_read_page → extract data from current page
3. memory_store → save extracted data
4. Check for pagination:
   a. browser_click → "Next" button or page number link
   b. browser_read_page → verify new page loaded (check for changed content)
   c. Repeat from step 2
5. If no more pages → compile and report results
```

### Account Registration
```
1. browser_navigate → registration page
2. browser_read_page → identify required fields
3. browser_type → fill name, email, password fields sequentially
4. browser_click → accept terms checkbox (if required)
5. browser_screenshot → verify all fields before submission
6. browser_click → submit/register button
7. browser_read_page → check for:
   - Success page → registration complete
   - Email verification prompt → inform user
   - Validation errors → read errors, correct fields, retry
```

### File Download Monitoring
```
1. browser_navigate → page with download link
2. browser_read_page → identify download button/link
3. browser_click → download trigger
4. browser_read_page → check for download confirmation or redirect
5. If download requires additional steps (accept terms, choose format):
   a. browser_click → required selections
   b. browser_click → final download button
6. Report download status to user
```

---

## Wait Strategies & Timing

### When to Wait
Proper waiting prevents most automation failures. Never use fixed sleep times when a condition-based wait is possible.

| Scenario | Strategy | Notes |
|----------|----------|-------|
| Page navigation | Wait for load event | `browser_navigate` handles this automatically |
| After clicking link | Read page to confirm new content | Check for expected elements on destination |
| AJAX/dynamic content | Re-read page after delay | Some SPAs load content asynchronously |
| Form submission | Read page for confirmation | Check for success message or redirect |
| Slow networks | Retry with backoff | 3s, 6s, 12s intervals |
| Animation/transition | Brief pause before interaction | Modal fade-in, dropdown expansion |

### Detecting Page Load Completion
```
After browser_navigate or browser_click that triggers navigation:
1. browser_read_page → check if expected content is present
2. If content missing → wait 2-3 seconds → browser_read_page again
3. If still missing after 3 retries → page may have changed structure
4. Use browser_screenshot to visually confirm page state
```

### SPA (Single Page Application) Handling
SPAs like React, Angular, and Vue do not trigger traditional page loads:
```
1. browser_click → triggers route change
2. browser_read_page → may return stale content from previous view
3. Wait 1-2 seconds for client-side rendering
4. browser_read_page → should now show updated content
5. If content still stale → look for loading spinners:
   - `.loading`, `.spinner`, `[aria-busy="true"]`
   - Wait until these elements disappear
6. browser_read_page → final attempt
```

---

## Error Recovery Strategies

### Quick Reference
| Error | Recovery |
|-------|----------|
| Element not found | Try alternative selector, use visible text, scroll page |
| Page timeout | Retry navigation, check URL |
| Login required | Inform user, ask for credentials |
| CAPTCHA | Cannot solve — inform user |
| Pop-up/modal | Click dismiss/close button first |
| Cookie consent | Click "Accept" or dismiss banner |
| Rate limited | Wait 30s, retry |
| Wrong page | Use browser_read_page to verify, navigate back |

### Element Not Found Recovery
When a selector fails, follow this escalation path:
```
1. RETRY: Try the same selector once more (transient timing issue)
2. SCROLL: Scroll the page to trigger lazy loading, then retry
3. ALTERNATIVE SELECTOR: Try these fallback patterns in order:
   a. By visible text content (button text, link text)
   b. By ARIA role: [role="button"], [role="link"]
   c. By data-testid: [data-testid="..."] (if site uses them)
   d. By partial attribute match: [class*="submit"], [id*="login"]
   e. By structural position: form button:last-child
4. READ PAGE: Use browser_read_page to see current DOM structure
5. SCREENSHOT: Use browser_screenshot to visually identify the element
6. REPORT: If all fail, inform user with what was tried and the current page state
```

### Navigation Failure Recovery
```
1. Timeout on browser_navigate:
   a. Retry the same URL once
   b. If still fails, check if URL is valid (no typos, correct protocol)
   c. Try simplified URL (remove query params, try base domain)
   d. Report connectivity issue to user

2. Unexpected redirect:
   a. browser_read_page → check current URL and content
   b. If redirected to login → handle login flow
   c. If redirected to error page → report the error code and message
   d. If redirected to different page → assess if it is relevant, otherwise navigate back

3. HTTP errors observed in page content:
   - 403 Forbidden → site may be blocking automation, inform user
   - 404 Not Found → URL is stale or incorrect, search for correct URL
   - 429 Too Many Requests → wait 60 seconds, retry with longer intervals
   - 500/502/503 → server issue, retry after 30 seconds (max 3 retries)
```

### Stale Element Recovery
Elements can become stale when the page re-renders (common in SPAs):
```
1. Identify the stale interaction (click that failed after page update)
2. browser_read_page → get fresh DOM snapshot
3. Re-locate the element using the same or updated selector
4. Retry the interaction on the fresh element
5. If element has moved or changed structure, use browser_screenshot
   to visually identify its new position
```

### Pop-up and Overlay Dismissal
```
Order of priority when dealing with overlays blocking interaction:
1. Cookie consent banners:
   - Click: button containing "Accept", "Agree", "OK", "Got it"
   - Selectors: #cookie-accept, .cookie-consent button, [data-action="accept"]
   - Fallback: .cookie-banner .close, #cookie-close

2. Newsletter/subscription modals:
   - Click: close/dismiss button
   - Selectors: .modal .close, [aria-label="Close"], button.dismiss
   - Fallback: press Escape key (if supported)

3. Chat widgets:
   - Usually do not block interaction (z-index overlay)
   - If blocking, click minimize/close on the widget

4. Age verification gates:
   - Click "Yes" / "I am over 18" / "Enter"
   - May need to select a birth date from dropdowns

5. Location/notification permission prompts:
   - These are browser-level, not DOM elements
   - Usually auto-dismissed by Playwright's browser context settings
```

---

## Anti-Detection Techniques

### User Agent Strategy
Rotate user agents to appear as a normal browser. Common realistic user agents:
```
Desktop Chrome (Windows):
  Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36

Desktop Chrome (macOS):
  Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36

Desktop Firefox (Windows):
  Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0

Mobile Chrome (Android):
  Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36

Mobile Safari (iOS):
  Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1
```

### Viewport Randomization
Use realistic viewport sizes with slight variation to avoid fingerprinting:
```
Common realistic viewports:
  Desktop:  1920x1080, 1366x768, 1536x864, 1440x900, 1280x720
  Tablet:   1024x768, 768x1024 (portrait), 1280x800
  Mobile:   375x812, 390x844, 360x780, 414x896

Add random offsets (1-20px) to avoid exact-match detection:
  1920x1080 → 1923x1077 (slightly varied)
```

### Behavioral Patterns
Automation detection looks for non-human interaction patterns. Mitigate by:
```
1. TIMING: Do not click or type instantly after page load
   - Wait 1-3 seconds before first interaction
   - Insert 0.5-2 second gaps between form field entries
   - Vary timing between actions (not perfectly uniform)

2. NAVIGATION: Follow natural browsing patterns
   - Visit homepage before going directly to deep URLs
   - Click through navigation menus instead of using direct URLs when possible
   - Scroll the page before interacting with below-the-fold content

3. MOUSE/KEYBOARD: Simulate realistic input
   - Type into fields character by character (browser_type handles this)
   - Click buttons rather than submitting forms programmatically
   - Do not fill hidden honeypot fields (fields with display:none or visibility:hidden)

4. AVOID DETECTABLE PATTERNS:
   - Do not request pages faster than 1 per 3 seconds on the same domain
   - Do not access robots.txt-blocked paths
   - Do not make requests in perfectly uniform intervals
```

### Honeypot Field Detection
Some forms include invisible fields designed to catch bots:
```
Do NOT fill fields that have:
  - style="display: none"
  - style="visibility: hidden"
  - class="hidden", class="d-none", class="sr-only"
  - type="hidden" (unless it is a legitimate CSRF token or form ID)
  - Position: absolute with left: -9999px or similar off-screen placement

Use browser_read_page to inspect field visibility before filling.
```

---

## Screenshot & Content Extraction

### When to Take Screenshots
| Situation | Purpose |
|-----------|---------|
| Before form submission | Visual verification of filled data |
| After login attempt | Confirm success or capture error state |
| When element not found | See actual page state for debugging |
| Price/product comparison | Visual record for user |
| CAPTCHA encountered | Show user what needs solving |
| Before financial transaction | Proof of cart/payment details |
| Unexpected page state | Diagnose navigation or rendering issues |

### Content Extraction Patterns

**Extracting structured data from tables:**
```
1. browser_read_page → get full page text
2. Identify table boundaries in the text output
3. Parse rows and columns from the structured text
4. memory_store → save as structured data for comparison
```

**Extracting specific data points:**
```
1. browser_read_page → get page content
2. Search output for relevant labels/headings:
   - "Price:", "Total:", "Subtotal:" → monetary values
   - "In Stock", "Available", "Sold Out" → availability
   - "Rating:", stars → review scores
   - "SKU:", "Item #:" → product identifiers
3. Extract the value adjacent to each label
```

**Handling dynamically loaded content:**
```
1. browser_read_page → check if content placeholder exists
2. If content shows "Loading..." or skeleton elements:
   a. Wait 2-3 seconds
   b. browser_read_page → retry
3. If content requires scroll-to-load (infinite scroll):
   a. Extract visible data
   b. Scroll down (click a lower element or use page navigation)
   c. browser_read_page → extract newly loaded data
   d. Repeat until desired amount collected or no new content appears
```

---

## Form Filling & Interaction Sequences

### Dropdown / Select Menus
```
Standard HTML <select>:
  browser_click → the <select> element to open it
  browser_click → the <option> with desired value

Custom dropdown (div-based):
  1. browser_click → the dropdown trigger element (.dropdown-toggle, .select-wrapper)
  2. browser_read_page → find the dropdown options that appeared
  3. browser_click → the desired option from the expanded list
```

### Date Pickers
```
Native HTML date input (input[type="date"]):
  browser_type → the date value in YYYY-MM-DD format directly into the input

Custom calendar widget:
  1. browser_click → date input to open calendar
  2. browser_click → month/year navigation arrows to reach target month
  3. browser_click → the target day cell
  4. browser_read_page → verify selected date
```

### File Uploads
```
Standard file input (input[type="file"]):
  - Playwright can set file input values directly
  - Not always available via browser_type — inform user if upload needed

Drag-and-drop upload zones:
  - Usually have a fallback "Browse files" button/link
  - browser_click → "Browse" or "Choose file" fallback button
```

### Multi-Step Forms (Wizards)
```
1. browser_read_page → identify current step and total steps
2. Fill current step fields with browser_type and browser_click
3. browser_click → "Next" / "Continue" button
4. browser_read_page → verify progression to next step
5. If validation error appears:
   a. browser_read_page → identify error messages
   b. Fix the flagged fields
   c. browser_click → "Next" again
6. Repeat until final step
7. browser_screenshot → capture summary/review page
8. STOP → get user approval before final submission
```

### Autocomplete / Typeahead Fields
```
1. browser_type → partial text into the input field
2. Wait 1-2 seconds for suggestion dropdown to appear
3. browser_read_page → check if suggestions loaded
4. browser_click → the desired suggestion from the dropdown
5. browser_read_page → verify the field populated correctly
```

### Checkbox and Radio Button Groups
```
Checkboxes (multi-select):
  browser_click → each desired checkbox
  Use browser_read_page to check current state ([checked] attribute)
  Do NOT click already-checked boxes unless intending to uncheck

Radio buttons (single-select):
  browser_click → the desired option
  Only one can be active — clicking a new one deselects the previous
```

---

## Multi-Tab and Popup Handling

### Links That Open New Tabs
```
When browser_click opens a new tab (target="_blank" links):
1. The new tab becomes the active context
2. browser_read_page → verify content in new tab
3. Complete actions in the new tab
4. browser_close → close the new tab to return to the original
5. browser_read_page → verify original tab is still in expected state
```

### Authentication Popups (OAuth, SSO)
```
OAuth/Social login flows often open a popup:
1. browser_click → "Sign in with Google/GitHub/etc."
2. New popup/tab opens with the provider's login page
3. browser_type → credentials in the popup
4. browser_click → authorize/allow button
5. Popup closes automatically, original page refreshes
6. browser_read_page → verify login success on original page
```

### Multiple Window Coordination
```
When workflow requires information from multiple pages:
1. Open first page → extract needed data → memory_store
2. browser_navigate → second page (replaces current)
3. Extract data from second page → memory_store
4. Use memory_recall to combine data from both sources
5. browser_navigate → return to original page if needed

Avoid keeping multiple tabs open simultaneously when possible —
single-tab workflows are more reliable and predictable.
```

---

## Cookie and Session Management

### Session Persistence
```
Playwright browser sessions persist cookies within a single session:
- Logging in once is enough for subsequent navigations to the same site
- Cookies expire when the browser context is closed (browser_close)
- For long workflows, periodically verify session is still active:
  1. browser_navigate → a page that requires authentication
  2. browser_read_page → check for login page redirect
  3. If redirected to login → session expired, re-authenticate
```

### Cookie Consent Handling
```
Most sites display cookie banners on first visit. Handle immediately:
1. browser_read_page → check for cookie banner presence
2. Look for accept buttons with these common selectors:
   - #cookie-accept, #accept-cookies, #onetrust-accept-btn-handler
   - button[data-action="accept"], .cookie-consent .accept
   - Text content: "Accept All", "Accept Cookies", "I Agree", "OK"
3. browser_click → the accept button
4. browser_read_page → verify banner dismissed
5. If banner persists → try clicking the close/X button instead
```

### Geo-Restricted Content
```
When content varies by location:
1. browser_read_page → check for location selection prompts
2. If location selector present:
   a. browser_click → country/region dropdown
   b. browser_click → desired country/region
   c. browser_read_page → verify content updated for selected region
3. Some sites redirect to country-specific domains (.co.uk, .de, etc.)
   - Navigate directly to the correct country domain
```

---

## Performance Optimization

### Minimizing Page Reads
```
browser_read_page is the most expensive operation (returns full page text).
Optimize by:
1. Use browser_read_page once after navigation, extract ALL needed data
2. Use browser_screenshot for quick visual checks instead of full reads
3. After clicking a button, only read the page if you need to verify
   the result or extract new data
4. Cache page content in memory_store if you will reference it later
```

### Efficient Navigation
```
1. Use direct URLs when possible instead of click-through navigation:
   BAD:  homepage → click "Products" → click "Electronics" → click "Phones"
   GOOD: browser_navigate → /products/electronics/phones

2. Use URL patterns for pagination:
   If page 1 is /results?page=1, go directly to /results?page=5
   instead of clicking "Next" five times

3. Combine operations:
   Instead of: navigate → read → navigate → read → navigate → read
   Use: navigate → read + extract all → navigate next → read + extract all
```

### Handling Lazy-Loaded Content
```
Many modern sites load content as the user scrolls (infinite scroll):
1. browser_read_page → get initially loaded content
2. If you need more items:
   a. browser_click → a far-down element to trigger scroll loading
   b. Wait 2-3 seconds for new content to render
   c. browser_read_page → extract newly loaded content
   d. Repeat until sufficient data collected
3. Set a maximum iteration count (e.g., 10 scroll cycles)
   to prevent infinite loops on endlessly scrolling pages
```

### Rate Limiting Awareness
```
Respect site rate limits to avoid IP blocks:
- Space requests to same domain by at least 2-3 seconds
- If you receive a 429 error or see "Too many requests":
  1. Wait 30-60 seconds before next request
  2. Double the wait time on each subsequent 429
  3. After 3 consecutive 429s, inform user and stop
- Watch for soft rate limiting signals:
  - CAPTCHA appearing mid-session
  - Results becoming empty or different
  - Redirect to a "verify you are human" page
```

---

## Common Failure Modes & Debugging

### Diagnosis Checklist
When an interaction fails, check in this order:
```
1. CORRECT PAGE?
   browser_read_page → confirm you are on the expected URL/page

2. ELEMENT EXISTS?
   browser_read_page → search output for the target element's text or nearby text

3. ELEMENT VISIBLE?
   browser_screenshot → check if element is visible (not behind overlay, not off-screen)

4. ELEMENT BLOCKED?
   Look for cookie banners, modals, chat widgets covering the element

5. ELEMENT INTERACTIVE?
   Check if element is disabled, greyed out, or read-only

6. PAGE FULLY LOADED?
   Look for loading indicators in page content (spinner text, "Loading...")

7. SESSION VALID?
   Check if you have been redirected to a login page
```

### Common Failure Patterns

**Clicking does nothing:**
```
Causes:
  - Element is covered by an overlay (cookie banner, modal)
  - Element is outside the viewport (needs scroll)
  - Element is disabled or has pointer-events: none
  - JavaScript click handler has not attached yet (page still loading)
  - Clicking on a wrapper div instead of the actual button

Fixes:
  1. Dismiss any overlays first
  2. Scroll to the element before clicking
  3. Wait 2 seconds and retry
  4. Try a more specific selector targeting the inner clickable element
```

**Form submission fails silently:**
```
Causes:
  - Required field left empty (client-side validation blocked submit)
  - Hidden honeypot field was filled (bot detection)
  - CSRF token expired (session timeout)
  - JavaScript form validation prevents submission

Fixes:
  1. browser_read_page → check for inline validation error messages
  2. browser_screenshot → look for highlighted required fields
  3. Verify all required fields are filled (check for asterisks or "required" labels)
  4. Try refreshing the page and filling the form again (new CSRF token)
```

**Page content appears empty or minimal:**
```
Causes:
  - Site requires JavaScript rendering (content injected by React/Vue/Angular)
  - Content is behind an authentication wall
  - Site is geo-blocked or IP-blocked
  - Content loads via AJAX after initial page load

Fixes:
  1. Wait 3-5 seconds after navigation, then browser_read_page
  2. browser_screenshot → check if content is visually present but not in text
  3. Check if login is required
  4. Try a different URL or approach
```

**Redirect loop or unexpected page:**
```
Causes:
  - Session expired → site redirects to login → tries to redirect back → loop
  - Geo-redirect based on IP location
  - A/B testing serves different page version
  - Site requires cookie acceptance before showing content

Fixes:
  1. browser_read_page → check current URL
  2. Handle cookie consent if prompted
  3. Re-authenticate if on login page
  4. Try navigating to the base domain first, then to the target page
```

---

## Security Checklist

### Before Entering Credentials
- Verify the domain matches the expected site (check for typosquatting)
- Confirm the page is served over HTTPS
- Look for suspicious elements (extra fields, unusual layout)
- Never enter credentials on HTTP pages
- Warn user about any certificate warnings or security indicators

### During Sensitive Operations
- Never store passwords in memory_store — use them only in browser_type
- Never auto-approve financial transactions — always STOP and confirm with user
- Report any unexpected redirects during authentication
- Log out of sessions when workflow is complete

### Phishing Indicators to Watch For
| Indicator | Example | Action |
|-----------|---------|--------|
| Misspelled domain | amaz0n.com, gooogle.com | STOP and warn user |
| Unusual TLD | amazon.xyz, paypal.ru | STOP and warn user |
| HTTP on login page | http://bank.com/login | STOP and warn user |
| Extra form fields | SSN on a retail login | STOP and warn user |
| Suspicious redirects | Login redirects to different domain | STOP and warn user |
| Urgency language | "Account suspended, act now" | Inform user, suggest verifying |

### Data Handling Rules
```
SAFE to store in memory_store:
  - Product names, prices, descriptions
  - Public profile information
  - Search results and comparisons
  - Order confirmation numbers
  - Non-sensitive form field values

NEVER store in memory_store:
  - Passwords, PINs, security codes
  - Credit card numbers or CVVs
  - Social Security or government ID numbers
  - Authentication tokens or session cookies
  - Private messages or confidential communications
```
