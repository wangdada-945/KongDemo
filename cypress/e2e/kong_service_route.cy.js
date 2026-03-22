const {
  typeByLabel,
  clickByText,
  openNewGatewayServiceForm,
  strictServiceFormVisible,
  fillNewGatewayServiceFields,
} = require("../support/login");

// Kong Manager SPA can throw on Axios 404 during navigation; only ignore for this spec file.
Cypress.on("uncaught:exception", (err) => {
  if (!String(Cypress.spec?.name || "").includes("kong_service_route")) return true;
  const msg = String(err?.message || "");
  if (msg.includes("Request failed with status code 404")) return false;
  return true;
});

describe("Kong Manager - Service + Route creation", () => {
  const serviceName = `cypress-service-${Date.now()}`;
  const upstreamUrl = "http://example.com";
  const routePath = `/cypress-route-${Date.now()}`;

  it("creates a new Service and then creates a Route for it", () => {
    const slug = Cypress.env("kongWorkspaceSlug") || "default";
    cy.visit(`/${slug}/services`, { failOnStatusCode: false });
    cy.url().then((url) => {
      if (!url.includes("services")) {
        cy.visit("/");
        cy.get("body", { timeout: 10000 }).then(($body) => {
          const link = $body.find("a[href*='default']").first();
          if (link.length) cy.wrap(link).click({ force: true });
        });
        clickByText(
          "a, button, [role='link'], span",
          [/gateway services/i, /services/i],
          "Could not find a Services navigation entry"
        );
      }
    });

    openNewGatewayServiceForm();
    cy.get("body", { timeout: 20000 }).should(($body) => {
      expect(
        strictServiceFormVisible($body),
        "New service form should be visible"
      ).to.be.true;
    });

    fillNewGatewayServiceFields(serviceName, upstreamUrl);

    // Fail fast if Create is disabled (read-only Kong Manager without Enterprise license)
    cy.get("body").then(($b) => {
      const createBtn = $b
        .find("button, input[type='submit'], [role='button']")
        .filter((_, el) => /create|add|submit|save/i.test(el.textContent || ""))
        .get(0);
      if (createBtn && createBtn.disabled) {
        throw new Error(
          "Create button is disabled. Kong Manager may be read-only (no Enterprise license). " +
            "UI creation tests require a licensed environment—see README."
        );
      }
    });

    clickByText(
      "button, input[type='submit'], [role='button']",
      [/create/i, /add/i, /submit/i, /save/i],
      "Could not find a create/add/submit button for the service form"
    );

    cy.contains(serviceName, { timeout: 60000 }).should("exist");

    cy.contains(serviceName).click({ force: true });

    clickByText(
      "a, button",
      [/routes/i],
      "Could not find Routes section/tab"
    );
    clickByText(
      "a, button",
      [/add route/i, /new route/i, /create route/i],
      "Could not find the add/new route button"
    );

    typeByLabel(/path/i, routePath);

    clickByText(
      "button, input[type='submit'], [role='button']",
      [/create/i, /add/i, /submit/i, /save/i],
      "Could not find a create/add/submit button for the route form"
    );

    cy.contains(routePath, { timeout: 60000 }).should("exist");
  });
});
