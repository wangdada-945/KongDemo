function elementMatchText(el, regexList) {
  const txt = (el.textContent || "").replace(/\s+/g, " ").trim();
  const aria = (el.getAttribute("aria-label") || "").trim();
  const title = (el.getAttribute("title") || "").trim();
  const combined = `${txt} ${aria} ${title}`;
  return regexList.some((rx) => rx.test(txt) || rx.test(aria) || rx.test(title) || rx.test(combined));
}

function findFirstTextMatch($root, selectors, regexList) {
  const elements = $root.find(selectors).toArray();
  for (const el of elements) {
    if (elementMatchText(el, regexList)) return el;
  }
  return null;
}

function typeByLabel(labelRegex, value) {
  cy.get("body").then(($body) => {
    const labelEls = $body.find("label").toArray();
    const label = labelEls.find((l) => labelRegex.test((l.textContent || "").trim()));
    if (!label) throw new Error(`Could not find label matching: ${labelRegex}`);

    const $field = firstTypableInput(Cypress.$(label).closest("div, fieldset, label"));

    if (!$field || $field.length === 0) {
      throw new Error(`No input found near label: ${labelRegex}`);
    }

    safeClearType($field, value);
  });
}

function clickByText(selectors, regexList, errorMessage) {
  cy.get("body").then(($body) => {
    const el = findFirstTextMatch($body, selectors, regexList);
    if (!el) throw new Error(errorMessage);
    cy.wrap(el).click({ force: true });
  });
}

function addLoginIfNeeded() {
  const username = Cypress.env("KONG_USERNAME");
  const password = Cypress.env("KONG_PASSWORD");

  cy.visit("/", { failOnStatusCode: false });

  cy.get("body", { timeout: 60000 }).then(($body) => {
    const hasPassword = $body.find("input[type='password']").length > 0;
    if (!hasPassword) return;

    if (!username || !password) {
      throw new Error(
        "Missing Kong Manager credentials. Please set CYPRESS_KONG_USERNAME and CYPRESS_KONG_PASSWORD."
      );
    }

    const $usernameField = $body
      .find(
        "input[name='username'], input[autocomplete='username'], input[type='text'], input[type='email']"
      )
      .first();

    if (!$usernameField || $usernameField.length === 0) {
      throw new Error("Login form detected but username input not found.");
    }

    cy.wrap($usernameField).clear({ force: true }).type(username, { force: true });
    cy.get("input[type='password']").clear({ force: true }).type(password, { log: false, force: true });

    clickByText(
      "button, input[type='submit']",
      [/sign in/i, /log in/i, /login/i, /submit/i],
      "Could not find a login/submit button"
    );
  });

  cy.url({ timeout: 60000 }).should("match", /workspaces|\/$|kong-manager/i);
}

/**
 * True only when the create-service form is likely shown (not the list page).
 */
function strictServiceFormVisible($body) {
  if ($body.find("form").length > 0) return true;
  if ($body.find('input[name="name"], input#name').length > 0) return true;
  const upstreamHints = $body.find(
    'input[name="url"], input[name="protocol"], input[name="host"], input[name="path"], input[placeholder*="url"], input[placeholder*="URL"], input[placeholder*="kong-air"]'
  ).length;
  const textInputs = $body.find('input[type="text"], input:not([type])').length;
  if (upstreamHints > 0 && textInputs >= 2) return true;
  const generic = $body.find("input:visible").filter((_, el) => {
    const t = String(el.type || "").toLowerCase();
    return t === "" || t === "text" || t === "url" || t === "search";
  }).length;
  if (generic >= 2) return true;
  if (/new gateway service/i.test($body.text()) && generic >= 1) return true;
  return false;
}

function isTypableInput(el) {
  if (!el || !el.tagName) return false;
  const tag = el.tagName.toLowerCase();
  if (tag === "textarea") return true;
  if (tag !== "input") return false;
  const tid = (el.getAttribute("data-testid") || "").toLowerCase();
  if (tid.includes("radio")) return false;
  const t = String(el.type || "").toLowerCase();
  if (["radio", "checkbox", "hidden", "submit", "button", "file", "range", "color"].includes(t)) {
    return false;
  }
  return true;
}

