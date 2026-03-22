const { addLoginIfNeeded } = require("./login");

beforeEach(function () {
  const name = Cypress.spec?.name || "";
  // API smoke: no Manager UI / login.
  if (name.includes("kong_admin_api_smoke")) return;

  addLoginIfNeeded();

  // Resolve workspace slug from Admin API for correct UI paths.
  if (name.includes("kong_service_route")) {
    const admin = Cypress.env("KONG_ADMIN_URL") || "http://localhost:8001";
    cy.request({ url: `${admin}/workspaces`, failOnStatusCode: false }).then((res) => {
      let slug = "default";
      let id = "";
      if (res.status === 200 && Array.isArray(res.body?.data) && res.body.data.length) {
        const w = res.body.data.find((x) => x.name === "default") || res.body.data[0];
        if (w?.name) slug = w.name;
        if (w?.id) id = w.id;
      }
      Cypress.env("kongWorkspaceSlug", slug);
      Cypress.env("kongWorkspaceId", id);
    });
  }
});