function firstTypableFromCollection($col) {
  if (!$col || !$col.length) return Cypress.$();
  const el = $col.toArray().find(isTypableInput);
  return el ? Cypress.$(el) : Cypress.$();
}

function firstTypableInput($ctx) {
  if (!$ctx || !$ctx.length) return Cypress.$();
  return firstTypableFromCollection($ctx.find("input, textarea"));
}

function safeClearType($jq, text) {
  cy.wrap($jq).then(($w) => {
    const el = $w && $w[0];
    if (!el || !isTypableInput(el)) {
      const tid = el && el.getAttribute ? el.getAttribute("data-testid") : "";
      const ty = el && "type" in el ? el.type : "";
      throw new Error(
        `safeClearType: expected typable field, got <${el && el.tagName}> type="${ty}" data-testid="${tid}"`
      );
    }
  });
  cy.wrap($jq).clear({ force: true }).type(text, { force: true });
}

function findInputForLabel($root, labelEl) {
  const $lab = Cypress.$(labelEl);
  let $in = firstTypableInput($lab.closest("div, fieldset"));
  if ($in.length) return $in;

  const forId = labelEl.getAttribute && labelEl.getAttribute("for");
  const doc = $root[0] && $root[0].ownerDocument;
  if (forId && doc && doc.getElementById) {
    const byId = doc.getElementById(forId);
    if (byId && /^(INPUT|TEXTAREA)$/i.test(byId.tagName)) {
      const t = String(byId.type || "").toLowerCase();
      if (t !== "radio" && t !== "checkbox") {
        return Cypress.$(byId);
      }
    }
  }

  $in = firstTypableInput($lab.parent());
  if ($in.length) return $in;

  $in = firstTypableInput($lab.closest("section, form, main, [role='dialog'], [role='main']"));
  if ($in.length) return $in;

  $in = firstTypableFromCollection(
    $lab.parent().find('input[type="text"], input[type="url"], input[type="search"], textarea')
  );
  if ($in.length) return $in;

  return Cypress.$();
}

function fillNewGatewayServiceFields(serviceName, upstreamUrl) {
  cy.get("body", { timeout: 15000 }).then(($b) => {
    const $adv = $b.find("a, button").filter((i, el) =>
      /view advanced fields/i.test(el.textContent || "")
    );
    if ($adv.length) cy.wrap($adv.first()).click({ force: true });
  });

  cy.wait(300);

  cy.get("body", { timeout: 10000 }).then(($b) => {
    const labels = $b.find("label").toArray();
    const textOf = (l) => (l.textContent || "").replace(/\s+/g, " ").trim();
    const lab =
      labels.find((l) => /service name/i.test(textOf(l))) ||
      labels.find((l) => /^name$/i.test(textOf(l))) ||
      labels.find((l) => /gateway service name/i.test(textOf(l)));
    if (lab) {
      const $in = findInputForLabel($b, lab);
      if ($in.length) safeClearType($in, serviceName);
      return;
    }
    const $byName = firstTypableFromCollection($b.find('input[name="name"], input#name'));
    if ($byName.length) safeClearType($byName, serviceName);
  });

  cy.get("body", { timeout: 15000 }).then(($b) => {
    const labels = $b.find("label").toArray();
    const textOf = (l) => (l.textContent || "").replace(/\s+/g, " ").trim();
    const lab =
      labels.find((l) => /full url/i.test(textOf(l))) ||
      labels.find((l) => /^url$/i.test(textOf(l)));

    let $in = Cypress.$();
    if (lab) {
      $in = findInputForLabel($b, lab);
    }
    if (!$in.length) {
      $in = firstTypableFromCollection(
        $b.find(
          'input[placeholder*="kong-air"], input[placeholder*="https"], input[placeholder*="api."]'
        )
      );
    }
    if (!$in.length) {
      $in = firstTypableFromCollection($b.find('input[type="url"]'));
    }
    if (!$in.length) {
      $in = firstTypableFromCollection(
        $b.find("input:visible").filter((_, el) => {
          const ph = (el.getAttribute("placeholder") || "").toLowerCase();
          const t = String(el.type || "").toLowerCase();
          if (t === "hidden" || t === "password") return false;
          if (/retry/i.test(ph)) return false;
          return ph.includes("http") || ph.includes("url") || t === "url" || t === "text" || !t;
        })
      );
    }
    if (!$in.length) {
      throw new Error(
        "Could not find Full URL input (label + placeholder fallbacks failed)"
      );
    }
    safeClearType($in, upstreamUrl);
  });
}

function dismissKongOverlays() {
  cy.get("body", { timeout: 5000 }).then(($b) => {
    const el = findFirstTextMatch(
      $b,
      "button, [role='button'], a",
      [/dismiss/i, /close/i, /^ok$/i, /got it/i, /understood/i, /continue/i, /accept/i]
    );
    if (el) cy.wrap(el).click({ force: true });
  });
}

/**
 * Open "new service" screen: try common Kong Manager URLs, then list page + href/text.
 */
function openNewGatewayServiceForm() {
  const slug = Cypress.env("kongWorkspaceSlug") || "default";
  const wsId = Cypress.env("kongWorkspaceId") || "";

  const queueTryPrefix = (prefix) => {
    if (!prefix) return;
    cy.visit(`/${prefix}/services/create`, { failOnStatusCode: false });
    cy.get("body", { timeout: 12000 }).then(($body) => {
      if (!strictServiceFormVisible($body)) {
        cy.visit(`/${prefix}/services/new`, { failOnStatusCode: false });
      }
    });
    cy.get("body", { timeout: 12000 }).then(($body) => {
      if (!strictServiceFormVisible($body)) {
        cy.visit(`/${prefix}/gateway/services/create`, { failOnStatusCode: false });
      }
    });
    cy.get("body", { timeout: 12000 }).then(($body) => {
      if (!strictServiceFormVisible($body)) {
        cy.visit(`/${prefix}/gateway/services/new`, { failOnStatusCode: false });
      }
    });
    cy.get("body", { timeout: 12000 }).then(($body) => {
      if (!strictServiceFormVisible($body)) {
        cy.visit(`/${prefix}/gateway-services/new`, { failOnStatusCode: false });
      }
    });
    cy.get("body", { timeout: 12000 }).then(($body) => {
      if (!strictServiceFormVisible($body)) {
        cy.visit(`/${prefix}/core-entities/services/new`, { failOnStatusCode: false });
      }
    });
  };

  queueTryPrefix(slug);
  if (wsId && wsId !== slug) queueTryPrefix(wsId);

  cy.get("body", { timeout: 12000 }).then(($body) => {
    if (strictServiceFormVisible($body)) return;

    cy.visit(`/${slug}/services`, { failOnStatusCode: false });
    cy.get("body", { timeout: 20000 }).then(() => {
      dismissKongOverlays();
    });
    cy.wait(800);

    cy.get("body", { timeout: 20000 }).then(($b) => {
      const $byHref = $b.find("a[href]").filter((i, el) => {
        const h = (el.getAttribute("href") || "").toLowerCase();
        if (h.includes("logout") || h.includes("sign-out")) return false;
        if (
          /\/new\/?(\?|$|#)/.test(h) ||
          h.endsWith("/new") ||
          /\/create\/?(\?|$|#)/.test(h) ||
          h.endsWith("/create")
        )
          return true;
        return (
          h.includes("service") &&
          (h.includes("new") || h.includes("create") || /\/new\/?$/.test(h))
        );
      });
      if ($byHref.length) {
        cy.wrap($byHref.first()).click({ force: true });
        return;
      }
      clickByText(
        "a, button, [role='button']",
        [/new gateway service/i, /add gateway service/i, /create gateway service/i],
        "Could not find a control to open the new Gateway Service form"
      );
    });
  });
}

module.exports = {
  typeByLabel,
  clickByText,
  addLoginIfNeeded,
  strictServiceFormVisible,
  openNewGatewayServiceForm,
  fillNewGatewayServiceFields,
};
